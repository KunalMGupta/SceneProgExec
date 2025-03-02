# #!/usr/bin/env python3

# import os
# import subprocess
# import shutil
# import argparse
# import sys
# import tempfile

# class SceneProgExecutor:
#     def __init__(self, output_blend="scene_output.blend"):
#         """
#         Initializes SceneProgExecutor with script execution and package management capabilities.
#         """
#         blender_path = os.getenv("BLENDER_PATH")
#         blender_python = os.getenv("BLENDER_PYTHON")

#         if blender_path is None or blender_python is None:
#             msg = """
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# BLENDER_PATH and BLENDER_PYTHON environment variables must be set.
# Example:
# export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
# export BLENDER_PYTHON=/Applications/Blender.app/Contents/Resources/4.3/python/bin/python3.11
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             """
#             raise Exception(msg)
        
#         self.blender_path = blender_path
#         self.blender_python = blender_python
#         self.output_blend = output_blend
#         self.tmp_dir = "blender_tmp"
#         self.log_path = os.path.join(self.tmp_dir, "blender_log.txt")

#         os.makedirs(self.tmp_dir, exist_ok=True)

#     def __call__(self, script: str):
#         """Creates a temporary script file and runs it inside Blender."""
#         temp_script_path = os.path.join(self.tmp_dir, "sceneprog_exec.py")

#         # Save the script content to a temporary file
#         with open(temp_script_path, "w") as f:
#             f.write(script)

#         # Run the script inside Blender
#         output = self.run_script(temp_script_path)

#         # Cleanup the temporary script file
#         if os.path.exists(temp_script_path):
#             os.remove(temp_script_path)

#         return output

#     def run_script(self, script_path, show_output=False):
#         """Runs a given Python script inside Blender."""
#         if not os.path.exists(script_path):
#             print(f"❌ Error: Script {script_path} not found.")
#             sys.exit(1)

#         print(f"🚀 Running script {script_path} in Blender...")
#         os.system(f"{self.blender_path} --background --python {script_path} 2> {self.log_path}")
#         with open(self.log_path, "r") as log_file:
#             blender_output = log_file.read().strip()
#         self.cleanup()
#         if show_output:
#             print(blender_output)
#         return blender_output

#     def install_packages(self, packages, hard_reset=False):
#         """Installs Python packages inside Blender's environment."""
#         if hard_reset:
#             print("\n🔄 Performing Hard Reset...\n")
#             self._delete_all_third_party_packages()
#             self._delete_user_modules()

#         for package in packages:
#             print(f"📦 Installing {package} inside Blender's Python...")
#             os.system(f"{self.blender_python} -m pip install {package} --force 2> {self.log_path}")
#             with open(self.log_path, "r") as log_file:
#                 print(log_file.read())

#         print("✅ All packages installed.")

#     def _delete_all_third_party_packages(self):
#         """Deletes all third-party packages from Blender's site-packages."""
#         try:
#             result = subprocess.run(
#                 [self.blender_python, "-m", "pip", "freeze"],
#                 capture_output=True, text=True
#             )
#             packages = [line.split("==")[0] for line in result.stdout.splitlines()]

#             if not packages:
#                 print("✅ No third-party packages found.")
#                 return

#             print(f"🗑️ Removing {len(packages)} third-party packages...")
#             subprocess.run(
#                 [self.blender_python, "-m", "pip", "uninstall", "-y"] + packages,
#                 text=True
#             )
#             print("✅ All third-party packages removed.")
#         except Exception as e:
#             print(f"⚠️ Error removing packages: {e}")

#     def _delete_user_modules(self):
#         """Deletes all user-installed packages from Blender's user module directory."""
#         if os.path.exists(self.user_modules):
#             try:
#                 shutil.rmtree(self.user_modules)
#                 print(f"🗑️ Deleted all modules in {self.user_modules}")
#             except Exception as e:
#                 print(f"⚠️ Could not delete user modules: {e}")
#         else:
#             print(f"✅ No user modules found in {self.user_modules}")

#     def cleanup(self):
#         """🔥 Deletes the temporary directory `blender_tmp` after execution."""
#         if os.path.exists(self.tmp_dir):
#             shutil.rmtree(self.tmp_dir)
#             print(f"🗑️ Cleanup: Deleted {self.tmp_dir}")

# def main():
#     parser = argparse.ArgumentParser(description="SceneProgExecutor CLI")
#     subparsers = parser.add_subparsers(dest="command")

#     install_parser = subparsers.add_parser("install", help="Install packages inside Blender's Python")
#     install_parser.add_argument("packages", nargs="+")
#     install_parser.add_argument("--reset", action="store_true")

#     run_parser = subparsers.add_parser("run", help="Run a Python script inside Blender")
#     run_parser.add_argument("script_path")

#     reset_parser = subparsers.add_parser("reset", help="Remove all third-party packages in Blender")

#     args = parser.parse_args()
#     executor = SceneProgExecutor()

#     if args.command == "install":
#         executor.install_packages(args.packages, hard_reset=args.reset)
#     elif args.command == "run":
#         executor.run_script(args.script_path, show_output=True)
#     elif args.command == "reset":
#         executor._delete_all_third_party_packages()

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3

