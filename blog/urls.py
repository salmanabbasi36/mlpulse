from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('archive/', views.archive, name='archive'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('category/<slug:slug>/', views.category_list, name='category'),
    path('tag/<slug:slug>/', views.tag_list, name='tag'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
