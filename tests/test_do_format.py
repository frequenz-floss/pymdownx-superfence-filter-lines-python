# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Tests for the do_format() function."""

import dataclasses
from typing import Iterator
from unittest import mock

import pytest
from pymdownx.superfences import SuperFencesBlockPreprocessor

from frequenz.pymdownx.superfences.filter_lines import (
    LinesRange,
    LinesRanges,
    Options,
    do_format,
)


@pytest.fixture
def md_mock() -> Iterator[mock.MagicMock]:
    """Mock the `md` object."""
    md = mock.MagicMock()
    preprocessor = mock.MagicMock(spec=SuperFencesBlockPreprocessor)
    preprocessor.highlight.return_value = True
    preprocessors = {"fenced_code_block": preprocessor}
    md.preprocessors.__getitem__.side_effect = preprocessors.__getitem__
    yield md


_SOURCE = """\
1. This is some text
2. which has multiple lines
3. and we want to filter some of them
4. we number them
5. so we can see which ones are filtered
6. and which ones are not
7. and we can also filter multiple ranges
"""


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TestCase:
    title: str | None = None
    options: Options = dataclasses.field(
        # We can't use just `Options` because `mypy` complains about type
        # incompatibility, which is not true.
        default_factory=lambda: Options()  # pylint: disable=unnecessary-lambda
    )
    expected_src: str


_cases = [
    _TestCase(title="No options", expected_src=_SOURCE),
    _TestCase(
        title="First line",
        options=Options(show_lines=LinesRanges({LinesRange(start=1, end=1)})),
        expected_src="""\
1. This is some text
""",
    ),
    _TestCase(
        title="Middle line",
        options=Options(show_lines=LinesRanges({LinesRange(start=3, end=3)})),
        expected_src="""\
3. and we want to filter some of them
""",
    ),
    _TestCase(
        title="Last line",
        options=Options(show_lines=LinesRanges({LinesRange(start=7, end=7)})),
        expected_src="""\
7. and we can also filter multiple ranges
""",
    ),
    _TestCase(
        title="Open range from the start",
        options=Options(show_lines=LinesRanges({LinesRange(start=1)})),
        expected_src=_SOURCE,
    ),
    _TestCase(
        title="Open range until the end",
        options=Options(show_lines=LinesRanges({LinesRange(end=7)})),
        expected_src=_SOURCE,
    ),
    _TestCase(
        title="Open range with start in the middle",
        options=Options(show_lines=LinesRanges({LinesRange(start=3)})),
        expected_src="""\
3. and we want to filter some of them
4. we number them
5. so we can see which ones are filtered
6. and which ones are not
7. and we can also filter multiple ranges
""",
    ),
    _TestCase(
        title="Open range with end in the middle",
        options=Options(show_lines=LinesRanges({LinesRange(end=3)})),
        expected_src="""\
1. This is some text
2. which has multiple lines
3. and we want to filter some of them
""",
    ),
    # range with start and end in the middle
    _TestCase(
        title="Open range with start and end in the middle",
        options=Options(show_lines=LinesRanges({LinesRange(start=2, end=4)})),
        expected_src="""\
2. which has multiple lines
3. and we want to filter some of them
4. we number them
""",
    ),
    _TestCase(
        title="Multiple lines",
        options=Options(
            show_lines=LinesRanges(
                {
                    LinesRange(start=1, end=1),
                    LinesRange(start=3, end=3),
                    LinesRange(start=6, end=6),
                }
            )
        ),
        expected_src="""\
1. This is some text
3. and we want to filter some of them
6. and which ones are not
""",
    ),
    _TestCase(
        title="Multiple ranges",
        options=Options(
            show_lines=LinesRanges(
                {
                    LinesRange(end=2),
                    LinesRange(start=4, end=5),
                    LinesRange(start=6),
                }
            )
        ),
        expected_src="""\
1. This is some text
2. which has multiple lines
4. we number them
5. so we can see which ones are filtered
6. and which ones are not
7. and we can also filter multiple ranges
""",
    ),
    _TestCase(
        title="Multiple ranges with overlap",
        options=Options(
            show_lines=LinesRanges(
                {
                    LinesRange(end=2),
                    LinesRange(start=2, end=5),
                    LinesRange(start=4, end=6),
                    LinesRange(start=6),
                }
            )
        ),
        expected_src=_SOURCE,
    ),
    _TestCase(
        title="Multiple ranges and lines",
        options=Options(
            show_lines=LinesRanges(
                {
                    LinesRange(end=1),
                    LinesRange(start=4, end=4),
                    LinesRange(start=5, end=5),
                    LinesRange(start=7),
                }
            )
        ),
        expected_src="""\
1. This is some text
4. we number them
5. so we can see which ones are filtered
7. and we can also filter multiple ranges
""",
    ),
]


@pytest.mark.parametrize(
    "case", _cases, ids=lambda c: f"{c.title} ({c.options.get('show_lines')})"
)
def test_do_format(
    case: _TestCase,
    md_mock: mock.MagicMock,  # pylint: disable=redefined-outer-name
) -> None:
    """Test valid initializations succeed."""
    language = "xxx"
    class_name = "yyy"
    kwargs = {"kwarg": "test"}
    assert do_format(_SOURCE, language, class_name, case.options, md_mock, **kwargs)
    md_mock.preprocessors["fenced_code_block"].highlight.assert_called_once_with(
        src=case.expected_src,
        class_name=class_name,
        language=language,
        md=md_mock,
        options=case.options,
        **kwargs,
    )
