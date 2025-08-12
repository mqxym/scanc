from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="scanc",
    version="1.1.0",
    description="AI-ready code-base scanner that outputs Markdown.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="mqxym",
    author_email="maxim@omg.lol",
    url="https://github.com/mqxym/scanc",
    project_urls={
        "Source": "https://github.com/mqxym/scanc",
        "Bug Tracker": "https://github.com/mqxym/scanc/issues",
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "treelib>=1.6.1",
    ],
    extras_require={
        "dev": [
            "pytest",
            "tox",
        ],
        "tiktoken": [
            "tiktoken>=0.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "scanc = scanc.cli:main",
        ],
    },
)