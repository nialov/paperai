"""
Tests for cli.py.
"""

from typer.testing import CliRunner
from traceback import print_tb
from click.testing import Result
import pytest
from paperai import cli
import tests

runner = CliRunner()

def click_error_print(result: Result):
    """
    Print click result traceback.
    """
    if result.exit_code == 0:
        return
    assert result.exc_info is not None
    _, _, tb = result.exc_info
    # print(err_class, err)
    print_tb(tb)
    print(result.output)
    raise Exception(result.exception)

@pytest.mark.parametrize("subcommand,args", tests.test_app_params())
def test_app(subcommand,args):
    """
    Test app.
    """
    result = runner.invoke(cli.app, [subcommand, *args])
    click_error_print(result=result)

