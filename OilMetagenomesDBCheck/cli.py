import click
from OilMetagenomesDBCheck import __version__
from OilMetagenomesDBCheck.main import run_tests
from pathlib import Path


@click.command()
@click.version_option(__version__)
@click.argument("dataset", type=click.Path(exists=True))
@click.argument("schema", type=click.Path(exists=True))
@click.option("-v", "--validity", is_flag=True, help="Turn on schema checking.")
@click.option("-m", "--markdown", is_flag=True, help="Output is in markdown format")

def cli(no_args_is_help=True, **kwargs):
    """\b
    ancientMetagenomeDirCheck: Performs validity check of ancientMetagenomeDir datasets
    Homepage & Documentation: github.com/agni-bioinformatics-lab/OilMetagenomesDBCheck
    \b
    DATASET: path to tsv file of dataset to check
    SCHEMA: path to JSON schema file
    """
    run_tests(**kwargs)


if __name__ == "__main__":
    cli()
