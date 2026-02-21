"""Tests for CLI entry point."""
import pytest
from click.testing import CliRunner
from xr.cli import main

@pytest.fixture
def runner():
    return CliRunner()

def test_version(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output

def test_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "tweet" in result.output
    assert "search" in result.output
    assert "user" in result.output
