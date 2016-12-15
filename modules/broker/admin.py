# -*- coding: utf-8 -*-

from django.contrib import admin

from models import Source


class SourceModelAdmin(admin.ModelAdmin):
    list_display = ('source',)

    class Meta:
        model = Source

admin.site.register(Source, SourceModelAdmin)

