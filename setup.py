"""CodeRefactor Pilot - AI-Powered Code Review & Intelligent Refactoring Engine."""
import os
import sys
from setuptools import setup, find_packages

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="coderefactor-pilot",
    version="1.0.0",
    description="AI-Powered Code Review & Intelligent Refactoring Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CodeRefactor Pilot Team",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[],
    extras_require={
        "dev": [],
    },
    entry_points={
        "console_scripts": [
            "coderefactor-pilot=coderefactor_pilot.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
