# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Tests for the LinesRange class."""

import dataclasses

import pytest

from frequenz.pymdownx.superfences.filter_lines import LinesRange


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ValidInitTestCase:  # pylint: disable=too-many-instance-attributes
    title: str
    start: int | None = None
    end: int | None = None
    expected: LinesRange | None


_valid_init_test_cases = [
    _ValidInitTestCase(title="No end", start=1, expected=LinesRange(start=1)),
    _ValidInitTestCase(title="No start", end=1, expected=LinesRange(end=1)),
    _ValidInitTestCase(
        title="Start and end", start=1, end=2, expected=LinesRange(start=1, end=2)
    ),
    _ValidInitTestCase(
        title="start == end", start=1, end=1, expected=LinesRange(start=1, end=1)
    ),
]


@pytest.mark.parametrize("case", _valid_init_test_cases, ids=lambda c: c.title)
def test_valid_init(case: _ValidInitTestCase) -> None:
    """Test valid initializations succeed."""
    assert LinesRange(start=case.start, end=case.end) == case.expected


@dataclasses.dataclass(frozen=True, kw_only=True)
class _InvalidInitTestCase:  # pylint: disable=too-many-instance-attributes
    title: str
    start: int | None = None
    end: int | None = None
    expected: ValueError


_invalid_init_test_cases = [
    _InvalidInitTestCase(
        title="Empty start and end",
        expected=ValueError("Cannot have both start and end as `None`"),
    ),
    _InvalidInitTestCase(
        title="start=0", start=0, expected=ValueError("Start must be at least 1")
    ),
    _InvalidInitTestCase(
        title="Negative start",
        start=-1,
        expected=ValueError("Start must be at least 1"),
    ),
    _InvalidInitTestCase(
        title="end=0", end=0, expected=ValueError("End must be at least 1")
    ),
    _InvalidInitTestCase(
        title="Negative end", end=-1, expected=ValueError("End must be at least 1")
    ),
    _InvalidInitTestCase(
        title="start > end",
        start=2,
        end=1,
        expected=ValueError("Start must be less than or equal to end"),
    ),
]


@pytest.mark.parametrize("case", _invalid_init_test_cases, ids=lambda c: c.title)
def test_invalid_init(case: _InvalidInitTestCase) -> None:  # TODO(cookiecutter): Remove
    """Test invalid initializations fail."""
    with pytest.raises(ValueError) as excinfo:
        LinesRange(start=case.start, end=case.end)
    assert str(excinfo.value) == str(case.expected)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ContainsTestCase:
    title: str
    lines_range: LinesRange
    item: int
    expected: bool


_contains_test_cases = [
    _ContainsTestCase(
        title="Start only, included",
        lines_range=LinesRange(start=1),
        item=1,
        expected=True,
    ),
    _ContainsTestCase(
        title="End only, included",
        lines_range=LinesRange(end=1),
        item=1,
        expected=True,
    ),
    _ContainsTestCase(
        title="Start and end the same, included",
        lines_range=LinesRange(start=1, end=1),
        item=1,
        expected=True,
    ),
    _ContainsTestCase(
        title="Start and end different, included",
        lines_range=LinesRange(start=1, end=2),
        item=2,
        expected=True,
    ),
    _ContainsTestCase(
        title="Start only, not included",
        lines_range=LinesRange(start=2),
        item=1,
        expected=False,
    ),
    _ContainsTestCase(
        title="End only, not included",
        lines_range=LinesRange(end=1),
        item=2,
        expected=False,
    ),
    _ContainsTestCase(
        title="Start and end the same, not included",
        lines_range=LinesRange(start=1, end=1),
        item=2,
        expected=False,
    ),
    _ContainsTestCase(
        title="Start and end different, not included",
        lines_range=LinesRange(start=1, end=2),
        item=3,
        expected=False,
    ),
]


@pytest.mark.parametrize("case", _contains_test_cases, ids=lambda c: c.title)
def test_contains(case: _ContainsTestCase) -> None:
    """Test that the __contains__ method works."""
    assert (case.item in case.lines_range) == case.expected


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ValidFromStrTestCase:
    title: str
    text: str
    expected: LinesRange


_from_str_test_cases = [
    _ValidFromStrTestCase(
        title="Line only", text="1", expected=LinesRange(start=1, end=1)
    ),
    _ValidFromStrTestCase(title="Start only", text="1:", expected=LinesRange(start=1)),
    _ValidFromStrTestCase(title="End only", text=":1", expected=LinesRange(end=1)),
    _ValidFromStrTestCase(
        title="Start and end the same", text="1:1", expected=LinesRange(start=1, end=1)
    ),
    _ValidFromStrTestCase(
        title="Start and end different", text="1:2", expected=LinesRange(start=1, end=2)
    ),
]


@pytest.mark.parametrize("case", _from_str_test_cases, ids=lambda c: c.title)
def test_from_str(case: _ValidFromStrTestCase) -> None:
    """Test that the parse method works."""
    assert LinesRange.parse(case.text) == case.expected
