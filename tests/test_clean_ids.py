"""Tests for the clean_ids script."""

import io
import platform
import sys

import pytest

from bin.clean_ids import main


def run_clean_ids(monkeypatch, capsys, input_text):
    """Run clean_ids with fake stdin and return stdout."""
    fake_input = io.StringIO(input_text)
    monkeypatch.setattr(sys, "stdin", fake_input)

    main()

    captured = capsys.readouterr()
    return captured.out


def test_script_execution(monkeypatch, capsys):
    assert run_clean_ids(monkeypatch, capsys, "kcFsuxaJ1es\nasd123\n") == "kcFsuxaJ1es\n"


def test_good_bad_good(monkeypatch, capsys):
    result = run_clean_ids(monkeypatch, capsys, "kcFsuxaJ1es\nbad\nCctJNYYCPo0\n")
    assert result == "kcFsuxaJ1es\nCctJNYYCPo0\n"


def test_bad_lines_only(monkeypatch, capsys):
    assert run_clean_ids(monkeypatch, capsys, "bad\n1234\n") == ""


def test_os_is_linux():
    assert platform.system() == "Linux"


def test_python_version():
    assert sys.version_info.major == 3


@pytest.mark.xfail(reason="Example expected failure for lab requirement")
def test_expected_failure():
    assert 1 == 2


@pytest.mark.skip(reason="Example skipped test for lab requirement")
def test_skipped_future_test():
    assert False


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("kcFsuxaJ1es\n", "kcFsuxaJ1es\n"),
        ("CctJNYYCPo0\n", "CctJNYYCPo0\n"),
        ("bad\n", ""),
    ],
)
def test_parametrized_ids(monkeypatch, capsys, input_text, expected):
    assert run_clean_ids(monkeypatch, capsys, input_text) == expected
