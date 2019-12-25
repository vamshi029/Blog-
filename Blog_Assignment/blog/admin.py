from django.contrib import admin

from .models import Post, Comment,Preference,Account


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Preference)
admin.site.register(Account)
