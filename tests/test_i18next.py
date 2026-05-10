import json
import random
import sys
from pathlib import Path

import pytest
from moz.l10n.formats import Format
from moz.l10n.model import (
    CatchallKey,
    Entry,
    Expression,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
    VariableRef,
)

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
from i18nxt_parse import COUNT, COUNT_DECLARATION, i18next_parse  # noqa: E402

DATA_DIR = Path(__file__).parent / 'data'


def test_simple():
    """Test the most basic strings."""
    expect_entries: list = [
        Entry(id=('nothing',), value=PatternMessage([''])),
        Entry(id=('simple1',), value=PatternMessage(['Das ist einfach!'])),
        Entry(id=('simple2',), value=PatternMessage(["C'est simple!"])),
        Entry(id=('simple3',), value=PatternMessage(["It's easy!"])),
    ]
    expect = Resource(format=Format.plain_json, sections=[Section(id=(), entries=expect_entries)])

    data_path = DATA_DIR / 'simple.json'
    for source in (data_path, str(data_path), data_path.read_text(), data_path.read_bytes()):
        assert expect == i18next_parse(source)


def test_interpolation():
    """Test basic string interpolation."""
    expect_entries: list = [
        Entry(
            id=('startWithVar',),
            value=PatternMessage(
                [Expression(VariableRef('greeting')), ', ', Expression(VariableRef('value')), '!']
            ),
        ),
        Entry(
            id=('varInMiddle',),
            value=PatternMessage(['My ', Expression(VariableRef('value')), ' is full of eels!']),
        ),
        Entry(
            id=('endingWithVar',),
            value=PatternMessage(
                ['My postillion has been struck by ', Expression(VariableRef('value'))]
            ),
        ),
        Entry(
            id=('onlyVars',),
            value=PatternMessage(
                [
                    Expression(VariableRef('x')),
                    Expression(VariableRef('y')),
                    Expression(VariableRef('z')),
                ]
            ),
        ),
        Entry(
            id=('unescaped',),
            value=PatternMessage(
                [
                    'L33t HTML C0D3 8Y ',
                    Expression(VariableRef('hacker')),
                    ': ',
                    Expression(VariableRef('code'), attributes={'unescaped': True}),
                ]
            ),
        ),
        Entry(
            id=('emptyVars',),
            value=PatternMessage(["What's up with {{}}, {{ }} or {{-}} or {{ -}}, {{- }}??"]),
        ),
    ]
    expect = Resource(format=Format.plain_json, sections=[Section(id=(), entries=expect_entries)])

    data_path = DATA_DIR / 'interpolation.json'
    for source in (data_path, str(data_path), data_path.read_text(), data_path.read_bytes()):
        assert expect == i18next_parse(source)


def test_plurals():
    """Test the six possible plural identifiers."""
    variants: dict = {
        ('zero',): ['No ducks!'],
        ('one',): ['One duck!'],
        ('two',): ['Two ducks!'],
        ('few',): ['A couple ducks!'],
        ('many',): ['Loads of ducks!'],
        (CatchallKey('other'),): [Expression(VariableRef(COUNT)), ' ducks!'],
    }
    expect_entries: list = [
        Entry(
            id=('plural',),
            value=SelectMessage(
                declarations=COUNT_DECLARATION, selectors=(VariableRef(COUNT),), variants=variants
            ),
        )
    ]
    expect = Resource(format=Format.plain_json, sections=[Section(id=(), entries=expect_entries)])

    data_path = DATA_DIR / 'plurals.json'
    for source in (data_path, str(data_path), data_path.read_text(), data_path.read_bytes()):
        assert expect == i18next_parse(source)


def test_plural_order_invariant():
    """Test plural variants can appear in any order."""
    data_path = DATA_DIR / 'plurals.json'
    data = json.loads(data_path.read_text())
    items = list(data.items())

    expected = i18next_parse(data_path)

    for _ in range(5):
        random.shuffle(items)
        shuffled = json.dumps(dict(items))
        assert i18next_parse(shuffled) == expected


if __name__ == '__main__':
    pytest.main([__file__, '-vv'])
