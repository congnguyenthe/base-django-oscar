from django.apps import apps
from django.conf.urls import include, url
from django.utils.translation import gettext_lazy as _

from oscar.core.application import OscarConfig
from oscar.core.loading import get_class


class CatalogueOnlyConfig(OscarConfig):
    label = 'catalogue'
    name = 'oscar.apps.catalogue'
    verbose_name = _('Catalogue')

    namespace = 'catalogue'

    def ready(self):
        from . import receivers  # noqa

        super().ready()

        self.detail_view = get_class('catalogue.views', 'ProductDetailView')
        self.catalogue_view = get_class('catalogue.views', 'CatalogueView')
        self.category_view = get_class('catalogue.views', 'ProductCategoryView')
        self.range_view = get_class('offer.views', 'RangeDetailView')

        self.product_create_view = get_class('catalogue.views', 'ProductCreateView')
        self.product_update_view = get_class('catalogue.views', 'ProductUpdateView')
        self.product_layout_view = get_class('catalogue.views', 'ProductLayoutView')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^$', self.catalogue_view.as_view(), name='index'),
            url(r'^create/$', self.product_create_view.as_view(), name='create'),
            url(r'^layout/$', self.product_layout_view.as_view(), name='layout'),
            url(r'^update/$', self.product_update_view.as_view(), name='update'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_view.as_view(), name='detail'),
            url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                self.category_view.as_view(), name='category'),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range'),
        ]
        return self.post_process_urls(urls)


class CatalogueReviewsOnlyConfig(OscarConfig):
    label = 'catalogue'
    name = 'oscar.apps.catalogue'
    verbose_name = _('Catalogue')

    def ready(self):
        from . import receivers  # noqa

        super().ready()

        self.reviews_app = apps.get_app_config('reviews')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/reviews/',
                include(self.reviews_app.urls[0])),
        ]
        return self.post_process_urls(urls)


class CatalogueConfig(CatalogueOnlyConfig, CatalogueReviewsOnlyConfig):
    """
    Composite class combining Products with Reviews
    """
