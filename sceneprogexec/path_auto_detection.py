import os
import platform

def find_blender_path():
    system = platform.system()
    if system == "Darwin":
        print("Running on macOS")
        if os.path.exists("/Applications/Blender.app/Contents/MacOS/Blender"):
            return "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        print("Blender not found")
        return None
    # TODO: Add Linux and Windows paths
    # elif system == "Linux":
    # elif system == "Windows":
        


def find_blender_python_path(blender_path):
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

if __name__ == "__main__":
    if not os.environ.get("BLENDER_PATH") or not os.environ.get("BLENDER_PYTHON"):
        # Try to auto-detect paths
        detected_blender_path = find_blender_path()
        if detected_blender_path:
            detected_python_path = find_blender_python_path(detected_blender_path)
            if detected_python_path:
                # Set environment variables for current process
                os.environ["BLENDER_PATH"] = detected_blender_path
                os.environ["BLENDER_PYTHON"] = detected_python_path
                print(f"Auto-detected Blender path: {detected_blender_path}")
                print(f"Auto-detected Python path: {detected_python_path}")


