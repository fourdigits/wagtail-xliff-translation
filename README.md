# wagtail-xliff-translation

_Wagtail XLIFF Translation_ is a Wagtail library for converting a Wagtail website to XLIFF (XML Localization Interchange File Format) and back.
It allows translators to work with -XLIFF based- translation software.

Exporting and importing a sub-tree, or a single page is supported.

## Documentation

https://fourdigits.github.io/wagtail-xliff-translation/

## Tests

To run the tests, checkout the repository and run:

```shell
pytest
```

## Release Process

Checklist:

- Update CONTRIBUTORS.rst if necessary
- Update CHANGELOG.txt
- Everything is commited, clean checkout

With an active virtual environment

```shell
pytest
git tag -a <MAJOR>.<MINOR>.<PATCH> -m "<message>"
git push --tags
python -m pip install --upgrade build
python -m build
python -m pip install --upgrade twine
python -m twine upload --repository pypi dist/*
```

## Powered by Four Digits

We love code: https://fourdigits.nl/en/
