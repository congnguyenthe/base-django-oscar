from six import with_metaclass
from django import template
from oscar.core.loading import get_model

register = template.Library()
ProductClass = get_model("catalogue", "ProductClass")

@register.simple_tag(name="quiz_tree")
def get_annotated_list():
    return ProductClass.objects.all()
