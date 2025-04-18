import os
import subprocess
import shutil
import platform

class BlenderPythonDetector:
    def __init__(self):
        pass

    def find_blender_path(self):
        system = platform.system()
        if system == "Darwin":
            # print("Running on macOS")
            if os.path.exists("/Applications/Blender.app/Contents/MacOS/Blender"):
                return "/Applications/Blender.app/Contents/MacOS/Blender"
        else:
            print("Blender not found")
            return None
        # TODO: Add Linux and Windows paths
        # elif system == "Linux":
        # elif system == "Windows":

    def find_blender_python_path(self, blender_path):
        system = platform.system()
        if not blender_path:
            return None

        if system == "Darwin":  # macOS
            # /Applications/Blender.app/Contents/MacOS/Blender 
            base_dir = os.path.dirname(os.path.dirname(blender_path))

            # different versions of blender have different versions of python in Resources
            resources_dir = os.path.join(base_dir, "Resources")
            # We only care the newest version of python in Resources now
            # export BLENDER_PYTHON=/Applications/Blender.app/Contents/Resources/4.3/python/bin/python3.11
            for version in os.listdir(resources_dir):
                try:
                    version_num = float(version)
                except:
                    continue
            
            if os.path.exists(os.path.join(resources_dir, str(version_num), "python", "bin", "python3.11")):
                python_path = os.path.join(resources_dir, str(version_num), "python", "bin", "python3.11")
                return python_path
            else:
                print("Blender Python not found")
                return None

        # TODO: Add Linux and Windows paths
        # elif system == "Linux":
        # elif system == "Windows":

    def __call__(self):
        detected_blender_path = self.find_blender_path()
        detected_python_path = self.find_blender_python_path(detected_blender_path)
        return detected_blender_path, detected_python_path            

class SceneProgExec:
    def __init__(self, caller_path=None):
        '''
        caller_path: str - Path to the caller script
        '''
        self.caller_path = caller_path
        self.blender_path, self.blender_python = BlenderPythonDetector()()
        
        if self.blender_path is None or self.blender_python is None:
            msg = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
BLENDER_PATH and BLENDER_PYTHON environment variables must be set.
Example:
export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
export BLENDER_PYTHON=/Applications/Blender.app/Contents/Resources/4.3/python/bin/python3.11
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            """
            raise Exception(msg)
        
        # Dynamically extract Blender version from Python path
        import re
        match = re.search(r'Resources/([\d.]+)/python', self.blender_python)
        blender_version = match.group(1) if match else "4.3"

        # Set the user modules path
        self.user_modules = os.path.expanduser(
            f"~/Library/Application Support/Blender/{blender_version}/scripts/modules"
        )
        
    def __call__(self, script:str, target:str=None, verbose=False):
        location = os.getcwd()

        random_uid = str(int(os.urandom(4).hex(), 16))
        tmp_script_path = os.path.join(location, f"{random_uid}.py")
        with open(tmp_script_path, "w") as f:
            f.write(script)

        output = self.run_script(tmp_script_path, target=target, verbose=verbose)

        if os.path.exists(tmp_script_path):
            os.remove(tmp_script_path)

        return output

    def run_script(self, script_path:str, target:str = None, verbose=False):
        script_abs = os.path.abspath(script_path)
        script_dir = os.path.dirname(script_abs)
        log_name = os.path.basename(script_path).replace(".py", ".log")
        self.log_path = os.path.join(script_dir, log_name)
        with open(script_path, "r") as f:
            script = f.read()
        code = f"""
import sys
sys.path.append('{script_dir}')
{script}
"""
        if target:
            code = f"""
{code}
import bpy
bpy.ops.wm.save_mainfile(filepath=r"{os.path.abspath(target)}")
"""
        if self.caller_path:
            code = f"""
import sys
sys.path.append(r"{self.caller_path}")
{code}
"""
        
        self.tmp_exec_path = script_abs.split(".py")[0] + "_exec.py"
        with open(self.tmp_exec_path, "w") as f:
            f.write(code)
        
        if verbose:
            print(f"🚀 Running {script_path} in Blender (via wrapper)")
        cmd = f"cd {script_dir} && {self.blender_path} --background --python {self.tmp_exec_path} 2> {self.log_path}"
        os.system(cmd)

        # Read Blender's stderr (the log)
        with open(self.log_path, "r") as log_file:
            blender_output = log_file.read().strip()

        self.cleanup()
        if verbose:
            print(blender_output)
        
        return blender_output
    
    def cleanup(self):
        if os.path.exists(self.tmp_exec_path):
            os.remove(self.tmp_exec_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
    
    def install_packages(self, packages, hard_reset=False):
        """Installs Python packages inside Blender's environment."""
        if hard_reset:
            print("\n🔄 Performing Hard Reset...\n")
            self._delete_all_third_party_packages()
            self._delete_user_modules()

        self.log_path = os.path.join(os.getcwd(), "blender_pip_log.txt")
        for package in packages:
            print(f"📦 Installing {package} inside Blender's Python...")
            os.system(f"{self.blender_python} -m pip install {package} --force 2> {self.log_path}")
            with open(self.log_path, "r") as log_file:
                print(log_file.read())

        print("✅ All packages installed.")
        os.remove(self.log_path)

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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SceneProgExec CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: install packages
    install_parser = subparsers.add_parser("install", help="Install packages inside Blender's Python")
    install_parser.add_argument("packages", nargs="+")
    install_parser.add_argument("--reset", action="store_true")

    # Subcommand: run a script
    run_parser = subparsers.add_parser("run", help="Run a Python script inside Blender and save as a .blend file")
    run_parser.add_argument("script_path")
    run_parser.add_argument("--target", required=False, help="Path to save the resulting .blend file")
    run_parser.add_argument("--verbose", action="store_true")

    # Subcommand: reset
    reset_parser = subparsers.add_parser("reset", help="Reset all third-party packages and user modules")
    args = parser.parse_args()

    executor = SceneProgExec()
    if args.command == "install":
        executor.install_packages(args.packages, hard_reset=args.reset)

    elif args.command == "run":
        output = executor.run_script(args.script_path, target=args.target, verbose=args.verbose)

    elif args.command == "reset":
        executor._delete_all_third_party_packages()

if __name__ == "__main__":
    main()