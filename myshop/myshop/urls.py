from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accounts.views import *
from myshop import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    import mimetypes

    # mimetypes.add_type("application/javascript", ".js", True)
    urlpatterns = [path('__debug__/', include('debug_toolbar.urls')), ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = pageNotFound
