"""Run with the target platform's Python after installing .[all] and pyinstaller."""

from pathlib import Path
import platform
import subprocess
import sys

root = Path(__file__).resolve().parent

target = {"win32": "Windows", "linux": "Linux"}[sys.platform]

if platform.machine().lower() not in {"amd64", "x86_64"}:
    raise SystemExit("Build on x86-64.")

out = root / "com.oraculum.npc" / "Tools~" / target
work = root.parent / "build" / target

subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconfirm",
        "--name",
        "oraculum-bridge",
        "--distpath",
        str(out),
        "--specpath",
        str(work),
        "--workpath",
        str(work / "work"),
        "--collect-submodules",
        "oraculum.providers",
        "--paths",
        str(root.parent),
        str(root / "bridge.py"),
    ],
    check=True,
)
