from six import with_metaclass
from django import template
from oscar.core.loading import get_model

register = template.Library()
Attribute = get_model("catalogue", "ProductAttribute")

@register.simple_tag(name="attributes")   # noqa: C901 too complex
def get_annotated_list():
    return Attribute.objects.all()
