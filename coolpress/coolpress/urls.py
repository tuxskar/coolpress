from django.urls import path, include

from press import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'authors', views.AuthorsViewSet)

urlpatterns = [
    path('post_details/<int:post_id>', views.post_detail, name='posts-detail'),
    path('post/<int:post_id>/comment-add/', views.add_post_comment, name='comment-add'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('post/add/', views.post_update, name='post-add'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('posts/', views.PostClassBasedListView.as_view(), name='post-list'),
    path('posts/<str:category_slug>', views.PostClassFilteringListView.as_view(),
         name='posts-list-by-category'),
    path('posts/<slug:category_slug>', views.PostClassFilteringListView.as_view(), name='post-list-filtered-by-category'),
    path('api-category/<slug:slug>', views.category_api, name='category-api'),
    path('api-categories/', views.categories_api, name='categories-api'),
    path('api/', include(router.urls)),
    path('post-search/', views.search_post, name='post-search'),
    path('api-auth/', include('rest_framework.urls')),
    path('login/', views.signup, name='login'),
    path('test-email/', views.test_send_email),
    path('signup/', views.signup, name='signup'),

]