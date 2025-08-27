"""
Setup script for GitHub Action TODO Tracker.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="github-action-todo-tracker",
    version="0.1.0",
    author="jjasghar",
    author_email="jjasghar@gmail.com",
    description="A tool to scan codebases for TODO comments and create GitHub issues",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jjasghar/github-action-todo-tracker",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "todo-tracker=todo_tracker.cli:cli",
        ],
    },
)
