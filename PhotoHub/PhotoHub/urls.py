from django.contrib import admin
from django.urls import path, include

#For uploading image to database.
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('Hub.urls')),
]

#For uploading image to database.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
                              