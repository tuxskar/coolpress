import datetime

from django.http import HttpResponse
from django.shortcuts import render

from press.models import Category, Post


def home(request):
    now = datetime.datetime.now()
    msg = 'Welcome to Coolpres'
    categories = Category.objects.all()
    user = request.user
    li_cats = [f'<li>{cat.label}</li>' for cat in categories]
    cats_ul = f'<ul>{"".join(li_cats)}</ul>'

    html = f"<html><head><title>{msg}</title><body><h1>{msg}</h1><div>{user}</div><p>It is now {now}.<p>{cats_ul}</body></html>"
    return HttpResponse(html)


def render_a_post(post):
    return f'<div style="margin: 20px;padding-bottom: 10px;"><h2>{post.title}</h2><p style="color: gray;">{post.body}</p><p>{post.author.user.username}</p></div>'


def posts_list(request):
    objects = Post.objects.all()[:20]
    return render(request, 'posts_list.html', {'posts_list': objects})


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'posts_detail.html', {'post_obj': post})
