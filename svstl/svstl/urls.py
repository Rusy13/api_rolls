"""
URL configuration for svstl project.

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
# from rolls.views import RollApiV  
from rolls.views import CoilListCreateView
from rolls.views import CoilDeleteView
from rolls.views import CoilStatsView
from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/coil/', CoilListCreateView.as_view(), name='coil-list-create'),
    path('api/coil/<int:pk>/', CoilDeleteView.as_view(), name='coil-delete'),  # Добавляем URL-маршрут для удаления
    path('api/coil/stats/', CoilStatsView.as_view()),
]

urlpatterns += doc_urls


