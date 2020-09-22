import logging

from django.core.management.base import BaseCommand, CommandError

from oscar.core.loading import get_class
from oscar.apps.catalogue.categories import create_from_breadcrumbs

class Command(BaseCommand):
    def handle(self, *args, **options):
        categories = (
                'IT',
                'Japanese',
                'English > Grade > 8',
                'English > Grade > 9',
                'English > Grade > 10',
                'English > Grade > 11',
                'English > Grade > 12',

                'English > Level > A2',
                'English > Level > A1',
                'English > Level > B2',
                'English > Level > B1',
                'English > Level > C2',
                'English > Level > C1',

                'English > Certificate > IELTS',
                'English > Certificate > TOEFL',
                'English > Certificate > TOEIC',

                'English > Grammar > Reported Speech',
                'English > Grammar > Conditional',
                'English > Grammar > Relative Clauses',
                'English > Grammar > Adverbs',
                'English > Grammar > Adjectives',
                'English > Grammar > Nouns',
                'English > Grammar > Verbs',
                'English > Grammar > Passive Voice',
                'English > Grammar > Tenses',
                'English > Grammar > Articles',
                'English > Grammar > Word Order'
                )
        for breadcrumbs in categories:
            create_from_breadcrumbs(breadcrumbs)
