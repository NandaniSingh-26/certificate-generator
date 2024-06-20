"""
URL configuration for certificate_generator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from certificates.views import generate_certificates,verify_certificate,download_all_certificates,download_certificate
urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/',generate_certificates, name='generate_certificates'),
    path('verify/<int:certificate_id>/', verify_certificate, name='verify_certificate'),
    path('download/<int:certificate_id>/', download_certificate, name='download_certificate'),
    path('download/all/', download_all_certificates, name='download_all_certificates'),
]
