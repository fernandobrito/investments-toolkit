import pathlib

from setuptools import setup, find_packages

# Get the long description from the README file
current_folder = pathlib.Path(__file__).parent.resolve()
long_description = (current_folder / "README.md").read_text(encoding="utf-8")

# Based on: https://packaging.python.org/tutorials/packaging-projects/
setup(
    name="investments-toolkit",
    version="0.1.0",
    description="Utilities for automating investments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fernandobrito/investments-toolkit",
    author="Fernando Brito",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License 2.0 (Apache-2.0)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9, <4",
    install_requires=[
        "fastapi[all] ~= 0.68.1",
        "google-cloud-firestore ~= 2.3.0",
        "requests ~= 2.26.0",
        "requests-cache[json] ~= 0.8.0",
        "pandas ~= 1.3.2",
        "scipy ~= 1.7.1",
        "numpy ~= 1.21.2",
        "plotly ~= 5.2.1",
        "kaleido ~= 0.2.1",
        "python-dotenv ~= 0.19.0",
        "pydantic ~= 1.8.2",
        # "avanza-api ~= 2.8.0",
        "avanza-api @ git+https://github.com/fernandobrito/avanza@retrieve-stop-loss",
        "structlog ~= 21.2.0",
        "rich ~= 10.12.0",
        "papermill ~= 2.3.3",
        "nbconvert ~= 6.2.0"
    ]
)
