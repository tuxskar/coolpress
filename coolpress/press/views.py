from django.shortcuts import render, get_object_or_404

from press.models import PostStatus, Post


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED).order_by('last_update')[:15]
    return render(request, 'posts_list.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts_detail.html', {'post_obj': post})
