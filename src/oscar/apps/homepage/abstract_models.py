import csv
import itertools
import operator
from decimal import Decimal as D
from decimal import ROUND_DOWN

from django.conf import settings
from django.core import exceptions
from django.db import models
from django.db.models.query import Q
from django.template.defaultfilters import date as date_filter
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import get_current_timezone, now
from django.utils.translation import gettext_lazy as _

class AbstractHomepage(models.Model):
    create = models.TextField(_('Create'), blank=True)
    browse = models.TextField(_('Browse'), blank=True)

    class Meta:
        abstract = True
        app_label = 'homepage'

