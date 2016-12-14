# -*- coding: utf-8 -*-

from django.contrib import admin

from models import SourceModel


class SourceModelAdmin(admin.ModelAdmin):
    list_display = ('source',)

    class Meta:
        model = SourceModel

admin.site.register(SourceModel, SourceModelAdmin)

