from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, ListView, FormView, CreateView, UpdateView, \
    DetailView

from press.forms import PostForm, CategoryForm
from press.models import PostStatus, Post, CoolUser, Category


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-last_update')[
                :20]
    return render(request, 'posts_list.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts_detail.html', {'post_obj': post})


@login_required
def post_update(request, post_id=None):
    post = None
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
        if request.user != post.author.user:
            return HttpResponseBadRequest('Not allowed to change others posts')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            instance = form.save(commit=False)
            username = request.user.username
            instance.author = CoolUser.objects.get(user__username=username)
            instance.save()
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': instance.id}))
    else:
        form = PostForm(instance=post)

    return render(request, 'posts_update.html', {'form': form})


class AboutView(TemplateView):
    template_name = "about.html"


class CategoryListView(ListView):
    model = Category


class PostClassBasedListView(ListView):
    limit = 20
    queryset = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-last_update')[
               :limit]
    context_object_name = 'post_list'
    template_name = 'posts_list.html'


class PostClassFilteringListView(PostClassBasedListView):
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Post.objects.filter(status=PostStatus.PUBLISHED.value, category=category).order_by(
            '-last_update')[:self.limit]


class CategoryFormView(FormView):
    template_name = 'press/category_form.html'
    form_class = CategoryForm


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm


class DetailCoolUser(DetailView):
    model = CoolUser
