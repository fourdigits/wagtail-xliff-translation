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
- Nested StreamBlocks are known to cause issues since their database values are not correct. We've been able to make it work to 3 levels of nesting, however they seem to fail after that. The page will be created but cause errors when you try to edit the page and will probably also cause errors when using the pages in a frontend.

## Installation

To install:

```shell
pip install wagtail-xliff-translation
```

In settings.py:

- Add `'wagtail_xliff_translation'` to `INSTALLED_APPS`.
- Add `'SERIALIZATION_MODULES = {"xliff": "wagtail_xliff_translation.serializers"}'` setting.

Like so:

```django
# settings.py

INSTALLED_APPS = [
    'wagtail_xliff_translation',
    ...
]

SERIALIZATION_MODULES = {"xliff": "wagtail_xliff_translation.serializers"}
```
