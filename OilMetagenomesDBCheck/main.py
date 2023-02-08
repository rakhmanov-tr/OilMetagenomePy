import pandas as pd
import json
from jsonschema import Draft7Validator
from io import StringIO
from OilMetagenomesDBCheck.exceptions import DatasetValidationError
import sys
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.table import Table


def check_extra_missing_columns(dataset, schema):
    """Check if there are extra or missing column in dataset
    Args:
        dataset (str): Path to dataset in tsv format
        schema (str): path to json schema
        markdown(bool): format ouput in markdown
    Returns:
        (str): If dataset has extra or missing columns compared to schema
    """

    dt = pd.read_csv(dataset, sep="\t")
    dt_json = json.load((StringIO(dt.to_json(orient="records"))))

    with open(schema, "r") as j:
        json_schema = json.load(j)

    required_columns = json_schema["items"]["required"]
    present_columns = list(dt.columns)
    missing_columns = list(set(required_columns) - set(present_columns))
    extra_columns = list(set(present_columns) - set(required_columns))
    if len(missing_columns) > 0:
        message = f"The required column(s) {', '.join(missing_columns)} is/are missing"
        print(message)
        return "MissingColumnError"
    if len(extra_columns) > 0:
        message = f"Additional column(s) {', '.join(extra_columns)} not allowed"
        print(message)
        return "UnwantedColumnError"


def check_validity(dataset, schema):
    """Check validity of dataset against schema
    Args:
        dataset (str): Path to dataset in tsv format
        schema (str): path to json schema
    Returns:
        (str): If dataset is not validated by schema
    """
    dt = pd.read_csv(dataset, sep="\t")
    dt_json = json.load((StringIO(dt.to_json(orient="records"))))

    with open(schema, "r") as j:
        json_schema = json.load(j)

    v = Draft7Validator(json_schema)
    errors = []
    for error in sorted(v.iter_errors(dt_json), key=str):
        errors.append(error)
    if len(errors) > 0:
        table = Table(title="Validation Errors were found")
        table.add_column(
            "Offending value",
            justify="right",
            style="red",
            no_wrap=True,
            # overflow="fold",
        )
        table.add_column("Line number", style="red")
        table.add_column("Column", justify="right", style="cyan")
        table.add_column("Error", style="magenta", overflow="fold")
        lines = []
        for error in errors:
            err_column = list(error.path)[-1]
            if "enum" in error.schema:
                if len(error.schema["enum"]) > 3:
                    error.message = f"'{error.instance}' is not an accepted value.\nPlease check [link={json_schema['items']['properties'][err_column]['$ref']}]{json_schema['items']['properties'][err_column]['$ref']}[/link]"
            err_line = str(error.path[0] + 2)
            lines.append(
                [
                    str(error.instance),
                    err_line,
                    str(err_column),
                    error.message,
                ]
            )

        # remove duplicate lines
        b_set = set(tuple(x) for x in lines)
        b = [list(x) for x in b_set]

        for l in b:
            table.add_row(*l)
        return ["DatasetValidationError", table]


def run_tests(dataset, schema, validity, markdown):

    print(f"Checking {dataset} against schema {schema}")

    check_list = []
    table_list = []
    error_list = []

    danger_style = Style(color="red", blink=True)
    ok_style = Style(color="green")
    console = Console()

    try:
        check_list.append(check_extra_missing_columns(dataset, schema))
        if validity:
            check_list.append(check_validity(dataset, schema))

        check_list = list(filter(None.__ne__, check_list))
        [error_list.append(i[0]) for i in check_list]
        [table_list.append(i[1]) for i in check_list if len(i) > 1]
        error_list = ["* `" + i + "`\n" for i in error_list]

        if len(error_list) > 0:
            raise DatasetValidationError(
                f"**The following type of errors were found**:\n{''.join(error_list)}"
            )
        else:
            md = Markdown("**All is good, no errors were found !**")
            console.print(md, style=ok_style)
    except DatasetValidationError as e:
        if markdown:
            print(
                "\n **Errors were found, please unfold below to see errors:**\n\n <details>\n\n```"
            )

        for table in table_list:
            console.print(table)

        md = Markdown(str(e))
        console.print(md, style=danger_style)

        if markdown:
            print("```\n</details>")

        sys.exit(1)
