# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Tests for the do_validate() function."""

import dataclasses
from typing import Iterator
from unittest import mock

import markdown
import pytest

from pymdownx_superfence_filter_lines import (
    Inputs,
    LinesRange,
    LinesRanges,
    Options,
    do_validate,
)


@pytest.fixture
def highlight_validator_mock() -> Iterator[mock.MagicMock]:
    """Mock `highlight_validator`."""
    with mock.patch(
        "pymdownx_superfence_filter_lines.highlight_validator",
        autospec=True,
    ) as mock_highlight_validator:
        mock_highlight_validator.return_value = True
        yield mock_highlight_validator


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TestCase:
    title: str | None = None
    # We can't use just `Inputs` because `mypy` complains about type incompatibility,
    # which is not true.
    # pylint: disable=unnecessary-lambda
    inputs: Inputs = dataclasses.field(default_factory=lambda: Inputs())
    options: Options = dataclasses.field(default_factory=lambda: Options())
    expected_options: Options = dataclasses.field(default_factory=lambda: Options())
    # pylint: enable=unnecessary-lambda
    expected_warnings: list[str] = dataclasses.field(default_factory=list)


_cases = [
    _TestCase(title="No options"),
    _TestCase(title="Empty", inputs=Inputs(show_lines="")),
    _TestCase(
        inputs=Inputs(
            show_lines=",".join(
                [
                    "1:2",
                    "4+5",
                    "6",
                    "7:10",
                    "-1",
                    "-1:-2",
                    "0",
                    "0:",
                    ":0",
                    "-1:0:2",
                    "3:1",
                    "a",
                    " 18",
                    " 19:20",
                    "",
                    "  ",
                ]
            ),
        ),
        expected_options=Options(
            show_lines=LinesRanges(
                {
                    LinesRange(start=1, end=2),
                    LinesRange(start=6, end=6),
                    LinesRange(start=7, end=10),
                    LinesRange(start=18, end=18),
                    LinesRange(start=19, end=20),
                },
            )
        ),
        expected_warnings=[
            "Range 2 ('4+5') is invalid: invalid literal for int() with base 10: '4+5'",
            "Range 5 ('-1') is invalid: Start must be at least 1",
            "Range 6 ('-1:-2') is invalid: Start must be at least 1",
            "Range 7 ('0') is invalid: Start must be at least 1",
            "Range 8 ('0:') is invalid: Start must be at least 1",
            "Range 9 (':0') is invalid: End must be at least 1",
            "Range 10 ('-1:0:2') is invalid: invalid literal for int() with base 10: '0:2'",
            "Range 11 ('3:1') is invalid: Start must be less than or equal to end",
            "Range 12 ('a') is invalid: invalid literal for int() with base 10: 'a'",
            "Range 15 ('') is invalid: Empty start",
            "Range 16 ('  ') is invalid: Empty start",
        ],
    ),
]


@pytest.mark.parametrize(
    "case",
    _cases,
    ids=lambda c: c.title if c.title else repr(c.inputs.get("show_lines")),
)
def test_do_validate(
    case: _TestCase,
    highlight_validator_mock: mock.MagicMock,  # pylint: disable=redefined-outer-name
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test valid initializations succeed."""
    language = "xxx"
    attrs = {"blah": "bleh"}
    md = mock.MagicMock(spec=markdown.Markdown)
    show_lines_input = case.inputs.get("show_lines")
    assert do_validate(language, case.inputs, case.options, attrs, md)
    highlight_validator_mock.assert_called_once_with(
        language, case.inputs, case.expected_options, attrs, md
    )
    if case.expected_warnings:
        assert show_lines_input is not None
        prefix = (
            f"Invalid `show_lines` option in {show_lines_input!r}, some lines will "
            "not be filtered: "
        )
        assert [prefix + warn for warn in case.expected_warnings] == [
            r.message for r in caplog.records
        ]
