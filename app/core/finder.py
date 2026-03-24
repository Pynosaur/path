from pathlib import Path
import time


def parse_size(size_str):
    multipliers = {
        "B": 1,
        "K": 1024,
        "M": 1024 ** 2,
        "G": 1024 ** 3,
    }
    direction = None
    if size_str.startswith("+"):
        direction = "gt"
        size_str = size_str[1:]
    elif size_str.startswith("-"):
        direction = "lt"
        size_str = size_str[1:]
    else:
        direction = "gt"

    suffix = size_str[-1].upper()
    if suffix in multipliers:
        value = float(size_str[:-1]) * multipliers[suffix]
    else:
        value = float(size_str)

    return direction, int(value)


def format_size(size_bytes):
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):.1f}G"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):.1f}M"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f}K"
    return f"{size_bytes}B"


def get_depth(entry_path, root_path):
    return len(entry_path.relative_to(root_path).parts)


def matches_filters(entry, opts):
    if opts.get("files_only") and not entry.is_file():
        return False
    if opts.get("dirs_only") and not entry.is_dir():
        return False

    if (
        not opts.get("hidden") and
        any(p.startswith(".") for p in entry.relative_to(opts["root"]).parts)
    ):
        return False

    name = entry.name

    if opts.get("pattern"):
        if not entry.match(opts["pattern"]):
            return False

    if opts.get("ext"):
        if entry.is_file() and entry.suffix.lstrip(".").lower() != opts["ext"].lower():
            return False
        if entry.is_dir():
            return False

    if opts.get("name"):
        if opts["name"].lower() not in name.lower():
            return False

    if opts.get("size") and entry.is_file():
        try:
            file_size = entry.stat().st_size
            direction, threshold = parse_size(opts["size"])
            if direction == "gt" and file_size <= threshold:
                return False
            if direction == "lt" and file_size >= threshold:
                return False
        except OSError:
            return False

    if opts.get("modified") is not None and entry.is_file():
        try:
            mtime = entry.stat().st_mtime
            days_ago = (time.time() - mtime) / 86400
            if days_ago > opts["modified"]:
                return False
        except OSError:
            return False

    return True


def walk(root, max_depth=None, hidden=False):
    root = Path(root).resolve()
    if not root.exists():
        return
    if not root.is_dir():
        yield root, 0
        return

    try:
        for entry in sorted(
            root.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower()),
        ):
            depth = 1
            if not hidden and entry.name.startswith("."):
                continue
            yield entry, depth
            if entry.is_dir() and (max_depth is None or depth < max_depth):
                yield from _walk_recursive(entry, root, depth, max_depth, hidden)
    except PermissionError:
        return


def _walk_recursive(directory, root, current_depth, max_depth, hidden):
    try:
        for entry in sorted(
            directory.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower()),
        ):
            depth = current_depth + 1
            if not hidden and entry.name.startswith("."):
                continue
            yield entry, depth
            if entry.is_dir() and (max_depth is None or depth < max_depth):
                yield from _walk_recursive(entry, root, depth, max_depth, hidden)
    except PermissionError:
        return


def find(root, opts):
    root = Path(root).resolve()
    if not root.exists():
        print(f"path: '{root}' does not exist")
        return []

    if not root.is_dir():
        print(f"path: '{root}' is not a directory")
        return []

    opts["root"] = root
    max_depth = opts.get("layers")
    hidden = opts.get("hidden", False)
    results = []

    for entry, depth in walk(root, max_depth, hidden):
        if matches_filters(entry, opts):
            results.append((entry, depth))

    return results


def build_tree(results, root, use_abs=False):
    lines = []
    root = Path(root).resolve()
    lines.append(f"\033[1;34m{root.name}/\033[0m")

    depth_last = {}
    grouped = []
    for entry, depth in results:
        grouped.append((entry, depth))

    for i, (entry, depth) in enumerate(grouped):
        is_last = True
        for j in range(i + 1, len(grouped)):
            if grouped[j][1] <= depth:
                if grouped[j][1] == depth:
                    is_last = False
                break

        depth_last[depth] = is_last

        prefix_parts = []
        for d in range(1, depth):
            parent_is_last = depth_last.get(d, False)
            prefix_parts.append("    " if parent_is_last else "\033[90m│\033[0m   ")

        connector = "\033[90m└── \033[0m" if is_last else "\033[90m├── \033[0m"
        prefix = "".join(prefix_parts) + connector

        if use_abs:
            display = str(entry)
        else:
            display = entry.name

        if entry.is_dir():
            display = f"\033[1;34m{display}/\033[0m"
        elif entry.is_symlink():
            display = f"\033[1;36m{display}\033[0m"
        elif entry.stat().st_mode & 0o111:
            display = f"\033[1;32m{display}\033[0m"

        lines.append(prefix + display)

    return "\n".join(lines)


def format_results(results, root, opts):
    if opts.get("count"):
        file_count = sum(1 for e, _ in results if e.is_file())
        dir_count = sum(1 for e, _ in results if e.is_dir())
        parts = []
        if not opts.get("dirs_only"):
            parts.append(f"{file_count} file{'s' if file_count != 1 else ''}")
        if not opts.get("files_only"):
            parts.append(f"{dir_count} dir{'s' if dir_count != 1 else ''}")
        return ", ".join(parts)

    if opts.get("tree"):
        return build_tree(results, root, opts.get("abs", False))

    lines = []
    root = Path(root).resolve()
    for entry, depth in results:
        if opts.get("abs"):
            display = str(entry)
        else:
            try:
                display = str(entry.relative_to(root))
            except ValueError:
                display = str(entry)

        if entry.is_dir():
            display = f"\033[1;34m{display}/\033[0m"
        elif entry.is_symlink():
            display = f"\033[1;36m{display}\033[0m"

        if opts.get("long"):
            try:
                stat = entry.stat()
                size = format_size(stat.st_size) if entry.is_file() else "-"
                lines.append(f"  {size:>6}  {display}")
            except OSError:
                lines.append(f"  {'?':>6}  {display}")
        else:
            lines.append(f"  {display}")

    return "\n".join(lines)
