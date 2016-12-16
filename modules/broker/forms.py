# -*- coding: utf-8 -*-

from django import forms
from django.forms import Select

from models import Rule
from broker import sources as broker_sources


class RuleAdminForm(forms.ModelForm):
    """
        Форма в админке для создания и редактирования правил брокера
    """
    source_hidden = forms.CharField(max_length=36, required=False,
                                    widget=forms.HiddenInput())
    destination_hidden = forms.CharField(max_length=36, required=False,
                                         widget=forms.HiddenInput())
    signal_hidden = forms.CharField(max_length=36, required=False,
                                    widget=forms.HiddenInput())
    callback_hidden = forms.CharField(max_length=36, required=False,
                                      widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(RuleAdminForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            self.fields['source_hidden'].initial = kwargs['instance'].source
            self.fields['destination_hidden'].initial = kwargs['instance']\
                                                        .destination
            self.fields['signal_hidden'].initial = kwargs['instance'].signal
            self.fields['callback_hidden'].initial = kwargs['instance']\
                                                     .callback

    def clean(self):
        source_name = self.cleaned_data.get('source_hidden')
        destination_name = self.cleaned_data.get('destination_hidden')
        signal = self.cleaned_data.get('signal')
        callback = self.cleaned_data.get('callback')

        # Проверка, содержит ли источник такой сигнал
        self._check_cls_has_func(source_name, signal)
        # Проверка, содержит ли приемник такой коллбэк
        self._check_cls_has_func(destination_name, callback, 'callbacks')

    def _check_cls_has_func(self, cls_name, func_name, type_func='signals'):
        """
            Бросает исключение, если сигнала или коллбэка (func_name)
            нет в классе cls_name
        """
        source_cls = getattr(broker_sources, cls_name)
        func_lst = source_cls.all_callbacks \
            if type_func == 'callbacks' else source_cls.all_signals
        func_names = [f.func_name for f in func_lst]

        if not func_name in func_names:
            raise forms.ValidationError(
                u'У класса {} нет функции {} типа {}'
                .format(cls_name, func_name, type_func)
            )

    class Meta:
        model = Rule
        fields = ['source', 'destination', 'signal', 'callback']
        widgets = {
            'signal': Select(),
            'callback': Select(),
        }
