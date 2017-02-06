# -*- coding: utf-8 -*-

from django.contrib import admin
from django.shortcuts import get_object_or_404

from models import Source, Rule
from forms import RuleAdminForm


class SourceAdmin(admin.ModelAdmin):
    list_display = ('source', 'type_source')
    fields = ['source', 'type_source', 'init_params']
    readonly_fields = ('type_source',)

    class Meta:
        model = Source


class RuleAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination')
    fields = [
        'source', 'signal', 'destination', 'callback', 'params',
        'additional_params'
    ]

    add_form_template = "admin/broker/rule/change_form_template.html"
    change_form_template = add_form_template

    form = RuleAdminForm

    def get_readonly_fields(self, request, obj=None):
        if obj:  # при редактировании
            return self.readonly_fields + ('source', 'destination')
        return self.readonly_fields

admin.site.register(Source, SourceAdmin)
admin.site.register(Rule, RuleAdmin)

