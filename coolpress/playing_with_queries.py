import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coolpress.settings")
django.setup()

from django.contrib.auth.models import User
from press.models import Post

def values():
    post = Post.objects.filter(title__icontains='covid')
    print(post)

    Post.objects.filter(title__icontains='covid')
    Post.objects.filter(title__contains='covid')
    Post.objects.filter(title__contains='covid').count()
    Post.objects.filter(title__icontains='covid').count()
    qs = Post.objects.filter(title__icontains='covid')
    type(qs)
    Post.objects.filter(title__icontains='covid').exclude(title__contains='weak')
    Post.objects.filter(title__icontains='covid').exclude(title__contains='weak').count()
    qs.exclude(title__contains='weak').count()
    qs
    qs2 = qs.exclude(title__contains='weak')
    qs2
    qs2.count()
    qs2.all()
    list(qs2.all())
    qs3 = list(qs2.all())
    qs3.count()
    qs2
    qs2.query
    print(qs2.query)
    qs2.values()
    qs2[2].values()
    qs2[1:].values()
    qs2.filter(id__in=[4, 5])
    qs3 = qs2.filter(id__in=[4, 5])
    qs3[0]
    qs3[0].id
    qs3.values()
    qs3.values()[0]
    qs3.values()[0]['last_update']
    qs3.values('body')
    qs2
    qs.count()
    qs2.count()
    qs2.update(body='Some awesome post information')
    sq2
    qs2
    qs2.values('body')
    User.objects.values('username')
    for val in User.objects.values('username'):
        print(val.get('username'))
    print("User.objects.values_list('username')", User.objects.values_list('username'))
    print("User.objects.values_list('username', flat=True)", User.objects.values_list('username', flat=True))
    print("User.objects.values_list('username', 'password')", User.objects.values_list('username', 'password'))
    print("User.objects.values_list('username', 'password', 'is_admin', 'email')", User.objects.values_list('username', 'password', 'is_admin', 'email'))
    print("User.objects.values_list('username', 'password', 'is_staff', 'email')", User.objects.values_list('username', 'password', 'is_staff', 'email'))
    print("User.objects.values_list('username')", User.objects.values_list('username'))
    print("User.objects.values_list('username', flat=True)", User.objects.values_list('username', flat=True))
    for val in User.objects.values_list('username', flat=True):
        print(val)
    User.objects.values_list('username', 'password', 'is_staff', 'email', flat=True)
    print(qs2)
    p = qs2[0]
    print(p)
    print(p.title)
    print(p.body)
    print(p.author)
    print(p.author.user)
    print(p.author.user.username)
    Post.objects.filter(status='DRAFT')
    Post.objects.filter(status='PUBLISHED')
    for post in Post.objects.filter(status='PUBLISHED'):
        print(post.author.user.username)
    Post.objects.filter(status='PUBLISHED').values('author__user__username')
    Post.objects.filter(status='PUBLISHED').values_list('author__user__username', flat=True)
    all = Post.objects.filter(status='PUBLISHED').values_list('author__user__username', flat=True)
    all.count()
    len(set(all))


if __name__ == '__main__':
    values()
