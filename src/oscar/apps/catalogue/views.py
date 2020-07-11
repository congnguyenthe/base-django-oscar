from django.contrib import messages
from django.core.paginator import InvalidPage
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, TemplateView, View
from django.http import JsonResponse
from django.db.models import Q
from django.core import serializers

import json

from oscar.apps.catalogue.signals import product_viewed, product_updated
from oscar.core.loading import get_class, get_model

Product = get_model('catalogue', 'product')
ProductAttributeValue = get_model('catalogue', 'productattributevalue')
ProductAttribute = get_model('catalogue', 'productattribute')
ProductCategory = get_model('catalogue', 'productcategory')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')
ProductClass = get_class('catalogue.models', 'ProductClass')
Quiz = get_class('catalogue.models', 'Quiz')
QuizTemplate = get_class('catalogue.models', 'QuizTemplate')
get_product_search_handler_class = get_class(
    'catalogue.search_handlers', 'get_product_search_handler_class')


class ProductDetailView(DetailView):
    context_object_name = 'product'
    model = Product
    view_signal = product_viewed
    template_folder = "catalogue"

    # Whether to redirect to the URL with the right path
    enforce_paths = True

    # Whether to redirect child products to their parent's URL. If it's disabled,
    # we display variant product details on the separate page. Otherwise, details
    # displayed on parent product page.
    enforce_parent = False

    def get(self, request, **kwargs):
        """
        Ensures that the correct URL is used before rendering a response
        """
        self.object = product = self.get_object()

        redirect = self.redirect_if_necessary(request.path, product)
        if redirect is not None:
            return redirect

        # Do allow staff members so they can test layout etc.
        if not self.is_viewable(product, request):
            raise Http404()

        response = super().get(request, **kwargs)
        self.send_signal(request, response, product)
        return response

    def is_viewable(self, product, request):
        return product.is_public or request.user.is_staff

    def get_object(self, queryset=None):
        # Check if self.object is already set to prevent unnecessary DB calls
        if hasattr(self, 'object'):
            return self.object
        else:
            return super().get_object(queryset)

    def redirect_if_necessary(self, current_path, product):
        if self.enforce_parent and product.is_child:
            return HttpResponsePermanentRedirect(
                product.parent.get_absolute_url())

        if self.enforce_paths:
            expected_path = product.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['alert_form'] = self.get_alert_form()
        ctx['has_active_alert'] = self.get_alert_status()
        return ctx

    def get_alert_status(self):
        # Check if this user already have an alert for this product
        has_alert = False
        if self.request.user.is_authenticated:
            alerts = ProductAlert.objects.filter(
                product=self.object, user=self.request.user,
                status=ProductAlert.ACTIVE)
            has_alert = alerts.exists()
        return has_alert

    def get_alert_form(self):
        return ProductAlertForm(
            user=self.request.user, product=self.object)

    def send_signal(self, request, response, product):
        self.view_signal.send(
            sender=self, product=product, user=request.user, request=request,
            response=response)

    def get_template_names(self):
        """
        Return a list of possible templates.

        If an overriding class sets a template name, we use that. Otherwise,
        we try 2 options before defaulting to :file:`catalogue/detail.html`:

            1. :file:`detail-for-upc-{upc}.html`
            2. :file:`detail-for-class-{classname}.html`

        This allows alternative templates to be provided for a per-product
        and a per-item-class basis.
        """
        if self.template_name:
            return [self.template_name]

        return [
            'oscar/%s/detail-for-upc-%s.html' % (
                self.template_folder, self.object.upc),
            'oscar/%s/detail-for-class-%s.html' % (
                self.template_folder, self.object.get_product_class().slug),
            'oscar/%s/detail.html' % self.template_folder]


class CatalogueView(TemplateView):
    """
    Browse all products in the catalogue
    """
    context_object_name = "products"
    template_name = 'oscar/catalogue/browse.html'

    def get(self, request, *args, **kwargs):
        try:
            self.search_handler = self.get_search_handler(
                self.request.GET, request.get_full_path(), [])
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
        data = self.search_handler.get_queryset()
        data = data.filter(structure='standalone')
        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        search_context[self.context_object_name] = data
        ctx.update(search_context)
        return ctx


