from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from press.models import CoolUser, Category, Post


class CoolUserInline(admin.StackedInline):
    model = CoolUser
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (CoolUserInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class CoolUserAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'github_profile', 'view_post_link', 'gh_repositories', 'gravatar_link')
    list_filter = ('gh_repositories',)

    def view_post_link(self, obj):
        count = obj.post_set.count()
        url = (
                reverse("admin:press_post_changelist")
                + "?"
                + urlencode({"author__id": f"{obj.id}"})
        )
        label = f'Posts' if count > 1 else 'Post'
        return format_html(f'<a href="{url}">{count} {label}</a>', url, count)

    view_post_link.short_description = "Post"


admin.site.register(CoolUser, CoolUserAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'label', 'view_post_link')

    def view_post_link(self, obj):
        count = obj.post_set.count()
        url = (
                reverse("admin:press_post_changelist")
                + "?"
                + urlencode({"category__id": f"{obj.id}"})
        )
        label = f'Posts' if count > 1 else 'Post'
        return format_html(f'<a href="{url}">{count} {label}</a>', url, count)

    view_post_link.short_description = "Post"


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_filter = ('category', 'status')
    search_fields = ("title", "body")
    list_display = ('title', 'author', 'last_update', 'status', 'category', 'image_link')


admin.site.register(Post, PostAdmin)
