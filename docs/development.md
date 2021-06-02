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

Run tests:

```shell
pytest
```

The test app can be managed (runserver, makemigrations, etc):

```shell
python manage.py makemigrations test_app
```

## Deploy docs

Deploy docs to Github pages:

```shell
mkdocs gh-deploy
```

Check https://fourdigits.github.io/wagtail-xliff-translation/
