# path

A pure Python file and directory finder powered by `pathlib`. Part of the [Pynosaur](https://pynosaur.org) ecosystem.

More sophisticated than `find`, with layers (depth control), pattern matching, size filtering, and tree view — all in a clean, intuitive interface.

## Install

```bash
pget install pynosaur/path
```

## Usage

```
path [ROOT] [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `-f, --files` | Find files only |
| `-d, --dirs` | Find directories only |
| `-p, --pattern PAT` | Glob pattern (`*.py`, `test_*`) |
| `-e, --ext EXT` | Filter by extension (`py`, `txt`) |
| `-n, --name NAME` | Name contains string |
| `-l, --layers N` | Max depth (0 = root only) |
| `-s, --size SIZE` | Filter by size (`+1M`, `-100K`) |
| `-m, --modified DAYS` | Modified within N days |
| `--hidden` | Include hidden files/dirs |
| `--count` | Show count only |
| `--abs` | Show absolute paths |
| `--tree` | Tree view output |
| `-L, --long` | Show file sizes |

## Examples

List everything in the current directory:
```bash
path
```

Find only files:
```bash
path . -f
```

Find only directories:
```bash
path . -d
```

Find Python files by glob pattern:
```bash
path . -f -p '*.py'
```

Find Python files by extension:
```bash
path . -f -e py
```

Limit search to 2 layers deep:
```bash
path . -l 2
```

Find directories named "bin" under /usr:
```bash
path /usr -d -n bin
```

Find files larger than 1MB:
```bash
path . -f -s +1M
```

Find files modified in the last 7 days:
```bash
path . -f -m 7
```

Tree view at 3 layers:
```bash
path . --tree -l 3
```

List files with sizes:
```bash
path . -f -L
```

Count files and directories:
```bash
path . --count
```

## Size Suffixes

| Suffix | Meaning |
|--------|---------|
| `B` | Bytes |
| `K` | Kilobytes (1024) |
| `M` | Megabytes (1024²) |
| `G` | Gigabytes (1024³) |

Prefix with `+` for "larger than", `-` for "smaller than":
```bash
path . -f -s +500K    # files > 500KB
path . -f -s -1M      # files < 1MB
```

## Build

```bash
bazel build //:path_bin
```

## License

MIT
