from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView

from press.models import Post, PostStatus, Category, CoolUser

from press.forms import PostForm, CategoryForm
from press.stats_manager import extract_stats_from_single_post, extract_stats_from_posts


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
    stats = extract_stats_from_single_post(post)
    return render(request, 'posts_detail.html', {'post_obj': post, 'stats': stats})


def post_list(request):
    post_list = Post.objects.filter(status=PostStatus.PUBLISHED.value).order_by('-pk')[:20]
    stats = extract_stats_from_posts(post_list)
    return render(request, 'posts_list.html', {'post_list': post_list, 'stats': stats})


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


class AboutView(TemplateView):
    template_name = "about.html"


class CategoryDetail(DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetail, self).get_context_data(*args, **kwargs)
        category = context['object']
        posts_filtered = Post.objects.filter(category=category)
        stats = extract_stats_from_posts(posts_filtered)
        context['stats'] = stats
        return context


class CategoryList(ListView):
    model = Category


class CategoryAdd(CreateView):
    model = Category
    form_class = CategoryForm


class CategoryUpdate(UpdateView):
    model = Category
    form_class = CategoryForm


class PostList(ListView):
    model = Post
    paginate_by = 2
    context_object_name = 'post_list'
    template_name = 'posts_list.html'

    def get_queryset(self):
        queryset = super(PostList, self).get_queryset()
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        return queryset.filter(category=category)


class PostFilteredByText(PostList):
    def get_queryset(self):
        queryset = super(PostList, self).get_queryset()
        search_text = self.request.GET.get('q')
        qs1 = Q(title__icontains=search_text)
        qs2 = Q(body__icontains=search_text)
        qs3 = Q(author__user__username__icontains=search_text)
        qs4 = Q(category__label__eq=search_text)
        return queryset.filter(qs1 | qs2 | qs3)

    def get_context_data(self, *args, **kwargs):
        context = super(PostFilteredByText, self).get_context_data(*args, **kwargs)
        context['search_data'] = self.request.GET.get('q')
        return context

def post_filtered_by_text(request):
    search_text = request.GET.get('q')
    qs1 = Q(title__icontains=search_text)
    qs2 = Q(body__icontains=search_text)
    qs3 = Q(author__user__username__icontains=search_text)
    qs4 = Q(category__label__eq=search_text)
    posts_list = Post.objects.filter(qs1 | qs2 | qs3| qs4)
    stats = extract_stats_from_posts(post_list)
    return render(request, 'posts_list.html', {'post_list': posts_list, 'stats': stats})


def category_api(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return JsonResponse(
        dict(slug=cat.slug, label=cat.label)
    )


def search_ajax(request):
    query_search = request.GET.get('q')
    posts = Post.objects.filter(title__icontains=query_search).values('id', 'title', 'body',
                                                                      'author__user__username',
                                                                      'category__label')
    ret = {p['id']: p for p in posts}
    return JsonResponse(
        ret
    )


class CooluserDetail(DetailView):
    model = CoolUser


class CooluserList(ListView):
    model = CoolUser
