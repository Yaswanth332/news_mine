from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css_class):
    # Only add class if this is a form field
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": css_class})
    return field  # Return unchanged if it's not a form field
