from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from . import views
from .views import AboutView, CategoryListView, PostClassBasedListView, PostClassFilteringListView, \
    CategoryCreateView, CategoryUpdateView, CategoryFormView, DetailCoolUser, category_api, \
    categories_list

router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'categories-2', views.CategoryViewSet)
router.register(r'authors', views.AuthorsViewSet)

urlpatterns = [
    path('', views.post_list, name='posts-list'),
    path('post/<int:post_id>/', views.post_detail, name='posts-detail'),
    path('post/add/', views.post_update, name='post-add'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('post/<int:post_id>/newcomment', views.add_post_comment, name='comment-add'),
    path('about/', AboutView.as_view()),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('posts/', PostClassBasedListView.as_view(), name='post-class-list'),
    path('posts/<str:category_slug>', PostClassFilteringListView.as_view(),
         name='posts-list-by-category'),
    path('category/add/', CategoryCreateView.as_view(), name='category-add'),
    path('category/sample-add/', CategoryFormView.as_view(), name='category-sample-add'),
    path('category/<int:pk>/', CategoryUpdateView.as_view(), name='category-update'),
    path('category/custom-add/', views.custom_category_edit, name='category-custom-add'),
    path('category/custom-add/<int:category_id>/', views.custom_category_edit, name='category-custom-modify'),
    path('user/<int:pk>/', DetailCoolUser.as_view(), name='user-detail'),
    path('api/category/<str:slug>/', category_api, name='category-json'),
    path('api/categories/', categories_list, name='categories-json'),
    path('post-search/', views.search_post, name='post-search'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('openapi', get_schema_view(
        title="CoolPress",
        description="API to get cool news",
        version="1.0.0"
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='redoc'),

    path('test-email/', views.test_send_email),
    path('signup/', views.signup, name='signup'),
]
