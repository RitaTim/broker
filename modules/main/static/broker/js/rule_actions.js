/*
   Логика работы с объектом Rule брокера в админке
*/
(function($){
        var set_source = function(){
            // Меняем значение текущего источника и значение источника в скрытом поле
            Rule.source = Rule.widgets.source_select.val() || Rule.source;
            Rule.widgets.source_hidden_input.val(Rule.source);
        };

        var set_destination = function () {
            // Меняем значение текущего приемника и значение приемника в скрытом поле
            Rule.destination = Rule.widgets.destination_select.val() || Rule.destination;
            Rule.widgets.destination_hidden_input.val(Rule.destination);
        };

        var update_select_methods = function(select, source, type_methods){
            // Обновляем селект с сигналами или коллбэками
            if (!source){
                select.html("");
                return;
            }

            var GET_DATA_SOURCE_URL = '/broker/source/get_methods';
            $.getJSON(
                [GET_DATA_SOURCE_URL, type_methods, source].join("/"),
                function (data) {
                    var options = "";
                    var current_func = type_methods == 'callbacks' ? Rule.callback : Rule.signal;
                    $.each(data[type_methods], function(num, func){
                        options = options + '<option value="' + func + '" ' + (func == current_func ? "selected" : "") + ' >' + func + '</option>';
                    });
                    select.html(options);
                }
            );
        };

    $(function() {
        Rule.init();
        var $_Rule = $(Rule);

        // Навешиваем обработчики событий
        $_Rule.on('RuleForm.change_source', function(){
            set_source();
            update_select_methods(Rule.widgets.signal_select, Rule.source, 'signals');
        });

        $_Rule.on('RuleForm.change_destination', function(){
            set_destination();
            update_select_methods(Rule.widgets.callback_select, Rule.destination, 'callbacks');
        });
        
        // Генирируем события, для обновления селектов сигналов и коллбэков
        Rule.change_source_event();
        Rule.change_destination_event();
    });
})(jQuery);
