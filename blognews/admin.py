from django.contrib import admin
from .models import User, NewsArticle
from django.db import models


class NewsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Author', {'fields': ['source', 'author']}),
        ('Title', {'fields': ['title', 'description']}),
        ('Content', {'fields': ['urlToImage', 'content']}),
        ('Source', {'fields': ['url', 'publishedAt']})
    ]



#admin.site.register(User)
#admin.site.register(NewsArticle)
admin.site.register(NewsArticle, NewsAdmin)