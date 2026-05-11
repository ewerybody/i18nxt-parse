import json
import re
from pathlib import Path

from moz.l10n.model import (
    CatchallKey,
    Comment,
    Entry,
    Expression,
    Format,
    Markup,
    Message,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
    VariableRef,
)

OTHER = 'other'
PLURALS = 'zero', 'one', 'two', 'few', 'many', OTHER
RE_INTERPOLATION = re.compile(r'\{\{(-\s*)?(\w+)\}\}')
"""Regex pattern for splitting into text, dash, varname."""

# plural interpolation has to happen with {{count}}! See:
# https://www.i18next.com/translation-function/plurals
COUNT = 'count'
COUNT_DECLARATION = {COUNT: Expression(VariableRef(COUNT), 'number')}


def i18next_parse(source: str | bytes | Path) -> Resource:
    """
    Parse i18next V4 data from string, bytes or given path into message resource.
    """
    if isinstance(source, bytes):
        source = str(source, 'utf8')
    elif isinstance(source, Path):
        source = source.read_text()
    else:
        source_path = Path(source)
        if source_path.is_file():
            source = source_path.read_text()

    # first pass, gather keys split by _ into key, context, plural. No _ no context ('')!
    keys: dict[str, dict[str, dict[str, str]]] = {}
    """Dictionary of keys[context[plural, value]]"""
    for key, value in json.loads(source).items():
        if isinstance(value, (list, dict)):
            raise NotImplementedError('So far there is no support for arrays and nesting!')

        if not isinstance(value, str):
            raise TypeError(f'Wrong value type! No support for {type(value)}')

        if '_' not in key:
            keys.setdefault(key, {}).setdefault('', {})[''] = value
            continue

        key, *parts = key.split('_')
        if len(parts) > 2:
            raise ValueError(
                'Unsupported amount of parts in key! '
                'Can be either "key", "key_contexy/plural" or "key_context_plural"'
            )

        # plural suffixes always come last. See:
        # https://www.i18next.com/translation-function/context#combining-with-plurals
        if parts[-1] in PLURALS:
            plural = parts[-1]
            context = parts[0] if len(parts) == 2 else ''
        else:
            plural = ''
            context = parts[0] if len(parts) == 1 else ''
        keys.setdefault(key, {}).setdefault(context, {})[plural] = value

    entries: list[Entry[Message] | Comment] = []
    for key, contexts in keys.items():
        for context, plurals in contexts.items():
            if context == 'ordinal':
                # TODO: https://www.i18next.com/translation-function/plurals#ordinal-plurals
                raise NotImplementedError('Support for Ordinal plurals is not yet implemented!')
            if context == 'interval':
                # TODO: https://www.i18next.com/translation-function/plurals#interval-plurals
                raise NotImplementedError('Support for Interval plurals is not yet implemented!')
            if context != '':
                raise NotImplementedError('No support yet for other than default contexts ("")!')

            if len(plurals) == 1 and '' in plurals:
                entries.append(
                    Entry(id=(key,), value=PatternMessage(_get_pattern_list(plurals[''])))
                )
                continue

            # Apparently bare keys could act as 'one' if other plurals exist:
            # https://www.i18next.com/translation-function/nesting#passing-options-to-nestings
            if '' in plurals:
                if 'one' in plurals:
                    raise ValueError('Bare key cannot be "one" if that already exists!')
                plurals['one'] = plurals['']
                del plurals['']

            variants: dict = {
                (p,) if p != 'other' else (CatchallKey('other'),): _get_pattern_list(plurals[p])
                for p in PLURALS
                if p in plurals
            }
            msg = SelectMessage(
                declarations=COUNT_DECLARATION,
                selectors=(VariableRef(COUNT),),
                variants=variants,
            )
            entries.append(Entry(id=(key,), value=msg))

    return Resource(Format.plain_json, [Section((), entries)])


def _get_pattern_list(value: str) -> list[str | Expression | Markup]:
    if '{{' not in value:
        return [value]

    pattern: list[str | Expression | Markup] = []
    parts = RE_INTERPOLATION.split(value)
    for text, dash, var_name in zip(parts[::3], parts[1::3], parts[2::3]):
        if text:
            pattern.append(text)
        if dash:
            pattern.append(Expression(VariableRef(var_name), attributes={'unescaped': True}))
        else:
            pattern.append(Expression(VariableRef(var_name)))
    # check for trailing text that the zip might have omitted:
    if len(parts) % 3 and parts[-1]:
        pattern.append(parts[-1])

    return pattern


if __name__ == '__main__':
    import pytest

    import tests.test_i18next

    pytest.main([tests.test_i18next.__file__, '-v'])
