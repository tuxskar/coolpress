from django.urls import path, include
from rest_framework import routers

from . import views
from .views import AboutView, CategoryListView, PostClassBasedListView, PostClassFilteringListView, \
    CategoryCreateView, CategoryUpdateView, CategoryFormView, DetailCoolUser, category_api, \
    categories_list

router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('', views.post_list, name='posts-list'),
    path('post/<int:post_id>/', views.post_detail, name='posts-detail'),
    path('post/add/', views.post_update, name='post-add'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('about/', AboutView.as_view()),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('posts/', PostClassBasedListView.as_view(), name='post-class-list'),
    path('posts/<str:category_slug>', PostClassFilteringListView.as_view(),
         name='posts-list-by-category'),
    path('category/add/', CategoryCreateView.as_view(), name='category-add'),
    path('category/sample-add/', CategoryFormView.as_view(), name='category-sample-add'),
    path('category/<int:pk>/', CategoryUpdateView.as_view(), name='category-update'),
    path('user/<int:pk>/', DetailCoolUser.as_view(), name='user-detail'),
    path('api/category/<str:slug>/', category_api, name='category-json'),
    path('api/categories/', categories_list, name='categories-json'),
    path('post-search/', views.search_post, name='post-search'),
    path('api/', include(router.urls)),
    path('test-email/', views.test_send_email),
]
