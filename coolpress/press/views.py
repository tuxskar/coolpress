import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from rest_framework import viewsets, mixins, permissions, filters, generics
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from press.forms import CommentForm, PostForm
from press.models import Category, Post, Comment, CoolUser, PostStatus
from press.serializers import CategorySerializer, PostSerializer, AuthorSerializer
from press.stats_manager import posts_analyzer


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
    objects = Post.objects.filter(status=PostStatus.PUBLISHED)[:20]
    return render(request, 'posts_list.html', {'posts_list': objects})


def author_details(request, author_id):
    author = get_object_or_404(CoolUser, pk=author_id)
    cat_stats = {}
    author_posts = author.post_set.all()
    author_char_cnt = 0
    for post in author_posts:
        category_id = post.category_id
        if category_id not in cat_stats:
            cat_stats[category_id] = 0
        cat_stats[category_id] += 1

        author_char_cnt += len(post.title)
        author_char_cnt += len(post.body)

    author_stats = posts_analyzer(author_posts)

    return render(request, 'author_details.html',
                  {'cat_stats': cat_stats,
                   'most_used_words': author_stats.top(10),
                   'user_characters': author_char_cnt,
                   'author': author
                   })


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)
    stats = posts_analyzer(Post.objects.filter(id=post.id))
    stats_list = stats.top(10)

    comments = post.comment_set.order_by('-creation_date')
    return render(request, 'posts_detail.html',
                  {'post_obj': post, 'comment_form': form, 'comments': comments, 'stats': stats,
                   'stats_list': stats_list})


@login_required
def add_post_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)
    if request.method == 'POST':
        if form.is_valid():
            votes = form.cleaned_data.get('votes')
            body = form.cleaned_data['body']
            Comment.objects.create(votes=votes, body=body, post=post, author=request.user.cooluser)
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': post_id}))

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

    return render(request, 'posts_update.html', {'my_awesome_form': form})


class AboutView(TemplateView):
    template_name = "about.html"


class CategoryListView(ListView):
    model = Category


class PostClassBasedListView(ListView):
    paginate_by = 20
    queryset = Post.objects.filter(status=PostStatus.PUBLISHED).order_by('-last_update')
    context_object_name = 'posts_list'
    template_name = 'posts_list.html'


class PostClassFilteringListView(PostClassBasedListView):
    paginate_by = 5

    def get_queryset(self):
        queryset = super(PostClassFilteringListView, self).get_queryset()
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return queryset.filter(category=category)


def filtered_search(queryset, search_text):
    is_in_title = Q(title__icontains=search_text)
    is_in_body = Q(body__icontains=search_text)
    is_in_username = Q(author__user__username__icontains=search_text)
    is_in_name = Q(author__user__first_name__icontains=search_text)
    return queryset.filter(is_in_title | is_in_body | is_in_username | is_in_name)


class PostSearchListView(PostClassBasedListView):
    def get_queryset(self):
        queryset = super(PostSearchListView, self).get_queryset()
        search_text = self.request.GET.get('search-text')
        if search_text:
            return filtered_search(queryset, search_text)

        return queryset

    @property
    def search_text(self):
        return self.request.GET.get('search-text')


def category_api(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return JsonResponse(
        dict(slug=cat.slug, label=cat.label)
    )


def categories_api(request):
    cats = {}
    for cat in Category.objects.all():
        cats[cat.id] = dict(slug=cat.slug, label=cat.label)

    return JsonResponse(
        cats
    )


class ModelNonDeletableViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               # mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class CategoryViewSet(ModelNonDeletableViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user.cooluser


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Post.objects.all().filter(status=PostStatus.PUBLISHED) \
        .order_by('-creation_date')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__id']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.cooluser)


class AuthorsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CoolUser.objects.alias(posts=Count('post')).filter(posts__gte=1)
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryAuthors(generics.ListAPIView):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        if self.kwargs.__len__() > 0:
            cslug_or_id = self.kwargs['pk']
            try:
                author_id = int(cslug_or_id)
                return self.queryset.filter(id=author_id)
            except:
                cat = Category.objects.get(slug=cslug_or_id)
                return self.queryset.filter(post__category=cat)
        return self.queryset
