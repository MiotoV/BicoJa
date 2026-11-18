import os

from django.contrib import admin
from django.urls import path

admin.site.site_header = "Painel BicoJá"
admin.site.site_title = "Painel BicoJá"

urlpatterns = [
    path(os.environ.get("DJANGO_ADMIN_URL", "admin/"), admin.site.urls),
]