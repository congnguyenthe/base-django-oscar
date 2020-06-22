from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView

from oscar.apps.basket.signals import (
    basket_addition, voucher_addition, voucher_removal)
from oscar.core import ajax
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import redirect_to_referrer, safe_referrer

Homepage = get_model('homepage', 'HomePage')

class HomepageView(ListView):
    model = Homepage
    template_name  = 'oscar/homepage/index.html'
    context_object_name = 'homepage'

    def get_queryset(self):
        template = loader.get_template('oscar/homepage/index.html')
        context = {
                'latest_question_list': "",
                }
        return HttpResponse(template.render(context))
