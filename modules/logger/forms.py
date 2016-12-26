# -*- coding: utf-8 -*-

from django import forms

from logger.models import CallbackLog, SignalLog


class SignalLogForm(forms.ModelForm):
    """
        Форма для модели логирования сигналов
    """
    class Meta:
        model = SignalLog
        fields = forms.ALL_FIELDS


class CallbackLogForm(forms.ModelForm):
    """
        Форма для модели логирования callbacks
    """
    class Meta:
        model = CallbackLog
        fields = forms.ALL_FIELDS
