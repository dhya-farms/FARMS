# description :- Script gets the translation from translation service and updates po files.
# python manage.py make_translation_message  --locale  all
# python manage.py make_translation_message  --locale  pa bn en ta te ml mr kn gu hi
# --locale - 2 options - all for all the languages and particular languages also ex.as pa bn ...


import requests
from django.conf import settings
from django.core.management.base import BaseCommand, no_translations
from rest_framework import status


class Command(BaseCommand):
    help = "Make Messages from Translation service"

    def add_arguments(self, parser):
        parser.add_argument(
            '--locale',
            nargs='+',
            help='set locale(s) like "ta", "te"',
        )

    @no_translations
    def handle(self, *args, **options):
        locales = options['locale']
        translation_format = "po"
        url_template = "https://translation-service-dev.internal.getlokalapp.com/translations/translations/" \
                       "?locale={locale}&" \
                       "destination={destination}&" \
                       "format={format}"

        filepath = "locale/{locale}/LC_MESSAGES/django.po"
        destination = 68  # Destination for Real Estate coded in translation service

        if 'all' in locales:
            locales = [i[0] for i in settings.LANGUAGES]

        for locale in locales:
            try:
                url = url_template.format(locale=locale, destination=destination, format=translation_format)
                response = requests.get(url)
                if response.status_code == status.HTTP_200_OK:
                    with open(filepath.format(locale=locale), "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"{locale} - file updated")
                else:
                    print(f"translation api fails,for - ,{locale}, response_code: {response.status_code}, "
                          f"response_message: {response.text}")
            except Exception as e:
                print(f"{locale} - got error - {e}")
