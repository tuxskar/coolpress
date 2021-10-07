from django.urls import path

from . import views

urlpatterns = [
    path('', views.post_list, name='posts_list'),
    path('post/<int:post_id>/', views.post_detail, name='posts_detail'),
    path('post/new/', views.post_update, name='post_new'),
    path('post/update/<int:post_id>', views.post_update, name='post_update'),
]