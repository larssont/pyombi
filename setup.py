from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyombi",
    version="0.1.0",
    url="https://github.com/larssont/pyombi",
    author="Tommy Larsson",
    author_email="larssont@tuta.io",
    description="A python module to retrieve information from Ombi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["pyombi"],
    package_dir={"": "pyombi"},
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
