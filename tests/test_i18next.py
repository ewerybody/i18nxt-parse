import pytest
import sys
from pathlib import Path

from moz.l10n.model import (
    Resource,
    Section,
    Entry,
    PatternMessage,
    VariableRef,
    Expression,
)
from moz.l10n.formats import Format

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
from i18nxt_parse import i18next_parse  # noqa: E402


DATA_DIR = Path(__file__).parent / 'data'


def test_simple():
    data_path = DATA_DIR / 'simple.json'
    result = i18next_parse(data_path)
    expect = Resource(
        format=Format.plain_json,
        sections=[
            Section(
                id=(),
                entries=[
                    Entry(
                        id=('simple1',),
                        value=PatternMessage(['Das ist einfach!']),
                    ),
                    Entry(
                        id=('simple2',),
                        value=PatternMessage(["C'est simple!"]),
                    ),
                    Entry(
                        id=('simple3',),
                        value=PatternMessage(["It's easy!"]),
                    ),
                ],
            )
        ],
    )
    assert result == expect


def test_interpolation():
    data_path = DATA_DIR / 'interpolation.json'
    result = i18next_parse(data_path)
    expect = Resource(
        format=Format.plain_json,
        sections=[
            Section(
                id=(),
                entries=[
                    Entry(
                        id=('interpolation1',),
                        value=PatternMessage(
                            [
                                Expression(VariableRef('greeting')),
                                ', ',
                                Expression(VariableRef('value')),
                                '!',
                            ]
                        ),
                    ),
                    Entry(
                        id=('interpolation2',),
                        value=PatternMessage(
                            [
                                'My ',
                                Expression(VariableRef('value')),
                                ' is full of eels!',
                            ]
                        ),
                    ),
                    Entry(
                        id=('interpolation3',),
                        value=PatternMessage(
                            [
                                'My postillion has been struck by ',
                                Expression(VariableRef('value')),
                            ]
                        ),
                    ),
                    Entry(
                        id=('interpolation4',),
                        value=PatternMessage(
                            [
                                Expression(VariableRef('x')),
                                Expression(VariableRef('y')),
                                Expression(VariableRef('z')),
                            ]
                        ),
                    ),
                ],
            )
        ],
    )
    assert result == expect


if __name__ == '__main__':
    pytest.main([__file__, '-vv'])
