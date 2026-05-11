# **i18nxt-parse** - a parser for moz-l10n

Welcome! This is a little demo project to implement a parser from [the **i18next JSON V4** format](https://www.i18next.com/misc/json-format#i18next-json-v4) to [the **moz-l10n** Python library](https://github.com/mozilla/moz-l10n/tree/main/python#mozl10n).

## How to prepare

* get the **project files**
  * via git `git clone https://github.com/ewerybody/i18nxt-parse.git` or
  * download and extract [the zip file](https://github.com/ewerybody/i18nxt-parse/archive/refs/heads/main.zip) or
  * on [the github-repository](https://github.com/ewerybody/i18nxt-parse) press the <kbd style="color: #fff; background: #29903B"><> Code ⮟</kbd> button and hit **🖳 Open with GitHub Desktop**

* Make sure you **have `uv` available**: [docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/#installing-uv)

## How to use

#### In your Terminal
* `cd i18nxt-parse` to go **into your local `i18nxt-parse` directory**
* `uv sync` to prepare the **python environment**
* `uv run pytest -vv` to run the **unit tests**

#### in Python code

```py
from moz.l10n.model import Resource
from i18nxt_parse import i18next_parse

resource: Resource = i18next_parse('/path/to/translation.json')
```

## About this

So far **moz-l10n** [implements parsers & serializers for these formats](https://github.com/mozilla/moz-l10n/tree/main/python/moz/l10n/formats): `android, dtd, fluent, gettext, inc, ini, plain_json, properties, webext, xliff`. All have varying capabilities. That's no different for **i18next**.\
While **moz-l10n** aims to cover a widest range of localization features there are things that can not be translated from [i18next like arrays](https://www.i18next.com/translation-function/objects-and-arrays#arrays).

It's not the aim of this demo project to represent all i18next features with the moz-l10n data model though. A small set of features was chosen to be supported so far:

* [x] parsing source data directly from `str`, `bytes` and from loading files via `str` paths and `Path` objects.
* [x] key ordering preserved from source
* [x] basic key-value pairs
* [x] string interpolation with `{{someValue}}` pattern
  * [x] unescaped interpolation `{{- value}}`
  * [x] malformed tags `{{}}`, `{{- }}` preserved as literal strings
* [x] the 6 plural forms `zero, one, two, few, many, other` with optional [interpolation via `{{count}}` variable](https://www.i18next.com/translation-function/plurals).
    * [x] plural forms parsing in any order
    * [x] implicit singular from "bare" `key` treated as `one` when `key_other` exists ([see](https://www.i18next.com/translation-function/nesting#passing-options-to-nestings))
* [x] validation for yet unsupported features (arrays, objects, `$t` nesting, contexts)

What's NOT yet available is:
* [ ] [interpolation with formatting](https://www.i18next.com/translation-function/formatting)
* [ ] [objects & arrays](https://www.i18next.com/translation-function/objects-and-arrays)
* [ ] [nesting](https://www.i18next.com/translation-function/nesting) with `$t` references
* [ ] [ordinal plurals](https://www.i18next.com/translation-function/plurals#ordinal-plurals)
* [ ] [interval plurals](https://www.i18next.com/translation-function/plurals#interval-plurals)
* [x] extraction of contexts
  * [ ] *[selection by context](https://www.i18next.com/translation-function/context) (it's gathered internally but not yet presented with moz-l10n `SelectMessage`)
  * [ ] gender context (`key_female`/`key_male`)
  * [ ] context+plural combination (`key_female_one`, `key_male_other` ...) (though the proper order is taken care of)
* [ ] [support for additional interpolation options](https://www.i18next.com/translation-function/interpolation#additional-options) like configurable interpolation delimiters other than `{{}}`
* [ ] and finally: No **Serialization** yet!


## Limitations

This is a demo project with no intentions to be 100% correct, super performant or complete in feature or test coverage.

Critique, reports & ideas are very welcome! 🙇

See the [`LICENSE`](https://github.com/ewerybody/i18nxt-parse/blob/main/LICENSE) for more.
