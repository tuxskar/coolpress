from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html

from press.models import Category, Post, CoolUser


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('label', 'view_post_lisk', 'slug')

    def view_post_lisk(self, obj):
        post_cnt = obj.post_set.count()
        url = reverse('admin:press_post_changelist') + f'?category__id={obj.id}'

        return format_html(f'<a href="{url}">{post_cnt}</a>')


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    search_fields = ['title', 'author__user__username']
    list_display = ['title', 'author']
    list_filter = ['category']


admin.site.register(Post, PostAdmin)


class CoolUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(CoolUser, CoolUserAdmin)
