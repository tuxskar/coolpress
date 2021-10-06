from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from coolpress.settings import HOME_INDEX
from press.forms import PostForm
from press.models import PostStatus, Post, CoolUser


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-id')
    return render(request, 'posts_list.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts_detail.html', {'post_obj': post})


@login_required
def post_update(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PostForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            instance = form.save(commit=False)
            username = request.user.username
            instance.author = CoolUser.objects.get(user__username=username)
            instance.save()
            return HttpResponseRedirect(reverse('posts_detail', kwargs={'post_id': instance.id}))
    else:
        form = PostForm()

    return render(request, 'posts_update.html', {'form': form})


