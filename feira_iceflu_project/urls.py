"""
URL configuration for feira_iceflu_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclui todas as URLs definidas em feira_app/urls.py
    # com um prefixo opcional.
    # Se você quiser que as URLs do app comecem com 'app/', use:
    # path('app/', include('feira_app.urls')),
    # Se você quiser que as URLs do app sejam acessadas diretamente da raiz do site (ex: seusite.com/login/), use:
    #path('app/', include('feira_app.urls', namespace='feira_app')), # Ou qualquer prefixo que desejar
    path('', include('feira_app.urls')),
]
