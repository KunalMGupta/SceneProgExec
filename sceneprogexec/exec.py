#!/usr/bin/env python3

import os
import subprocess
import shutil
import argparse
import sys
from sceneprogllm import LLM
from tqdm import tqdm
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
            # TODO: Compatible with different versions of Blender
            if os.path.exists(os.path.join(resources_dir, "4.3", "python", "bin", "python3.11")):
                python_path = os.path.join(resources_dir, "4.3", "python", "bin", "python3.11")
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
    def __init__(self, output_blend="scene_output.blend"):

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
        
        self.output_blend = output_blend

    def __call__(self, script: str, target: str = None, location=None):
        """
        Creates a temporary script file and runs it inside Blender,
        saving the .blend file to `target` if specified, otherwise
        uses `self.output_blend`.
        """

        if target is None:
            target = self.output_blend

        if location is None:
            location = os.getcwd()
            
        temp_script_path = os.path.join(location, "temp_script.py")
        with open(temp_script_path, "w") as f:
            f.write(script)

        # Run the script inside Blender and save to `target`
        output = self.run_script(temp_script_path, target=target)

        # Cleanup the temporary script file
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
        
        return output
    
    def run_script(self, temp_script_path, target, show_output=False):
        script_abs = os.path.abspath(temp_script_path)
        script_dir = os.path.dirname(script_abs)
        self.log_path = os.path.join(script_dir, "blender_log.txt")

        with open(temp_script_path, 'r') as f:
            script = f.read()

        if target is None:
            target = self.output_blend
        code = f"""
import sys
sys.path.append('{script_dir}')
{script}
import bpy
bpy.ops.wm.save_mainfile(filepath=r"{os.path.abspath(target)}")
"""
        
        self.temp_exec_path = os.path.join(script_dir,"temp_exec.py")

        with open(self.temp_exec_path, "w") as f:
            f.write(code)

        print(f"🚀 Running script {temp_script_path} in Blender (via wrapper) and saving to {target}...")
        
        cmd = f"cd {script_dir} && {self.blender_path} --background --python {self.temp_exec_path} 2> {self.log_path}"
        
        os.system(cmd)

        # Read Blender's stderr (the log)
        with open(self.log_path, "r") as log_file:
            blender_output = log_file.read().strip()

        self.cleanup()
        if show_output:
            print(blender_output)

        return None, blender_output

    def cleanup(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

        if os.path.exists(self.temp_exec_path):
            os.remove(self.temp_exec_path)

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

class SceneProgExecWithDebugger(SceneProgExec):
    def __init__(self, api_path=None,
                 output_blend="scene_output.blend",
                 max_attempts=5,
                 ):
        super().__init__(output_blend)
    
        self.MAX_ATTEMPTS = max_attempts
        self.exec = SceneProgExec()
        self.api_path = api_path
        if api_path is not None:
            with open(api_path, 'r') as f:
                self.apis = f.read()
        else:
            self.apis = None

        header = f"""
You should go through the code and find the errors including those caused by wrong use of the API. Then you must respond with the corrected code.
Only add the code that is necessary to fix the errors. Don't add any other code.
"""
        default_system_desc = f"""
First identify the errors and then respond with the corrected code. You should also pay attention to the exceptions raised while running the code and find ways to fix them. 
You are not supposed to change placement values or settings in the code, but only watch out for reasons due to which the code may crash!
Lastly, don't save or export the scene, I will do that myself later.
Also, you don't have to worry about importing additional modules. They are already imported for you.In case the code includes imports, make sure that debugged code includes the same imports.
Make sure that the debugged code does what the original code was intended to do and that it is not doing anything extra. The only thing you have to do is to fix the errors.
Example:
code:
a = 1+1
b = 1+a
c = 1++b
print("Hello, world!"

debugged code:
a = 1+1
b = 1+a
c = 1+b
print("Hello, world!")

code:
import numpy as np
a = np.array([1,2,3])
b = np.array([4,5,6],[7,8,9])

debugged code:
import numpy as np
a = np.array([1,2,3])
b = np.array([[4,5,6],[7,8,9]])

"""
        if self.apis is not None:
            api_usage = f"""
Please refer to the API documentation:\n{self.apis}.
"""
        else:
            api_usage = ""

        system_desc = header + api_usage + default_system_desc
        self.llm_debugger = LLM(name='llm_debugger', system_desc=system_desc, response_format='code',use_cache=False)
        
        header = f"""
You should go through the code as well as the traceback and find the errors including those caused by wrong use of the API. Then you must respond with the corrected code.
"""

        system_desc = header + api_usage + default_system_desc
        self.debugger = LLM(name='trace_debugger', system_desc=system_desc, response_format='code',use_cache=False)

        self.checker = LLM(name='debug_checker', system_desc="You are supposed to go through the stdout and respond whether there are any errors or not. In case you don't see any errors (ignore warnings!) respond in a JSON format with 'errors': 'False'. Else, respond with 'errors': 'True'.", response_format='json',use_cache=False)

    def __call__(self, script: str, target: str = None, debug=True, silent=True):
        if not debug:
            return script,self.exec(script)
        script = self.llm_debugger(script)
        if not silent:
            print("Attempting to run the code...")
        traceback = self.exec(script)

        with tqdm(total=self.MAX_ATTEMPTS, desc="Debugging Attempts") as pbar:
            for i in range(self.MAX_ATTEMPTS):
                checker = self.checker(traceback)
                if checker['errors']=='False':
                    if not silent:
                        print("Success!")
                    return script, traceback
                prompt = f"Input: {script}.\nErrors: {traceback}.\nDebugged code:"
                script = self.debugger(prompt)
                traceback = self.exec(script)
                pbar.update(1)

        raise Exception(f"Failed to execute the code. Debugging attempts exhausted after {self.MAX_ATTEMPTS} attempts. Last traceback: \n{traceback} \n\nLast debugged code: \n{script}")
    
    def run_script(self, script_path, show_output=False, target=None, debug=True, silent=True):
        if not debug:
            return self.exec.run_script(script_path, target, show_output)
        
        with open(script_path, 'r') as f:
            script = f.read()

        script = self.llm_debugger(script)
        if not silent:
            print("Attempting to run the code...")
        _, traceback = self.exec(script, target=target, location=os.path.dirname(script_path))
        
        with tqdm(total=self.MAX_ATTEMPTS, desc="Debugging Attempts") as pbar:
            for i in range(self.MAX_ATTEMPTS):
                checker = self.checker(traceback)
                if checker['errors']=='False':
                    if not silent:
                        print("Success!")
                    return script, traceback
                if not silent:
                    print(f"Attempt {i+1} failed. Debugging...")
                prompt = f"Input: {script}.\nErrors: {traceback}.\nDebugged code:"
                print(prompt)
                script = self.debugger(prompt)
                _, traceback = self.exec(script, target=target, location=os.path.dirname(script_path))
                pbar.update(1)

        raise Exception(f"Failed to execute the code. Debugging attempts exhausted after {self.MAX_ATTEMPTS} attempts. Last traceback: \n{traceback} \n\nLast debugged code: \n{script}")
    

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
    run_parser.add_argument("--target", required=True, help="Path to save the resulting .blend file")
    run_parser.add_argument("--debug", action="store_true")
    run_parser.add_argument("--silent", action="store_true")
    run_parser.add_argument("--api_path", default=None, help="Path to the API documentation")
    run_parser.add_argument("--max_attempts", default=5, type=int)
   
    args = parser.parse_args()
    
    if args.command == "install":
        executor = SceneProgExec()
        executor.install_packages(args.packages, hard_reset=args.reset)
    elif args.command == "run":
        executor = SceneProgExecWithDebugger(api_path=args.api_path, max_attempts=args.max_attempts)
        script, traceback = executor.run_script(args.script_path, show_output=True, target=args.target, debug=args.debug, silent=args.silent)
        print("*********** SCRIPT ***********")
        print(script)
        print("*********** TRACEBACK ***********")
        print(traceback)
        print("*********** END ***********")
    elif args.command == "reset":
        executor._delete_all_third_party_packages()

if __name__ == "__main__":
    main()

# exec = SceneProgExec()
# exec.run_script('/Users/kunalgupta/Documents/scenecraft/test4.py', '/Users/kunalgupta/Documents/scenecraft/scene_output.blend')



    

