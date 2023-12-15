# Frequenz Filter Lines Superfence

[![Build Status](https://github.com/frequenz-floss/pymdownx-superfence-filter-lines-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/pymdownx-superfence-filter-lines-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/pymdownx-superfence-filter-lines)](https://pypi.org/project/pymdownx-superfence-filter-lines/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/pymdownx-superfence-filter-lines-python/)

## Introduction

A custom superfence for pymdown-extensions that can filters lines and plays
nice with MkDocs.

This is particularly useful when you want to hide some comments or some
boilerplate code from the documentation for any reason.

A typical use case is when you are testing your examples in the documentation,
so you might need to add some initialization code, or importing some dependencies
that are not relevant for the point you are trying to make in the
documentation, but you still need the example code to work to make sure they are
not inadvertedly broken.

## Quick Example

When writing some documentation, and you want to show some code block, but
you want to show only some lines, you can use this superfence as follows:

~~~markdown
```text show_lines=":2,4,7,10:12,15:"
This is line 1
This is line 2
This is line 3
This is line 4
This is line 5
This is line 6
This is line 7
This is line 8
This is line 9
This is line 10
This is line 11
This is line 12
This is line 13
This is line 14
This is line 15
This is line 16
This is line 17
```
~~~

This will show the following block of code in the rendered output:

```text show_lines=":2,4,7,10:12,15:"
This is line 1
This is line 2
This is line 3
This is line 4
This is line 5
This is line 6
This is line 7
This is line 8
This is line 9
This is line 10
This is line 11
This is line 12
This is line 13
This is line 14
This is line 15
This is line 16
This is line 17
```

See [Usage](#usage) for a more detailed explanation of the available options.

## Configuration

### MkDocs

To use this superfence with [MkDocs](https://www.mkdocs.org/), you can use
something like this:

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: "*"
          class: "highlight"
          format: !!python/name:pymdownx_superfence_filter_lines.do_format
          validator: !!python/name:pymdownx_superfence_filter_lines.do_validate
```

### Standalone

To use this superfence standalone, you can use something like this:

```python
import markdown
from pymdownx_superfence_filter_lines import do_format, do_validate

html = markdown.markdown(
    markdown_source,
    extensions=['pymdownx.superfence'],
    extension_configs={
        "pymdownx.superfences": {
            "custom_fences": [
                {
                    'name': '*',
                    'class': 'highlight',
                    'validator': do_validate,
                    'format': do_format
                }
            ]
        }
    }
)

print(html)
```

## Usage

See [Quick Example](#quick-example) for an example.

The superfence supports the following options:

### `show_lines`

A comma separated list of line numbers or ranges of line numbers to show.

The line numbers are 1-based. If any line number is zero or negative, a warning
is logged and the line or range are ignored.

If `show_lines` is omitted, it defaults to showing all lines.

#### Ranges

Ranges are inclusive and are defined as follows:

* The ranges are specified as `start:end`, where `start` and `end` are the line
  numbers of the first and last lines to show, respectively.

* If `start` is omitted, it defaults to the first line. If `end` is omitted, it
  defaults to the last line.

* If `start` is greater than `end`, a warning is logged and the range is
  ignored.

* If `start` is greater than the number of lines in the code block, the range
  is ignored.

* If `end` is greater than the number of lines in the code block, it is set to
  the number of lines in the code block.

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
