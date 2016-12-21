# -*- coding: utf-8 -*-

from django.contrib import admin
from django.shortcuts import get_object_or_404

from models import Source, Rule
from forms import RuleAdminForm


class SourceAdmin(admin.ModelAdmin):
    list_display = ('source',)

    class Meta:
        model = Source


class RuleAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination')
    fields = ['source', 'signal', 'destination', 'callback']

    add_form_template = "admin/broker/rule/change_form_template.html"
    change_form_template = add_form_template

    form = RuleAdminForm

    def get_readonly_fields(self, request, obj=None):
        if obj:  # при редактировании
            return self.readonly_fields + ('source', 'destination')
        return self.readonly_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = {}
        context.update(extra_context or {})
        instance = get_object_or_404(Rule, id=object_id)
        context.update({
            'source_hidden': instance.source_id,
            'destination_hidden': instance.destination_id,
            'signal_hidden': instance.signal,
            'callback_hidden': instance.callback,
        })
        return super(RuleAdmin, self).change_view(
            request, object_id, form_url, context
        )

admin.site.register(Source, SourceAdmin)
admin.site.register(Rule, RuleAdmin)

