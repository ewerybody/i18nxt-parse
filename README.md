# **i18nxt-parse** - a wip parser for moz-l10n

Welcome! This is a little demo project to implement a parser from [the **i18next JSON V4** format]() to [the **moz-l10n** Python library](https://github.com/mozilla/moz-l10n/tree/main/python#mozl10n).

## How to

* get the **project files**
  * via git `git clone https://github.com/ewerybody/i18nxt-parse.git` or
  * download and extract [the zip file](https://github.com/ewerybody/i18nxt-parse/archive/refs/heads/main.zip) or
  * on [the github-repository](https://github.com/ewerybody/i18nxt-parse) press the <kbd style="color: #fff; background: #29903B"><> Code ⮟</kbd> button and hit **🖳 Open with GitHub Desktop** if that's your style

* go **into your local `i18nxt-parse` directory**
  * via commandline `cd i18nxt-parse`
  * or in your file browser

* Make sure you **have `uv` available**: [docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/#installing-uv)
  * `uv sync` to prepare the python environment
  * `uv run pytest -vv` to run the tests

## About this

So far **moz-l10n** implements parsers & serializers for these formats: `android, dtd, fluent, gettext, inc, ini, plain_json, properties, webext, xliff`. All have varying capabilities. That's no different for **i18next**.\
While **moz-l10n** aims to cover a widest range of localization features there are even things that can not be translated from [i18next like arrays](https://www.i18next.com/translation-function/objects-and-arrays#arrays).

It's not the aim of this demo project to represent all i18next features with the moz-l10n data model though. A small set of features was chosen to be supported so far:

* [x] parsing source data directly from `str`, `bytes` and from loading files via `str` paths and `Path` objects.
* [x] basic key-value pairs
* [x] string interpolation with `{{someValue}}` pattern
* [x] the 6 plural forms `zero, one, two, few, many, other` with optional [interpolation via `{{count}}` variable](https://www.i18next.com/translation-function/plurals).
* [x] extraction of contexts*

What's NOT yet available is:
* [ ] arrays
* [ ] objects
* [ ] nesting
* [ ] *selection by context (it's gathered internally but not yet presented with moz-l10n data model)
