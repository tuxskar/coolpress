from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden, \
    JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, FormView, CreateView, UpdateView, \
    DetailView

from rest_framework import viewsets

from coolpress.settings import EMAIL_HOST_USER, HOME_INDEX
from .serializers import PostSerializer

from press.forms import PostForm, CategoryForm, CoolUserForm, CommentForm
from press.models import PostStatus, Post, CoolUser, Category, Comment
from press.stats_manager import extract_posts_stats


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-last_update')[
                :20]
    return render(request, 'posts_list.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    qs_post = Post.objects.filter(pk=post_id)
    stats = extract_posts_stats(qs_post)
    return render(request, 'posts_detail.html', {'post_obj': post, 'stats': stats})


@login_required
def add_post_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)
    if request.method == 'POST':
        if form.is_valid():
            votes = form.cleaned_data.get('votes')
            body = form.cleaned_data.get('body')
            Comment.objects.create(votes=votes, body=body, author=request.user.cooluser, post=post)
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': post.id}))

    return render(request, 'comment-add.html', {'form': form, 'post': post})


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


class PostClassBasedPaginatedListView(PostClassBasedListView):
    paginate_by = 2
    queryset = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-last_update')


class PostClassFilteringListView(PostClassBasedPaginatedListView):
    def get_queryset(self):
        queryset = super(PostClassFilteringListView, self).get_queryset()
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return queryset.filter(category=category)

    def get_context_data(self, *args, **kwargs):
        context = super(PostClassFilteringListView, self).get_context_data(*args, **kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['category_slug']).label
        stats = extract_posts_stats(context['object_list'])
        context['stats'] = stats
        return context


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


def category_api(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return JsonResponse(
        dict(slug=cat.slug, label=cat.label)
    )


def categories_list(request):
    cats = {}
    for cat in Category.objects.all():
        cats[cat.id] = dict(slug=cat.slug, label=cat.label)

    return JsonResponse(
        cats
    )


def search_posts(search_text: str, limit=15):
    if not search_text:
        return []
    is_in_title = Q(title__icontains=search_text)
    is_in_body = Q(body__icontains=search_text)
    is_in_username = Q(author__user__username__icontains=search_text)
    is_in_name = Q(author__user__first_name__icontains=search_text)
    return Post.objects.filter(is_in_title | is_in_body | is_in_username | is_in_name)[:limit]


def search_post(request):
    search_text = request.GET.get('search-text')
    post_list = search_posts(search_text)
    return render(request, 'posts_list.html', {'post_list': post_list, 'search_text': search_text})


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Post.objects.all().filter(status=PostStatus.PUBLISHED.value).order_by(
        '-creation_date')
    serializer_class = PostSerializer


def test_send_email(request):
    send_mail('Testing subject',
              'This is just a test of how would looks like an email from django',
              recipient_list=['tuxskar@gmail.com', 'oramirezpublic@gmail.com'],
              from_email=EMAIL_HOST_USER)
    return render(request, 'sent_email.html')


def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        cooluser_form = CoolUserForm(request.POST)
        if user_form.is_valid() and cooluser_form.is_valid():
            user = user_form.save(commit=False)
            user.email = cooluser_form.cleaned_data.get('email')
            user.save()
            user.refresh_from_db()  # load the profile instance created by the signal

            cooluser_form = CoolUserForm(request.POST, instance=user.cooluser)
            cooluser_form.full_clean()
            _ = cooluser_form.save()

            password = user_form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=password)
            login(request, user)
            return redirect(HOME_INDEX)
    else:
        user_form = UserCreationForm()
        cooluser_form = CoolUserForm()
    return render(request, 'signup.html', {
        'user_form': user_form,
        'cooluser_form': cooluser_form
    })
