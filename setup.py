from setuptools import setup, find_packages

setup(
    name="magicglass",
    version="0.1.0",
    description="A program to analyze stock trends",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "yfinance>=0.2.0",
        "matplotlib>=3.5.0",
        "pandas>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "magicglass=magicglass.main:main",
        ],
    },
)
