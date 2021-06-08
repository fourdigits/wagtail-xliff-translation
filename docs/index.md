# Wagtail XLIFF Translation

_Wagtail XLIFF Translation_ is a Wagtail library for converting a Wagtail website to XLIFF (XML Localization Interchange File Format) and back.
It allows translators to work with -XLIFF based- translation software.

## What does it do?

Wagtail XLIFF Translation provides a download view in the Wagtail admin to export site contents to XLIFF file.
Once the file is translated, it can be uploaded to create a translated site tree.

Exporting and importing a sub-tree, or a single page is supported.

## Known limitations

- Related objects (such as images, documents, and snippets) are not translated or duplicated.
- Pages will be in draft mode. Pages need to be reviewed and published.
- Nested streamfield are known to cause issues since their database values are not correct. The page will be created but causes errors.

## Installation

To install:

```shell
pip install wagtail-xliff-translation
```

In settings.py:

- Add `'wagtail-xliff-translation'` to `INSTALLED_APPS`.
- Add `'SERIALIZATION_MODULES = {"xliff": "wagtail_xliff_translation.serializers"}'` setting.

Like so:

```django
# settings.py

INSTALLED_APPS = [
    'wagtail-xliff-translation',
    ...
]

SERIALIZATION_MODULES = {"xliff": "wagtail_xliff_translation.serializers"}
```
