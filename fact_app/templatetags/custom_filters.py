# polls/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    try:
        return value.as_widget(attrs={"class": css_class})
    except AttributeError:
        return value