class ProductCategoryView(TemplateView):
    """
    Browse products in a given category
    """
    context_object_name = "questions"
    template_name = 'oscar/catalogue/category.html'
    enforce_paths = True

    def get(self, request, *args, **kwargs):
        # Fetch the category; return 404 or redirect as needed
        self.category = self.get_category()
        potential_redirect = self.redirect_if_necessary(
            request.path, self.category)
        if potential_redirect is not None:
            return potential_redirect

        try:
            self.search_handler = self.get_search_handler(
                request.GET, request.get_full_path(), self.get_categories())
        except InvalidPage:
            messages.error(request, _('The given page number was invalid.'))
            return redirect(self.category.get_absolute_url())

        return super().get(request, *args, **kwargs)

    def get_category(self):
        return get_object_or_404(Category, pk=self.kwargs['pk'])

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            # Categories are fetched by primary key to allow slug changes.
            # If the slug has changed, issue a redirect.
            expected_path = category.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_categories(self):
        """
        Return a list of the current category and its ancestors
        """
        return self.category.get_descendants_and_self()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        data = self.search_handler.get_queryset()
        data = data.filter(structure='standalone')
        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        search_context[self.context_object_name] = data
        context.update(search_context)
        return context


class ProductCreateView(TemplateView):
    """
    Create a composite product
    """
    context_object_name = "products"
    template_name = 'oscar/catalogue/create2.html'
    category_slug = ""

    def get(self, request, *args, **kwargs):
        try:
            self.category_slug = self.request.GET.get('cat')
            self.search_handler = self.get_search_handler(
                self.request.GET, request.get_full_path(), [])
        except InvalidPage:
            # Redirect to page one.
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:index')
        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        pc = ProductClass.objects.get(slug=self.category_slug)
        qt = QuizTemplate.objects.get(pk=1)
        quiz = Quiz()
        quiz.product_class = pc
        quiz.quiz_template = qt
        quiz.item_list = []
        quiz.save()
        ctx['quiz'] = quiz
        ctx['category'] = Category.objects.get(slug=self.category_slug)
        data = self.search_handler.get_queryset()
        data = data.filter(structure='standalone', product_class_id=pc.pk)
        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        search_context[self.context_object_name] = data
        ctx.update(search_context)
        return ctx

class ProductUpdateView(TemplateView):
    context_object_name = "products"
    template_name = 'oscar/catalogue/partials/products.html'
    pk_list = []

    def get(self, request, *args, **kwargs):
        # print(self.request.GET)
        self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [])

        # payload = dict(request.GET.lists())
        ques_type = self.request.GET.getlist("type")
        ques_topic = self.request.GET.getlist("topic")
        ques_type_id = []
        ques_topic_id = []
        for qt in ques_type:
            try:
                type_name = Category.objects.get(name=qt.strip())
                ques_type_id.append(type_name.pk)
            except Category.DoesNotExist:
                print("not found " + qt)

        for qt in ques_topic:
            try:
                topic_name = ProductAttribute.objects.get(name=qt.strip())
                ques_topic_id.append(topic_name.pk)
            except ProductAttribute.DoesNotExist:
                print("not found " + qt)
        filter_type = list(ProductAttributeValue.objects.filter(attribute_id__in=ques_type_id))
        filter_topic = list(ProductCategory.objects.filter(category_id__in=ques_topic_id))
        type_data = []
        topic_data = []
        for i in filter_type:
            type_data.append(i.product_id)
        for i in filter_topic:
            topic_data.append(i.product_id)
        self.pk_list = list(set(type_data).intersection(topic_data))

        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        cp, __ = Quiz.objects.get_or_create(pk=payload["composite_pk"])
        cp.update_itemlist([payload["pk"]], payload["action"])
        cp.save()
        return JsonResponse({'result':'ok'})

    def get_context_data(self, **kwargs):
        ctx = {}
        search_context = self.search_handler.get_search_context_data(
                            self.context_object_name)
        data = Product.objects.filter(pk__in=self.pk_list)
        search_context[self.context_object_name] = data
        ctx.update(search_context)
        return ctx

class ProductLayoutView(TemplateView):
    context_object_name = "questions"
    template_name = 'oscar/catalogue/layout_quiz.html'
    pk = ""

    def get(self, request, *args, **kwargs):
        self.pk = self.request.GET.get('pk')
        self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [])
        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        search_context = self.search_handler.get_search_context_data(
                            self.context_object_name)
        quiz = Quiz.objects.get(pk=self.pk)
        questions = Product.objects.filter(pk__in=quiz.item_list)
        search_context[self.context_object_name] = questions
        ctx.update(search_context)
        return ctx
