from django import template
from django.utils.http import urlencode

from goods.models import Category

register = template.Library()


@register.simple_tag()
def tag_categories():
    categories = Category.objects.filter(product__isnull=False).distinct()

    all_products_category = Category.objects.filter(name="Усі товари").first()
    if all_products_category and all_products_category not in categories:
        categories = [all_products_category] + list(categories)

    return categories


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
