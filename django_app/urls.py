from django.contrib import admin
from django.urls import path, include
import hello.views as hello

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', include('hello.urls')),
    path('sns/', include('sns.urls')),
]
