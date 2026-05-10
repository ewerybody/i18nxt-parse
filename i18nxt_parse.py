import re
import json
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
RE_INTERPOLATION = re.compile(r'\{\{(\w+)\}\}')

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
                    raise NotImplementedError('Bare key cannot be "one" if that already exists!')
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
    for i, part in enumerate(RE_INTERPOLATION.split(value)):
        if not part:
            continue
        # regex split puts our {{variables}} in the even spots all other in odds
        pattern.append(Expression(VariableRef(part)) if i % 2 else part)
    return pattern


if __name__ == '__main__':
    import pytest
    import tests.test_i18next

    pytest.main([tests.test_i18next.__file__, '-v'])
