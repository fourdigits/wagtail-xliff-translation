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
