# -*- coding: utf-8 -*-

from django import forms
from django.forms import Select

from models import Rule
from broker import sources as broker_sources


class RuleAdminForm(forms.ModelForm):
    """
        Форма в админке для создания и редактирования правил брокера
    """
    def clean(self):
        cleaned_data = super(RuleAdminForm, self).clean()
        signal = cleaned_data.get('signal')
        callback = cleaned_data.get('callback')

        if self.instance.id:
            source = self.instance.source
            destination = self.instance.destination

            # Проверка на существование правила с указанными параметрами
            if Rule.objects.filter(source=source, destination=destination,
                                   signal=signal, callback=callback)\
                           .exclude(id=self.instance.id).exists():
                raise forms.ValidationError(
                    u'Rule c указанными параметрами уже существует'
                )
        else:
            source = self.cleaned_data.get('source')
            destination = self.cleaned_data.get('destination')

        # Проверка на наличие сигнала и коллбэка у источника
        if source and destination:
            if signal:
                # Проверка, содержит ли источник такой сигнал
                self._check_cls_has_func(source.source, signal)
            if callback:
                # Проверка, содержит ли приемник такой коллбэк
                self._check_cls_has_func(
                    destination.source, callback, 'callbacks'
                )

        return cleaned_data

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
                u'У класса {} нет указанной функции {} типа {}'
                .format(cls_name, func_name, type_func)
            )

    class Meta:
        model = Rule
        fields = '__all__'
        widgets = {
            'signal': Select(),
            'callback': Select(),
        }
