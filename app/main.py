import argparse
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app.core.finder import find, format_results
from app.utils.doc_reader import read_app_doc


def build_parser():
    doc = read_app_doc("path")
    parser = argparse.ArgumentParser(
        prog="path",
        description=doc.get("description", "Pure Python file and directory finder"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  path                        list everything in current dir\n"
            "  path . -f                   files only\n"
            "  path . -d                   dirs only\n"
            "  path . -f -p '*.py'         python files by glob\n"
            "  path . -f -e py             python files by extension\n"
            "  path . -l 2                 max 2 layers deep\n"
            "  path /usr -d -n bin         dirs containing 'bin' under /usr\n"
            "  path . -f -s +1M            files larger than 1MB\n"
            "  path . -f -m 7              files modified in last 7 days\n"
            "  path . --tree -l 3          tree view, 3 layers\n"
            "  path . -f -L                list with sizes\n"
        ),
    )

    parser.add_argument(
        'root',
        nargs='?',
        default='.',
        help='starting directory (default: .)',
    )
    parser.add_argument("-f", "--files", action="store_true", help="find files only")
    parser.add_argument(
        '-d',
        '--dirs',
        action='store_true',
        help='find directories only',
    )
    parser.add_argument("-p", "--pattern", help="glob pattern (e.g. '*.py', 'test_*')")
    parser.add_argument("-e", "--ext", help="filter by extension (e.g. py, txt)")
    parser.add_argument("-n", "--name", help="name contains string")
    parser.add_argument("-l", "--layers", type=int, help="max depth (0 = root only)")
    parser.add_argument("-s", "--size", help="filter by size (+1M, -100K)")
    parser.add_argument("-m", "--modified", type=int, help="modified within N days")
    parser.add_argument(
        '--hidden',
        action='store_true',
        help='include hidden files/dirs',
    )
    parser.add_argument("--count", action="store_true", help="show count only")
    parser.add_argument("--abs", action="store_true", help="show absolute paths")
    parser.add_argument("--tree", action="store_true", help="tree view output")
    parser.add_argument("-L", "--long", action="store_true", help="show file sizes")
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f"path {doc.get('version', '0.1.0')}",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"path: '{args.root}' does not exist")
        sys.exit(1)
    if not root.is_dir():
        print(f"path: '{args.root}' is not a directory")
        sys.exit(1)

    opts = {
        "files_only": args.files,
        "dirs_only": args.dirs,
        "pattern": args.pattern,
        "ext": args.ext,
        "name": args.name,
        "layers": args.layers,
        "size": args.size,
        "modified": args.modified,
        "hidden": args.hidden,
        "count": args.count,
        "abs": args.abs,
        "tree": args.tree,
        "long": args.long,
    }

    results = find(root, opts)

    if not results and not args.count:
        print("path: no matches found")
        sys.exit(0)

    output = format_results(results, root, opts)
    if output:
        print(output)


if __name__ == "__main__":
    main()
