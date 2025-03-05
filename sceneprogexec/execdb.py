from .exec import SceneProgExecutor
from sceneprogllm import LLM
from tqdm import tqdm

class SceneProgExecutorWithDebugger(SceneProgExecutor):
    def __init__(self, api_path=None,
                 output_blend="scene_output.blend",
                 max_attempts=5,
                 ):
        super().__init__(output_blend)
    
        self.MAX_ATTEMPTS = max_attempts
        self.exec = SceneProgExecutor()
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
Also, you don't have to worry about importing additional modules. They are already imported for you.
"""
        if self.apis is not None:
            api_usage = f"""
Please refer to the API documentation:\n{self.apis}.
"""
        else:
            api_usage = ""

        system_desc = header + api_usage + default_system_desc
        self.llm_debugger = LLM(name='llm_debugger', system_desc=system_desc, response_format='code')
        
        header = f"""
You should go through the code as well as the traceback and find the errors including those caused by wrong use of the API. Then you must respond with the corrected code.
"""

        system_desc = header + api_usage + default_system_desc
        self.debugger = LLM(name='trace_debugger', system_desc=system_desc, response_format='code')

        self.checker = LLM(name='debug_checker', system_desc="You are supposed to go through the stdout and respond whether there are any errors or not. In case you don't see any errors (ignore warnings!) respond in a JSON format with 'errors': 'False'. Else, respond with 'errors': 'True'.", response_format='json')

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
                if not silent:
                    print(f"Attempt {i+1} failed. Debugging...")
                prompt = f"Input: {script}.\nErrors: {traceback}.\nDebugged code:"
                script = self.debugger(prompt)
                traceback = self.exec(script)
                pbar.update(1)

        raise Exception(f"Failed to execute the code. Debugging attempts exhausted after {self.MAX_ATTEMPTS} attempts.")
    
    def run_script(self, script_path, show_output=False, target=None, debug=True, silent=True):
        if not debug:
            return self.exec.run_script(script_path, show_output, target)
        
        with open(script_path, 'r') as f:
            script = f.read()

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
                if not silent:
                    print(f"Attempt {i+1} failed. Debugging...")
                prompt = f"Input: {script}.\nErrors: {traceback}.\nDebugged code:"
                script = self.debugger(prompt)
                traceback = self.exec(script)
                pbar.update(1)

        raise Exception(f"Failed to execute the code. Debugging attempts exhausted after {self.MAX_ATTEMPTS} attempts.")
    

def main():
    import argparse
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
    run_parser.add_argument("--debug", action="store_true")
    run_parser.add_argument("--silent", action="store_true")
    run_parser.add_argument("--api_path", help="Path to the API documentation")
    run_parser.add_argument("--max_attempts", default=5, type=int)
   
    args = parser.parse_args()
    executor = SceneProgExecutorWithDebugger(api_path=args.api_path, max_attempts=args.max_attempts)

    if args.command == "install":
        executor.install_packages(args.packages, hard_reset=args.reset)
    elif args.command == "run":
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