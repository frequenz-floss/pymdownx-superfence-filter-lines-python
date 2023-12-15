# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""A custom superfence for pymdown-extensions that can filters lines and plays nice with MkDocs."""

import dataclasses
import inspect
import logging
from typing import Any, NotRequired, Self, Set, TypedDict, cast

import markdown
from pymdownx.superfences import SuperFencesBlockPreprocessor, highlight_validator


@dataclasses.dataclass(frozen=True, kw_only=True)
class LinesRange:
    """A range of lines.

    `start` and `end` are inclusive and the indices start from 1.
    """

    start: int | None = None
    """Start line.

    `None` means the beginning of the file.
    """

    end: int | None = None
    """End line.

    `None` means the end of the file.
    """

    def __post_init__(self) -> None:
        """Validate inputs upon creation."""
        if self.start is None and self.end is None:
            raise ValueError("Cannot have both start and end as `None`")
        if self.start is not None and self.start < 1:
            raise ValueError("Start must be at least 1")
        if self.end is not None and self.end < 1:
            raise ValueError("End must be at least 1")
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("Start must be less than or equal to end")

    def __contains__(self, item: int) -> bool:
        """Whether the item is inside this range."""
        if self.start is None:
            assert self.end is not None
            return item <= self.end

        if self.end is None:
            return self.start <= item

        return self.start <= item <= self.end

    @classmethod
    def parse(cls, text: str) -> Self:
        """Create from a string.

        The string can be in the following formats:

        - `start`
        - `start:end`
        - `:end`
        - `start:`

        where `start` and `end` are integers.

        If `start` is empty, it is assumed to be 1.
        If `end` is empty, it is assumed to be the end of the file.
        If `start` appears without `:`, it is assumed to be both `start` and `end`.

        Lines are 1-indexed.

        Args:
            text: String to parse.

        Returns:
            The created range.

        Raises:
            ValueError: If the string is invalid.
        """
        splitted = text.split(":", 1)
        stripped = map(lambda s: s.strip(), splitted)
        match tuple(map(lambda s: s if s else None, stripped)):
            case (None,):
                raise ValueError("Empty start")
            case () | (None, None):
                raise ValueError("Both start and end are empty")
            case (str() as start,):
                return cls(start=int(start), end=int(start))
            case (str() as start, None):
                return cls(start=int(start))
            case (None, str() as end):
                return cls(end=int(end))
            case (str() as start, str() as end):
                return cls(start=int(start), end=int(end))
            case _ as invalid:
                raise ValueError(f"Invalid: {invalid!r}")

    def __str__(self) -> str:
        """Get the string representation."""
        if self.start is None:
            assert self.end is not None
            return f":{self.end}"
        if self.end is None:
            return f"{self.start}:"
        return f"{self.start}:{self.end}"


@dataclasses.dataclass(frozen=True)
class LinesRanges:
    """A set of line ranges."""

    ranges: Set[LinesRange]
    """The lines ranges."""

    def __post_init__(self) -> None:
        """Validate."""
        if not self.ranges:
            raise ValueError("Cannot have empty ranges")

    def __contains__(self, item: int) -> bool:
        """Whether the item is inside any of the ranges."""
        return any(item in r for r in self.ranges)

    @classmethod
    def parse(cls, text: str) -> tuple[Self | None, list[ValueError]]:
        """Create from a string.

        The string must be a comma-separated list of ranges, where each range is in the
        format described in
        [`LinesRange.parse`][pymdownx_superfence_filter_lines.LinesRange.parse].

        If no ranges are given, `None` is returned. If any ranges are invalid, they are
        ignored and a list of errors is returned.

        Args:
            text: String to parse.

        Returns:
            The created ranges, or `None` if no ranges are given, plus a list of errors,
                if any.
        """
        ranges: set[LinesRange] = set()
        errors: list[ValueError] = []
        for n, range_str in enumerate(text.split(","), start=1):
            try:
                lines_range = LinesRange.parse(range_str.strip())
            except ValueError as exc:
                error = ValueError(f"Range {n} ({range_str!r}) is invalid: {exc}")
                error.__cause__ = exc
                errors.append(error)
                continue
            ranges.add(lines_range)
        return cls(ranges) if ranges else None, errors

    def __str__(self) -> str:
        """Get the string representation."""
        return ",".join(map(str, self.ranges))


class Inputs(TypedDict):
    """Raw input options before they are validated."""

    show_lines: NotRequired[str]
    """Lines to show option."""


class Options(TypedDict):
    """Raw options before they are validated."""

    show_lines: NotRequired[LinesRanges]
    """Lines to show."""


def do_validate(
    language: str,
    inputs: Inputs,
    options: Options,
    attrs: dict[str, Any],
    md: markdown.Markdown,
) -> bool:
    """Validate the inputs."""
    # Parse `show_lines` option
    if show_lines_option := inputs.get("show_lines"):
        lines_ranges, errors = LinesRanges.parse(show_lines_option)

        for error in errors:
            _warn(
                "Invalid `show_lines` option in %r, some lines will not be filtered: %s",
                show_lines_option,
                error,
            )

        if lines_ranges:
            options["show_lines"] = lines_ranges

        # Remove handled option from inputs
        del inputs["show_lines"]

    # Run default validator
    return cast(bool, highlight_validator(language, inputs, options, attrs, md))


def do_format(
    src: str,
    language: str,
    class_name: str,
    options: Options,
    md: markdown.Markdown,
    **kwargs: Any,
) -> Any:
    """Filter the lines and run the default highlighter."""
    # Filter the lines to show
    if show_lines := options.get("show_lines"):
        lines = []
        for n, line in enumerate(src.splitlines(keepends=True), 1):
            if n in show_lines:
                lines.append(line)
        src = "".join(lines)

    # Run through default highlighter
    fenced_code_block = md.preprocessors["fenced_code_block"]
    assert isinstance(fenced_code_block, SuperFencesBlockPreprocessor)
    return fenced_code_block.highlight(
        src=src,
        class_name=class_name,
        language=language,
        md=md,
        options=options,
        **kwargs,
    )


def _warn(msg: str, /, *args: Any, **kwargs: Any) -> None:
    """Emit a warning.

    We do a bit of a hack to determine if we are running inside MkDocs or not, and if we are
    then we use the MkDocs logger, so warnings are shown in the MkDocs output with special
    formatting and also are detected as such when running in *strict* mode.

    If we are not running inside MkDocs, then we use the logger for this module.

    Args:
        msg: Message to emit.
        *args: Arguments to format the message with.
        **kwargs: Keyword arguments to format the message with.
    """
    _warn_logger.warning(msg, *args, **kwargs)


def _get_warn_logger() -> logging.Logger:
    """Get the logger to use for warnings."""
    if _is_running_inside_mkdocs():
        return logging.getLogger("mkdocs")
    return logging.getLogger(__name__)


def _is_running_inside_mkdocs() -> bool:
    """Whether we are running inside MkDocs or not."""
    for frame_record in inspect.stack():
        frame = frame_record.frame
        module = inspect.getmodule(frame)
        if module is not None:
            # Check if the module's name is associated with MkDocs
            if module.__name__.startswith("mkdocs."):
                return True
    return False


_warn_logger: logging.Logger = _get_warn_logger()
"""The logger to use for warnings."""
