# Development

Install this package in development mode:

```shell
git clone git@github.com:fourdigits/wagtail-xliff-translation.git
cd wagtail-xliff-translation
```

With your preferred virtualenv activated, install the package in development mode with the included testing and documentation dependencies:

```shell
python -m pip install -e '.[test,docs]' -U
```

## Tests

Run tests:

```shell
pytest
```

The test app can be managed (runserver, makemigrations, etc):

```shell
python manage.py makemigrations test_app
```

## Documentation

Run the documentation locally:

```shell
mkdocs serve
```

Deploy the documentation to Github pages:

```shell
mkdocs gh-deploy
```

See [https://fourdigits.github.io/wagtail-xliff-translation/](https://fourdigits.github.io/wagtail-xliff-translation/)


## Release Process

### Pre release

- Update CONTRIBUTORS.rst if necessary
- Update CHANGELOG.txt
- Update `version = <MAJOR>.<MINOR>.<PATCH>` in `setup.cfg`
- Everything is committed, clean checkout

### Release

With an active virtual environment:

```shell
pytest
git tag -a <MAJOR>.<MINOR>.<PATCH> -m "<message>"
git push --tags
python -m pip install --upgrade build
python -m build
python -m pip install --upgrade twine
python -m twine upload --repository pypi dist/*
```

### Post release

- Add new header `<MAJOR>.<MINOR>.<PATCH> - IN DEVELOPMENT` to CHANGELOG.txt. Increment the MINOR +1.
- Commit with the message `Back to development` and push.
- Update the docs `mkdocs gh-deploy`.
- Do promotion: blog, tweet, Wagtail Slack #twiw.
