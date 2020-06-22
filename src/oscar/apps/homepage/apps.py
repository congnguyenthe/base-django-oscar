from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

from oscar.core.application import OscarConfig
from oscar.core.loading import get_class


class HomepageConfig(OscarConfig):
    label = 'homepage'
    name = 'oscar.apps.homepage'
    verbose_name = _('Homepage')

    namespace = 'homepage'

    def ready(self):
        self.summary_view = get_class('homepage.views', 'HomepageView')

    def get_urls(self):
        urls = [
            url(r'^$', self.summary_view.as_view(), name='summary'),
        ]
        return self.post_process_urls(urls)
