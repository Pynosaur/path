import os
import re
import sys


def read_app_doc(app_name):
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "doc", f"{app_name}.yaml"),
        os.path.join(os.path.dirname(sys.executable), "..", "doc", f"{app_name}.yaml"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    content = f.read()
                doc = {}
                for line in content.split("\n"):
                    if ":" in line and not line.strip().startswith("-"):
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key.upper() == key:
                            doc[key.lower()] = value
                return doc
            except Exception:
                pass

    return {
        "name": app_name,
        "version": "0.1.0",
        "description": "Pure Python file and directory finder",
    }
