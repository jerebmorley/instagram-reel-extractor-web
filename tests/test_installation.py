"""Comprueba que la instalación no depende del directorio del repositorio."""

import subprocess
import sys


def test_package_imports_outside_repository(tmp_path):
    subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "import sorteos; from importlib.metadata import version; "
            "version('sorteos-ig')",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
