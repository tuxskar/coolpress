from django.urls import path

from . import views

urlpatterns = [
    path('', views.post_list, name='index'),
    path('post/<int:post_id>', views.post_detail, name='posts-detail'),
    path('posts/', views.post_list, name='posts-list'),
    path('post/add/', views.post_update, name='post-add'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('category/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('category/add/', views.CategoryAdd.as_view(), name='category-add'),
    path('category/update/<int:pk>', views.CategoryUpdate.as_view(), name='category-update'),
    path('new-posts/<str:category_slug>', views.PostList.as_view(), name='post-list'),
    path('category-json/<str:slug>', views.category_api, name='category-json'),
    path('user/<int:pk>', views.CooluserDetail.as_view(), name='cooluser-detail'),
    path('users/', views.CooluserList.as_view(), name='cooluser-list'),
    path('posts-filtered/', views.search_ajax, name='search-ajax'),
    path('post-filtered/', views.PostFilteredByText.as_view(), name='post-filtered'),
]
