# -*- coding: utf-8 -*-

from django import forms

from broker.models import Rule
from .models import CallbackLog, SignalLog


class SignalLogForm(forms.ModelForm):
    """
        Форма для модели логирования сигналов
    """
    def get_rules(self):
        """
            Возвращает список правил по данным сигнала
        """
        return Rule.objects.filter(
            source=self.cleaned_data.get('source'),
            signal=self.cleaned_data.get('signature')
        )

    class Meta:
        model = SignalLog
        fields = forms.ALL_FIELDS


class CallbackLogForm(forms.ModelForm):
    """
        Форма для модели логирования callbacks
    """
    class Meta:
        model = CallbackLog
        exclude = ('state',)
