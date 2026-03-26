from setuptools import setup, find_packages

setup(
    name="magicglass",
    version="0.1.0",
    description="Quantitative trading program for AI stocks with sentiment, fundamental, and market analysis",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "yfinance>=0.2.31",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "textblob>=0.17.1",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "magicglass=magicglass.main:main",
        ],
    },
)
