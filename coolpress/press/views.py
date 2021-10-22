from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from press.models import Post, PostStatus

from press.forms import PostForm


def index(request):
    return HttpResponse('Hi this is my first app')


def get_html_from_post(post):
    return f'''
    <html>
    <body>
    <h1>The asked post id {post.id}</h1> 
    <ul>
    <li>{post.title}</li>
    <li>{post.body}</li>
    <li>{post.category.label}</li>
    <li>{post.last_update}</li>
    </ul>

    <p>{post.author.user.username}</p>
    </body>
    </html>
    '''


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts_detail.html', {'post_obj': post})


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-pk')[:20]
    return render(request, 'posts_list.html', {'post_list': post_list})


@login_required
def post_update(request, post_id=None):
    post = None
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
        if request.user != post.author.user:
            return HttpResponseBadRequest('Not Allowed to change others posts')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user.cooluser
            instance.save()
            redirect_url = reverse('posts-detail', kwargs={'post_id': instance.id})
            return HttpResponseRedirect(redirect_url)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts_update.html', {'form': form})