import os
import subprocess
import shutil
import argparse
import sys
import tempfile

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
        self.output_blend = output_blend  # Default .blend filename if none specified
        self.tmp_dir = "blender_tmp"
        self.log_path = os.path.join(self.tmp_dir, "blender_log.txt")

        os.makedirs(self.tmp_dir, exist_ok=True)

    def __call__(self, script: str, target: str = None):
        """
        Creates a temporary script file and runs it inside Blender,
        saving the .blend file to `target` if specified, otherwise
        uses `self.output_blend`.
        """
        if target is None:
            target = self.output_blend

        temp_script_path = os.path.join(self.tmp_dir, "sceneprog_exec.py")

        # Save the script content to a temporary file
        with open(temp_script_path, "w") as f:
            f.write(script)

        # Run the script inside Blender and save to `target`
        output = self.run_script(temp_script_path, target=target)

        # Cleanup the temporary script file
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

        return output

    def run_script(self, script_path, show_output=False, target=None):
        """
        Auto-inject script_path's directory into sys.path, run script, and save .blend.
        This allows imports from the same directory (like `import api`) to work automatically.
        """
        if not os.path.exists(script_path):
            print(f"❌ Error: Script {script_path} not found.")
            sys.exit(1)
        if target is None:
            target = self.output_blend

        script_abs = os.path.abspath(script_path)
        script_dir = os.path.dirname(script_abs)

        # We'll create a temporary "wrapper script" that:
        #  1) Adds `script_path`'s directory to sys.path
        #  2) Reads and exec's the original script
        #  3) Saves the .blend file
        wrapper_script = os.path.join(self.tmp_dir, "wrapper_script.py")

        wrapper_code = f"""\
import sys, os

# Add the directory of the user script to sys.path
user_script_path = r"{script_abs}"
user_script_dir = r"{script_dir}"
if user_script_dir not in sys.path:
    sys.path.insert(0, user_script_dir)

# Now run the original script
with open(user_script_path, "rb") as f:
    code = compile(f.read(), user_script_path, "exec")
exec(code, {{}}, {{}})

# Finally, save the .blend file
import bpy
bpy.ops.wm.save_mainfile(filepath=r"{os.path.abspath(target)}")
"""

        with open(wrapper_script, "w") as f:
            f.write(wrapper_code)

        print(f"🚀 Running script {script_path} in Blender (via wrapper) and saving to {target}...")

        cmd = (
            f"{self.blender_path} --background --python {wrapper_script} "
            f"2> {self.log_path}"
        )
        os.system(cmd)

        # Read Blender's stderr (the log)
        with open(self.log_path, "r") as log_file:
            blender_output = log_file.read().strip()

        self.cleanup()
        if show_output:
            print(blender_output)

        return blender_output

    def install_packages(self, packages, hard_reset=False):
        """Installs Python packages inside Blender's environment."""
        if hard_reset:
            print("\n🔄 Performing Hard Reset...\n")
            self._delete_all_third_party_packages()
            self._delete_user_modules()

        for package in packages:
            print(f"📦 Installing {package} inside Blender's Python...")
            os.system(f"{self.blender_python} -m pip install {package} --force 2> {self.log_path}")
            with open(self.log_path, "r") as log_file:
                print(log_file.read())

        print("✅ All packages installed.")

    def _delete_all_third_party_packages(self):
        """Deletes all third-party packages from Blender's site-packages."""
        try:
            result = subprocess.run(
                [self.blender_python, "-m", "pip", "freeze"],
                capture_output=True, text=True
            )
            packages = [line.split("==")[0] for line in result.stdout.splitlines()]

            if not packages:
                print("✅ No third-party packages found.")
                return

            print(f"🗑️ Removing {len(packages)} third-party packages...")
            subprocess.run(
                [self.blender_python, "-m", "pip", "uninstall", "-y"] + packages,
                text=True
            )
            print("✅ All third-party packages removed.")
        except Exception as e:
            print(f"⚠️ Error removing packages: {e}")

    def _delete_user_modules(self):
        """Deletes all user-installed packages from Blender's user module directory."""
        if os.path.exists(self.user_modules):
            try:
                shutil.rmtree(self.user_modules)
                print(f"🗑️ Deleted all modules in {self.user_modules}")
            except Exception as e:
                print(f"⚠️ Could not delete user modules: {e}")
        else:
            print(f"✅ No user modules found in {self.user_modules}")

    def cleanup(self):
        """🔥 Deletes the temporary directory `blender_tmp` after execution."""
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
            print(f"🗑️ Cleanup: Deleted {self.tmp_dir}")

def main():
    parser = argparse.ArgumentParser(description="SceneProgExecutor CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: install packages
    install_parser = subparsers.add_parser("install", help="Install packages inside Blender's Python")
    install_parser.add_argument("packages", nargs="+")
    install_parser.add_argument("--reset", action="store_true")

    # Subcommand: run a script
    run_parser = subparsers.add_parser("run", help="Run a Python script inside Blender and save as a .blend file")
    run_parser.add_argument("script_path")
    run_parser.add_argument("--target", required=True, help="Path to save the resulting .blend file")

    # Subcommand: reset third-party packages
    reset_parser = subparsers.add_parser("reset", help="Remove all third-party packages in Blender")

    args = parser.parse_args()
    executor = SceneProgExecutor()

    if args.command == "install":
        executor.install_packages(args.packages, hard_reset=args.reset)
    elif args.command == "run":
        executor.run_script(args.script_path, show_output=True, target=args.target)
    elif args.command == "reset":
        executor._delete_all_third_party_packages()

if __name__ == "__main__":
    main()