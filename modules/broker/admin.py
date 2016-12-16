# -*- coding: utf-8 -*-

from django.contrib import admin

from models import Source, Rule
from forms import RuleAdminForm


class SourceAdmin(admin.ModelAdmin):
    list_display = ('source',)

    class Meta:
        model = Source


class RuleAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination')
    fields = [
        'source', 'destination', 'signal', 'callback', 'source_hidden',
        'destination_hidden', 'signal_hidden', 'callback_hidden'
    ]

    add_form_template = "admin/broker/rule/change_form_template.html"
    change_form_template = "admin/broker/rule/change_form_template.html"

    form = RuleAdminForm

    def get_readonly_fields(self, request, obj=None):
        if obj:  # при редактировании
            return self.readonly_fields + ('source', 'destination')
        return self.readonly_fields

admin.site.register(Source, SourceAdmin)
admin.site.register(Rule, RuleAdmin)

