import json
import random
import sys
import typing
from pathlib import Path
from importlib import import_module

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
from i18nxt_parse import COUNT, COUNT_DECLARATION, i18next_parse, DEFAULT_SECTION_NAME  # noqa: E402

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

    for source, section_name in _iter_source_variants(DATA_DIR / 'simple.json'):
        expect.sections[0].id = (section_name,)
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

    for source, section_name in _iter_source_variants(DATA_DIR / 'interpolation.json'):
        expect.sections[0].id = (section_name,)
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

    for source, section_name in _iter_source_variants(DATA_DIR / 'plurals.json'):
        expect.sections[0].id = (section_name,)
        assert expect == i18next_parse(source)


def test_plural_order_invariant():
    """Test plural variants can appear in any order."""
    data_path = DATA_DIR / 'plurals.json'
    data = json.loads(data_path.read_text())
    items = list(data.items())

    expected = i18next_parse(data_path)
    expected.sections[0].id = (DEFAULT_SECTION_NAME,)

    for _ in range(5):
        random.shuffle(items)
        shuffled = json.dumps(dict(items))
        assert i18next_parse(shuffled) == expected


def test_not_implemented():
    with pytest.raises(NotImplementedError):
        i18next_parse('{"notImplementedArray": ["not", "yet", "implemented"]}')

    with pytest.raises(NotImplementedError):
        i18next_parse('{"notImplementedObject": {"subKey": "subValue"}}')

    with pytest.raises(NotImplementedError):
        i18next_parse('{"key_context": "some value"}')

    with pytest.raises(NotImplementedError):
        i18next_parse('{"whichNumber_ordinal_one": "{{count}}st implement this!"}')

    with pytest.raises(NotImplementedError):
        i18next_parse('{"numItems_interval": "(1)[one item];(2-7)[a few items];"}')


def test_proper_errors():
    # should be strings only!
    with pytest.raises(TypeError):
        i18next_parse('{"keyWithNumber": 1337.42}')

    # should be either no underscore `key`, `key_context`/`key_plural` or `key_context_plural`
    with pytest.raises(ValueError):
        i18next_parse('{"key_with_many_underscores": "muppets"}')

    # implicit "one"
    with pytest.raises(ValueError):
        i18next_parse('{"alice": "Just {{count}} Bob!","alice_one": "Just another Bob!"}')


def test_serializing_to_mozl10n_formats():
    """Test serializing our generated Resources back to all of the moz-l10n formats.
    This is expected to not work on everything but some successful back serializations.
    """
    resources = {
        n: i18next_parse(DATA_DIR / f'{n}.json') for n in ('interpolation', 'plurals', 'simple')
    }
    report = {}
    for fmt in Format:
        try:
            serialize_module = import_module(f'moz.l10n.formats.{fmt.name}.serialize')
        except Exception as error:
            report[fmt.name] = f'ERROR: could not import {fmt.name}.serialize: {error}'
            continue

        try:
            serializer = getattr(serialize_module, f'{fmt.name}_serialize')
        except AttributeError:
            report[fmt.name] = f'ERROR: No "{fmt.name}_serialize" function!'
            continue

        report[fmt.name] = []
        for res_name, resource in resources.items():
            if fmt.name == 'inc':
                resource.sections[0].id = ()
            else:
                resource.sections[0].id = (res_name,)

            try:
                result = '\n'.join(serializer(resource))
            except Exception as error:
                report[fmt.name].append(
                    f'ERROR: could not serialize "{res_name}.json" with {fmt.name}.serialize: {error}'
                )
                continue

            assert isinstance(result, str)
            report[fmt.name].append(f'DONE: {res_name}')

    if all(isinstance(results, str) for results in report.values()):
        pytest.fail('None of the serializer modules could be imported!')

    if all(
        result.startswith('ERROR:')
        for results in report.values()
        for result in results
        if isinstance(results, list)
    ):
        pytest.fail('ALL serializers reported errors!')


def _iter_source_variants(data_path: Path) -> typing.Iterator[tuple[str | bytes | Path, str]]:
    """From given `Path` object iterate over `source` variants to yield to the parser."""
    yield data_path, data_path.stem

    yield str(data_path), data_path.stem

    yield data_path.read_text(), DEFAULT_SECTION_NAME

    yield data_path.read_bytes(), DEFAULT_SECTION_NAME


if __name__ == '__main__':
    pytest.main([__file__, '-vv'])
