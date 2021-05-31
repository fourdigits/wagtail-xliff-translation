# Wagtail XLIFF Translation

*Wagtail XLIFF Translation* is a Wagtail library for converting a Wagtail website to XLIFF (XML Localization Interchange File Format) and back. 
It allows translators to work with -XLIFF based- translation software. 

## What does it do?

Wagtail XLIFF Translation provides a download view in the Wagtail admin to export site contents to XLIFF file. 
Once the file is translated, it can be uploaded to create a translated site tree.

Exporting and importing a sub-tree, or a single page is supported.

## Known limitations

- Related objects (such as images, documents, and snippets) are not translated or duplicated.
- Pages will be in draft mode. Pages need to be reviewed and published.
- ...

## Installation

To install:

```shell
pip install wagtail-xliff-translation
```

Add `'wagtail-xliff-translation'` to your project's `INSTALLED_APPS`.
