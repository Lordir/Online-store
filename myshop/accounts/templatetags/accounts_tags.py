from django import template
from django.db.models import Count

from accounts.models import *

register = template.Library()


@register.simple_tag()
def get_categories(id_category=None):
    if not id_category:
        return Category.objects.all()
    else:
        return Category.objects.filter(pk=id_category)


@register.inclusion_tag('accounts/list_categories.html')
def show_categories(sort=None, selected_category=0):
    if not sort:
        category = Category.objects.annotate(Count('product'))
    else:
        category = Category.objects.order_by(sort)

    return {"category": category, "selected_category": selected_category}


@register.inclusion_tag('accounts/menu.html')
def show_menu():
    menu = [{'title': "Информация", 'url_name': 'info'},
            {'title': "Добавить товар", 'url_name': 'add_product'},
            {'title': "Регистрация", 'url_name': 'registry'},
            {'title': "Войти", 'url_name': 'login'}
            ]
    return {"menu": menu}
