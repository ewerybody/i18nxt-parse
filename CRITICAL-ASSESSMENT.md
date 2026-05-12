# Critical Assessment

## gettext parser does not work with PathLike objects
Seems all parsers only advertise `source: str | bytes` but due to passing to
other builtins might be much more capable which is not yet documented nor tested.
The `bytes` capability also seems untested atm? (https://github.com/mozilla/moz-l10n/issues/136)

## Readme has issues linking `Message` and `Resource`
The sub-readme that is! Right under the first couple lines: https://github.com/mozilla/moz-l10n/blob/main/python/README.md#mozl10n
`resource.py` and `message.py` don't exist no more?
* there could be a CI check for broken links.

## typing issue in Section, entries
It says `entries: list[Entry[V_co] | Comment]` and half the test is glowing like an xmax tree.

## mf2 serializer does not follow {format_name}_serialize pattern?
`Resource` is not even imported in the module? Although it's in the `moz.l10n.formats.Formats` enum?
But I understand. It's the foundational model for moz-l10n itself!


## sparse documentation about format features
To test my generated resources somewhat more thoroughly against code I didn't write myself I put togehter a little test that loops over available moz-i18n formats, imports their serialize module and passes each resource into it. So far these are the results

| Format | simple | i11n | plurals | notes |
|--------|--------|---------------|---------|-------|
| fluent | ✔️ | ✔️ | ✔️ | the **only** one working with all! |
| webext | ✔️ | ✔️ | ❌ | `Unsupported entry for plural` |
| dtd | ✔️ | ❌ | ❌ | `Unsupported message for startWithVar`, `Unsupported message for plural: SelectMessage(declarations={'count'` |
| gettext | ✔️ | ❌ | ❌ | `gettext.serialize: Value for ('startWithVar',) is not supported:`, `gettext.serialize: Value for ('plural',) is not supported` |
| ini | ✔️ | ❌ | ❌ | **needs** a named section, `Unsupported message for ('startWithVar'`, `Unsupported message for ('plural'` |
| plain_json | ✔️ | ❌ | ❌ | `plain_json.serialize: Unsupported message for "('startWithVar'`, `plain_json.serialize: Unsupported message for ('plural'` |
| properties | ✔️ | ❌ | ❌ | `properties.serialize: Error serializing startWithVar`, `properties.serialize: Error serializing plural` |
| inc | ✔️ | ❌ | ❌ | **rejects** named sections, `Unsupported message for startWithVar`, `Unsupported message for plural: SelectMessage(declarations={'count'` |
| android | ❌ | ❌ | ❌ | needs `lxml` / `moz.l10n[xml]` |
| xliff | ❌ | ❌ | ❌ | needs `lxml`/ `moz.l10n[xml]` |
| mf2 | ❌ | ❌ | ❌ | internal model, not a file format^ |

Although It's clearly documented that moz-l10n is primarily for **internal** Mozilla use I wish there would have been a more hands on approach to documenting the usage. I.e. the cherry on the pie would be:

`for each format:`
* in its folder have a `README.md` with
* this is what it's about
* here is a link to the docs
* `for each feature:`
  * this is how `feature` is done for example ...
  * this is how it's covered in **moz-l10n** ... or
  * this is why it **cannot** be covered ...
  * and for completeness `for each moz-l10n feature:`
    * this is how it's done in `format`
    * this is why it **cannot** be done

To be fair: There **are** some comprehensive docstrings in most of the `_parse` and `_serialize` functions but it might be more approachable.
