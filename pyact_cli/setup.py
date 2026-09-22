from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyact-cli",
    version="0.3.0",
    author="Abstergo2003",
    author_email="",
    description="A CLI tool to compile .pamd files to Markdown.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Abstergo2003/PyAct",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pyact=pyact.cli:main",
        ],
    },
)
