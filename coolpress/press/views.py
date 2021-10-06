from django.shortcuts import render

from press.models import PostStatus, Post


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED).order_by('last_update')[:15]
    return render(request, 'posts_list.html', {'post_list': post_list})
