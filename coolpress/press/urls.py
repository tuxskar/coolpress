from django.urls import path

from . import views

urlpatterns = [
    path('', views.post_list, name='index'),
    path('post/<int:post_id>', views.post_detail, name='posts-detail'),
    path('posts/', views.post_list, name='posts-list'),
    path('post/add/', views.post_update, name='post-add'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
]
