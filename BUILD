genrule(
    name = "path_bin",
    srcs = glob(["app/**/*.py", "doc/**/*.yaml"]),
    outs = ["path"],
    cmd = """
        /opt/homebrew/bin/nuitka \
            --onefile \
            --include-data-dir=doc=doc \
            --onefile-tempdir-spec=/tmp/nuitka-path \
            --no-progressbar \
            --assume-yes-for-downloads \
            --no-deployment-flag=self-execution \
            --output-dir=$$(dirname $(location path)) \
            --output-filename=path \
            $(location app/main.py)
    """,
    local = 1,
    visibility = ["//visibility:public"],
)
