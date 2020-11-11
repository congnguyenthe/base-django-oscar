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


import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse

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


class ProductDetailView(TemplateView):
    context_object_name = 'product'
    template_name = "oscar/catalogue/detail_coreui.html"
    pk = ""

    def get(self, request, *args, **kwargs):
        self.pk = self.request.GET.get('pk')
        self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [])
        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        build_step = dict()
        build_step['step_prev'] = "3. Setup layout"
        build_step['step_present'] = "4. Finish"
        build_step['action_prev'] = "layout"
        build_step['action_present'] = "summarize"
        ctx['build_step'] = build_step
        search_context = self.search_handler.get_search_context_data(
                            self.context_object_name)
        topics = dict()
        types = dict()
        quiz = Quiz.objects.get(pk=self.pk)
        for question_id in quiz.item_list:
            topic_id = ProductCategory.objects.get(product_id=question_id).category_id
            topic_name = Category.objects.get(pk=topic_id).name
            if topic_name in topics:
                topics[topic_name] = topics[topic_name] + 1
            else:
                topics[topic_name] = 1

            type_id = ProductAttributeValue.objects.get(product_id=question_id).attribute_id
            type_name = ProductAttribute.objects.get(pk=type_id).name
            if type_name in topics:
                types[type_name] = types[type_name] + 1
            else:
                types[type_name] = 1
        quiz = Quiz.objects.get(pk=self.pk)
        template = QuizTemplate.objects.get(pk=quiz.quiz_template_id)
        questions = Product.objects.filter(pk__in=quiz.item_list)
        ctx['template'] = template
        ctx['quiz'] = quiz
        ctx['topics'] = topics
        ctx['types'] = types
        search_context[self.context_object_name] = questions
        ctx.update(search_context)
        return ctx


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
    template_name = 'oscar/catalogue/create_coreui.html'
    category_slug = ""
    topic_selection = []
    type_selection = []

    def get(self, request, *args, **kwargs):
        try:
            self.category_slug = self.request.GET.get('cat')
            self.type_selection = self.request.GET.get('ques_type').split(",")
            self.topic_selection = self.request.GET.get('ques_topic').split(",")
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
        pk_list = []
        pc = ProductClass.objects.get(slug=self.category_slug)

        qt = QuizTemplate()
        qt.top_left = "Quiz Maker"
        qt.top_right = "Sample Test"
        qt.title = "Quiz Maker Sample Test"
        qt.bottom_left = "Quiz Maker"
        qt.bottom_right = "Sample Test"
        qt.page_num = True
        qt.save()

        quiz = Quiz()
        quiz.product_class = pc
        quiz.quiz_template = qt
        quiz.item_list = []
        quiz.save()
        ctx['quiz'] = quiz
        ctx['category'] = Category.objects.get(slug=self.category_slug)

        ques_type_id = []
        ques_topic_id = []
        for qt in self.type_selection:
            try:
                type_name = Category.objects.get(name=qt.strip())
                ques_type_id.append(type_name.pk)
            except Category.DoesNotExist:
                print("not found " + qt)

        for qt in self.topic_selection:
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
        pk_list = list(set(type_data).intersection(topic_data))

        # print(self.type_selection[0])
        # print(self.topic_selection[0])

        build_step = dict()
        build_step['step_prev'] = "1. Select Domain"
        build_step['step_present'] = "2. Select Contents"
        build_step['step_next'] = "3. Select layout"
        build_step['action_prev'] = "select"
        build_step['action_present'] = "create"
        build_step['action_next'] = "layout"
        build_step['type_selection'] = self.type_selection
        build_step['topic_selection'] = self.topic_selection
        # ctx['build_previous'] = "None"
        ctx['build_step'] = build_step

        data = self.search_handler.get_queryset()
        search_context = self.search_handler.get_search_context_data(
                            self.context_object_name)
        data = Product.objects.filter(pk__in=pk_list)
        search_context[self.context_object_name] = data
        ctx.update(search_context)

        return ctx


class ProductSelectView(TemplateView):
    """
    Select a composite product
    """
    context_object_name = "products"
    template_name = 'oscar/catalogue/select_adminlte.html'
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
        
        if self.category_slug:
            domain = dict()
            domain['slug'] = self.category_slug
            domain['name'] = Category.objects.get(slug=self.category_slug).name
            ctx['domain'] = domain

        return ctx


class ProductUpdateView(TemplateView):
    context_object_name = "products"
    template_name = 'oscar/catalogue/partials/products.html'
    quiz_pk = ""
    pk_list = []

    def get(self, request, *args, **kwargs):
        # print(self.request.GET)
        self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [])

        # payload = dict(request.GET.lists())
        ques_type = self.request.GET.getlist("type")
        ques_topic = self.request.GET.getlist("topic")
        self.pk = self.request.GET.get("pk")
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
        cp, __ = Quiz.objects.get_or_create(pk=payload["quiz_pk"])
        cp.update_itemlist([payload["pk"]], payload["action"])
        cp.save()
        return JsonResponse({'result':'ok'})

    def get_context_data(self, **kwargs):
        ctx = {}
        search_context = self.search_handler.get_search_context_data(
                            self.context_object_name)
        data = Product.objects.filter(pk__in=self.pk_list)
        quiz = Quiz.objects.get(pk=self.pk)
        search_context[self.context_object_name] = data
        ctx['quiz'] = quiz
        ctx.update(search_context)
        return ctx


class ProductLayoutView(TemplateView):
    context_object_name = "questions"
    template_name = 'oscar/catalogue/template_adminlte.html'
    pk = ""

    def get(self, request, *args, **kwargs):
        self.pk = self.request.GET.get('pk')
        self.search_handler = self.get_search_handler(self.request.GET, request.get_full_path(), [])
        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        build_step = dict()
        build_step['step_prev'] = "2. Select Contents"
        build_step['step_present'] = "3. Select layout"
        build_step['step_next'] = "4. Finish"
        build_step['action_prev'] = "create"
        build_step['action_present'] = "layout"
        build_step['action_next'] = "summarize"
        ctx['build_step'] = build_step

        search_context = self.search_handler.get_search_context_data(
                            self.context_object_name)
        # quiz = Quiz.objects.get(pk=self.pk)
        # template = QuizTemplate.objects.get(pk=quiz.quiz_template_id)
        # questions = Product.objects.filter(pk__in=quiz.item_list)
        # ctx['template'] = template
        # ctx['quiz'] = quiz
        # search_context[self.context_object_name] = questions
        ctx.update(search_context)
        return ctx

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        template = QuizTemplate.objects.get(pk=payload["pk"])
        if payload["pn"] == "True":
            show_pn = True
        else:
            show_pn = False
        template.updateTemplateContent(payload["tl"], payload["tr"], payload["title"], payload["bl"], payload["br"], show_pn)
        template.save()
        return JsonResponse({'result':'ok'})


class ProductDownloadView(TemplateView):
    template_name = 'oscar/printable/a4_pdf.html'
    pk = ""
    print_format = ""

    def get(self, request, *args, **kwargs):
        self.pk = self.request.GET.get('pk')
        self.print_format = self.request.GET.get('format')
        ctx = {}

        templateData = QuizTemplate.objects.get(pk=quiz.quiz_template_id)
        questions = Product.objects.filter(pk__in=quiz.item_list)
        template = get_template(self.template_name)
        ctx['questions'] = questions
        ctx['template'] = templateData
        html  = template.render(ctx)
        result = io.BytesIO()

        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))
