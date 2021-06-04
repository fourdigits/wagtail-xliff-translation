import factory

from django.utils.translation import get_language

from wagtail.core.models import Locale


class LocaleFactory(factory.django.DjangoModelFactory):
    language_code = factory.LazyFunction(get_language)

    class Meta:
        model = Locale
        django_get_or_create = ("language_code",)
