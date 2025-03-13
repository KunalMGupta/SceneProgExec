from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sceneprogexec",
    version="0.1.6",
    packages=find_packages(),  # Automatically finds the 'sceneprogexec' package (and any sub-packages)
    entry_points={
        "console_scripts": [
            # If 'main()' is defined in exec.py, reference it here.
            "sceneprogexec=sceneprogexec:main",
        ],
    },
    install_requires=[],  # Add any dependencies here
    author="Kunal Gupta",
    description="A CLI and Python module for executing Blender scripts and managing Blender's Python environment. Built to support SceneProg projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KunalMGupta/SceneProgExec",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)