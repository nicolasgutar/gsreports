"""Setup file for gsreports package."""
from setuptools import setup, find_packages

setup(
    name="gsreports",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.1.3",
        "openpyxl>=3.1.2",
    ],
    python_requires=">=3.8",
)
