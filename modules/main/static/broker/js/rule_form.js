/* 
   Объектом Rule брокера в админке
*/
var Rule = {
    // Текущие значения источника, приемника, сигнала и коллбэка
    'source': undefined,
    'destination': undefined,
    'signal': undefined,
    'callback': undefined,
    
    // DOM объекты
    'selectors': {
        'source_select': 'select[name=source]',
        'destination_select': 'select[name=destination]',
        'signal_select': 'select[name=signal]',
        'callback_select': 'select[name=callback]',
        'source_hidden_input': '#source_hidden',
        'destination_hidden_input': '#destination_hidden',
        'signal_hidden_input': '#signal_hidden',
        'callback_hidden_input': '#callback_hidden'
    },
    'widgets':{},
    'init_widgets': function(){
        // Заполняем widgets объектами, полученными из DOM по селекторам
        $.each(Rule.selectors, function(name_field, selector){
            Rule.widgets[name_field] = $(selector);
        });
    },

    // Генерация событий
    'change_source_event': function(){
        // Изменился источник
        $(Rule).trigger('RuleForm.change_source');
    },
    'change_destination_event': function(){
        // Изменился приемник
        $(Rule).trigger('RuleForm.change_destination');
    },

    'init': function(){
        Rule.init_widgets();
        
        // Устанавливаем начальные значения Правила
        Rule.source = Rule.widgets.source_hidden_input.val();
        Rule.destination = Rule.widgets.destination_hidden_input.val();
        Rule.callback = Rule.widgets.callback_hidden_input.val();
        Rule.signal = Rule.widgets.signal_hidden_input.val();

        // Навешиваем обработчики на событие смены источника и приемника
        Rule.widgets.source_select.on('change', Rule.change_source_event);
        Rule.widgets.destination_select.on('change', Rule.change_destination_event);
    }
};
