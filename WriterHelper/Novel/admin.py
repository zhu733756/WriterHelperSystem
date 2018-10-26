from django.contrib import admin
from .models import Book,Author,Arcticle,Category
# Register your models here.

# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ("name",)
#     search_fields = ("name",)
#
#     def get_search_results(self, request, queryset, search_term):
#         queryset,use_distinct=super(AuthorAdmin,self).get_search_results(request,queryset,serch_term)
#         return queryset, use_distinct

admin.site.register([Author,Arcticle,Book,Category])