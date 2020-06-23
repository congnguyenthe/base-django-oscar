from django.contrib import messages
from django.core.paginator import InvalidPage
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, TemplateView

from oscar.apps.catalogue.signals import product_viewed
from oscar.core.loading import get_class, get_model

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')
get_product_search_handler_class = get_class(
            'catalogue.search_handlers', 'get_product_search_handler_class')

Homepage = get_model('homepage', 'HomePage')

class HomepageView(TemplateView):
    model = Homepage
    template_name  = 'oscar/homepage/index.html'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        try:
            self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [])
        except InvalidPage:
            # Redirect to page one.
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:index')
        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['summary'] = _("All questions")
        search_context = self.search_handler.get_search_context_data(self.context_object_name)
        ctx.update(search_context)
        return ctx
