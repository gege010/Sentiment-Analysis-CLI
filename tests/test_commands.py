"""Test suite for src/cli/commands.py and main.py"""
import pytest
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_cli_analyze_command_exists():
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0


def test_cli_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0


def test_cli_analyze_requires_topic():
    result = runner.invoke(app, ["analyze"])
    assert result.exit_code != 0


def test_cli_analyze_with_missing_env_shows_error():
    result = runner.invoke(app, ["analyze", "--topic", "test"], env={})
    assert result.exit_code != 0
