import datetime

from django.db.models import Count, F
from django.db.models.functions import Coalesce

from press.models import CoolUser, Category, Post

# values
Post.objects.values('title', 'author__user__email')
Post.objects.values_list('title', 'author__user__email')
Post.objects.values_list('title', flat=True)

# filter
Post.objects.filter(title__icontains='google')
Post.objects.filter(title__icontains='google').count()
Post.objects.all().count()
Post.objects.filter(creation_date__gt=datetime.datetime(2022, 10, 1))
Post.objects.filter(creation_date__gt=datetime.datetime(2022, 10, 1)).count()
Post.objects.filter(creation_date__gt=datetime.datetime(2022, 10, 1), creation_date__lt=datetime.datetime(2022, 10, 5))
Post.objects.filter(creation_date__gt=datetime.datetime(2022, 10, 1), creation_date__lt=datetime.datetime(2022, 10, 5)).count()
# 61


## filter with lookup
Post.objects \
    .filter(author__user__email__icontains='gmail.com',
            creation_date__lt=datetime.datetime(2022, 10, 5)) \
    .exclude(title__icontains='LLC').order_by('-creation_date')
posts_qs = Post.objects \
    .filter(author__user__email__icontains='gmail.com',
            creation_date__lt=datetime.datetime(2022, 10, 5)) \
    .exclude(title__icontains='LLC')\
    .order_by('-creation_date')
print(posts_qs.query)
"""
SELECT "press_post"."id", "press_post"."title", "press_post"."body", "press_post"."image_link", 
       "press_post"."status", "press_post"."author_id", "press_post"."category_id", 
       "press_post"."creation_date", "press_post"."last_update" 
       FROM "press_post" 
           INNER JOIN "press_cooluser" ON ("press_post"."author_id" = "press_cooluser"."id") 
           INNER JOIN "auth_user" ON ("press_cooluser"."user_id" = "auth_user"."id") 
       WHERE ("auth_user"."email" LIKE %gmail.com% ESCAPE \'\\\' 
              AND "press_post"."creation_date" < 2022-10-05 00:00:00 
              AND NOT ("press_post"."title" LIKE %LLC% ESCAPE \'\\\')) 
       ORDER BY "press_post"."creation_date" DESC
"""


# exclude
last_qs = Post.objects\
    .filter(creation_date__gt=datetime.datetime(2022, 10, 1),
            creation_date__lt=datetime.datetime(2022, 10, 5))\
    .exclude(title__icontains='LLC')


print(last_qs.query)
"""
SELECT "press_post"."id", "press_post"."title", "press_post"."body", "press_post"."image_link", 
       "press_post"."status", "press_post"."author_id", "press_post"."category_id", 
       "press_post"."creation_date", "press_post"."last_update" 
       FROM "press_post" 
       WHERE ("press_post"."creation_date" > 2022-10-01 00:00:00 
         AND "press_post"."creation_date" < 2022-10-05 00:00:00 
         AND NOT ("press_post"."title" LIKE %LLC% ESCAPE '\'))
"""

Post.objects\
    .filter(creation_date__gt=datetime.datetime(2022, 10, 1),
            creation_date__lt=datetime.datetime(2022, 10, 5))\
    .exclude(title__icontains='LLC').count()
# 54



# order by
posts = Post.objects.order_by('-creation_date')
for post in posts:
    msg = f'({post.category.label}) - {post.title}'

posts = Post.objects.order_by(Coalesce('creation_date', 'category').desc())
for post in posts:
    msg = f'({post.category.label}) - {post.title}'

CoolUser.objects.get(id=2).post_set.count()

# annotate
users = CoolUser.objects.annotate(Count('post'))
users[0]
# <CoolUser: oscar>
users[0].post__count
# 5
users[1].post__count
# 2

## Alias
CoolUser.objects.alias(posts=Count('post')).filter(posts__gt=2)
pro_authors = CoolUser.objects.alias(posts=Count('post')).filter(posts__gt=2)
for author in pro_authors:
    print(author.user.username)

for author in pro_authors:
    print(author.user.username, author.post_set.count())

pro_ordered_authors = CoolUser.objects \
    .alias(posts=Count('post')) \
    .filter(posts__gt=2) \
    .order_by('-posts')
for author in pro_authors:
    print(f'{author.user.username} - {author.post_set.count()} posts')

# Get how may posts are by category
cats = Category.objects.alias(posts=Count('post')).annotate(posts=F('posts'))
for cat in cats:
    msg = f'{cat.label}: {cat.posts} posts'
    print(msg)

cat_values = Category.objects.all().values('label', post_cnt=Count('post'))
for values in cat_values:
    print(values.get('label'), values.get('post_cnt'))
