#!/usr/bin/env python3

import os
import subprocess
import shutil
import argparse
import sys

class SceneProgExecutor:
    def __init__(self, output_blend="scene_output.blend"):
        """
        Initializes SceneProgExecutor with script execution and package management capabilities.
        """
        blender_path = os.getenv("BLENDER_PATH")
        blender_python = os.getenv("BLENDER_PYTHON")

        if blender_path is None or blender_python is None:
            msg = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
BLENDER_PATH and BLENDER_PYTHON environment variables must be set.
Example:
export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
export BLENDER_PYTHON=/Applications/Blender.app/Contents/Resources/4.3/python/bin/python3.11
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            """
            raise Exception(msg)
        
        self.blender_path = blender_path
        self.blender_python = blender_python
        self.output_blend = output_blend
        self.tmp_dir = "blender_tmp"
        self.log_path = os.path.join(self.tmp_dir, "blender_log.txt")

        os.makedirs(self.tmp_dir, exist_ok=True)

    def run_script(self, script_path):
        """Runs a given Python script inside Blender."""
        if not os.path.exists(script_path):
            print(f"❌ Error: Script {script_path} not found.")
            sys.exit(1)

        print(f"🚀 Running script {script_path} in Blender...")
        os.system(f"{self.blender_path} --background --python {script_path} 2> {self.log_path}")

        self.cleanup()

    def install_packages(self, packages, hard_reset=False):
        """Installs Python packages inside Blender's environment."""
        if hard_reset:
            self._delete_all_third_party_packages()

        for package in packages:
            os.system(f"{self.blender_python} -m pip install {package} --force 2> {self.log_path}")

        self.cleanup()

    def _delete_all_third_party_packages(self):
        """Deletes all third-party packages from Blender's site-packages."""
        subprocess.run([self.blender_python, "-m", "pip", "freeze"], capture_output=True, text=True)

        self.cleanup()

    def cleanup(self):
        """🔥 Deletes the temporary directory `blender_tmp` after execution."""
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
            print(f"🗑️ Cleanup: Deleted {self.tmp_dir}")

def main():
    parser = argparse.ArgumentParser(description="SceneProgExecutor CLI")
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Install packages inside Blender's Python")
    install_parser.add_argument("packages", nargs="+")
    install_parser.add_argument("--reset", action="store_true")

    run_parser = subparsers.add_parser("run", help="Run a Python script inside Blender")
    run_parser.add_argument("script_path")

    reset_parser = subparsers.add_parser("reset", help="Remove all third-party packages in Blender")

    args = parser.parse_args()
    executor = SceneProgExecutor()

    if args.command == "install":
        executor.install_packages(args.packages, hard_reset=args.reset)
    elif args.command == "run":
        executor.run_script(args.script_path)
    elif args.command == "reset":
        executor._delete_all_third_party_packages()

if __name__ == "__main__":
    main()