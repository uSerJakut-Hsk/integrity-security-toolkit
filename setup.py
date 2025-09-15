
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="file-integrity-checker",
    version="1.0.0",
    author="Security Team",
    author_email="security@example.com",
    description="A comprehensive file integrity monitoring tool for security professionals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/file-integrity-checker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "integrity-checker=file_integrity_checker:main",
        ],
    },
    install_requires=[
        "pathlib",
    ],
)