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
        $.event.trigger('Rule.change_source');
    },
    'change_destination_event': function(){
        // Изменился приемник
        $.event.trigger('Rule.change_destination');
    },

    'init': function(){
        Rule.init_widgets();
        
        // Устанавливаем начальные значения Правила
        Rule.source = Rule.widgets.source_hidden_input.val();
        Rule.destination = Rule.widgets.destination_hidden_input.val();
        Rule.callback = Rule.widgets.callback_hidden_input.val();
        Rule.signal = Rule.widgets.signal_hidden_input.val();
    }
};

jQuery(document).ready(function(){
    Rule.init();

    Rule.widgets.source_select.on('change', Rule.change_source_event);
    Rule.widgets.destination_select.on('change', Rule.change_destination_event);

    // Генирируем события, для обновления селектов сигналов и коллбэков
    if (Rule.source && Rule.destination) {
        Rule.change_source_event();
        Rule.change_destination_event();
    }
});


jQuery(document).bind({
    'Rule.change_source': function(){
        Rule.source = Rule.widgets.source_select.val() || Rule.source;
        Rule.widgets.source_hidden_input.val(Rule.source);

        var ruleMan = new ruleManager();
        ruleMan.get_methods_for_cls(Rule.source, 'signals')
    },
    'Rule.change_destination': function(){
        Rule.destination = Rule.widgets.destination_select.val() || Rule.destination;
        Rule.widgets.destination_hidden_input.val(Rule.destination);

        var ruleMan = new ruleManager();
        ruleMan.get_methods_for_cls(Rule.destination, 'callbacks')
    },
    'Rule.update_select': function(event, data){
        var current_func;
        var select;
        var type_methods = data['type_methods'];
        var methods = data['methods'];

        if (type_methods == 'callbacks'){
            current_func = Rule.callback;
            select = Rule.widgets.callback_select;
        } else {
            current_func = Rule.signal;
            select = Rule.widgets.signal_select;
        }

        // Формируем список опций для селекта
        var options = "";
        $.each(methods, function(num, func){
            options = options + '<option value="' + func + '" ' + (func == current_func ? "selected" : "") + ' >' + func + '</option>';
        });

        select.html(options);
    }
});