from django.contrib import admin
from .models import TodoModel


class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created',)


# Register your models here.


admin.site.register(TodoModel, TodoAdmin)
