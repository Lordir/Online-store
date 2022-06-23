from django.db.models import Count

from .models import *

menu = [{'title': "Информация", 'url_name': 'info'},
        ]


class DataMixin:
    paginate_by = 4

    def get_user_context(self, **kwargs):
        context = kwargs
        category = Category.objects.annotate(Count('product'))
        if self.request.user.is_authenticated:
            profile = User.objects.filter(username=self.request.user)
            context['profile'] = profile
        user_menu = menu.copy()
        context['menu'] = user_menu
        context['category'] = category
        if 'selected_category' not in context:
            context['selected_category'] = 0
        return context
