from setuptools import setup, find_packages
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="OilMetagenomesDBCheck",
    version=get_version("OilMetagenomesDBCheck/__init__.py"),
    description="Performs validity check of OilMetagenomesDB datasets",
    long_description=open("README.md").read(),
    url="https://github.com/rakhmanov-tr/OilMetagenomePy",
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=["click", "pandas", "jsonschema", "rich"],
    packages=find_packages(include=["OilMetagenomesDBCheck"]),
    entry_points={
        "console_scripts": [
            "OilMetagenomesDBCheck = OilMetagenomesDBCheck.cli:cli"
        ]
    },
)
