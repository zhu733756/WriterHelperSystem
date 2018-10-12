"""WriterHelper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path,re_path
from Novel import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index,name="home"),
    path('search/', views.search,name="search"),
    path('search_form/', views.search_form,name="search_form"),
    path('search_dir/', views.search_dir,name="search_dir"),
    path('search_booklist/', views.search_booklist,name="search_booklist"),
    path('search_duplicate_url/', views.search_duplicate_url,name="search_duplicate_url"),
    path('search_crawl_status/', views.search_crawl_status,name="search_crawl_status"),
]

