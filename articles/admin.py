from django.contrib import admin
from .models import Article, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0   # Esta variable la utilizacion para indicar el # de filas extra que deseamos que aparezca en el adminsite por default.

class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
    ]
    list_display = [
        "title",
        "body",
        "author",
    ]

admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)