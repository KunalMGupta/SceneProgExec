from setuptools import setup

setup(
    name="sceneprogexec",
    version="0.1.0",
    py_modules=["sceneprogexec"],
    entry_points={
        "console_scripts": [
            "sceneprogexec=sceneprogexec:main",  # Creates global CLI command `sceneprog`
        ],
    },
    install_requires=[],
    author="Kunal Gupta",
    description="A CLI and Python module for executing Blender scripts and managing Blender's Python environment. Built to support SceneProg projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KunalMGupta/SceneProgExec",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)