import re
import json
from pathlib import Path

from moz.l10n.model import (
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


PLURALS = 'zero', 'one', 'two', 'few', 'many', 'other'
RE_INTERPOLATION = re.compile(r'\{\{(\w+)\}\}')


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

    data = json.loads(source)

    entries: list[Entry[Message] | Comment] = []
    for key, value in data.items():
        plural_keys = {}

        if '_' not in key:
            if '{{' not in value:
                entries.append(
                    Entry(
                        id=(key,),
                        value=PatternMessage([value]),
                    )
                )
                continue

            pattern: list[str | Expression | Markup] = []
            for i, part in enumerate(RE_INTERPOLATION.split(value)):
                if not part:
                    continue
                pattern.append(Expression(VariableRef(part)) if i % 2 else part)

            entries.append(
                Entry(
                    id=(key,),
                    value=PatternMessage(pattern),
                )
            )
        else:
            parts = key.split('_')

    return Resource(Format.plain_json, [Section((), entries)])


if __name__ == '__main__':
    import pytest
    import tests.test_i18next

    pytest.main([tests.test_i18next.__file__, '-v'])
