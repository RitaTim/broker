/* 
    Работа с формой модели Rules брокера в админке
*/

(function ($){
    var RuleForm = {
        'source': undefined,
        'destination': undefined,
        'signal': undefined,
        'callback': undefined,

        // Селекты параметров, которые видит(изменяет) пользователь
        'source_select': $('select[name=source]'),
        'destination_select': $('select[name=destination]'),
        'signal_select': $('select[name=signal]'),
        'callback_select': $('select[name=callback]'),

        // Скрытые инпуты, из которых берутся необходимые значения
        'source_hidden_input': $('input[name=source_hidden]'),
        'destination_hidden_input': $('input[name=destination_hidden]'),
        'signal_hidden_input': $('input[name=signal_hidden]'),
        'callback_hidden_input': $('input[name=callback_hidden]'),
        // Значения этих инпутов меняются динамически, при смене видимых селектов

        'get_data_source_url': '/broker/source/get_methods',

        // Функции
        "_get_value_select": function(select){
            var selected_option = select.find('option:selected');
            return selected_option.val() ? selected_option.text() : null;
        },
        'on_change_source': function(){
            // Изменяем источник
            RuleForm.source = RuleForm._get_value_select(RuleForm.source_select);
            RuleForm.source_hidden_input.val(RuleForm.source);

            // Обновляем select со списком сигналов
            RuleForm.update_select_methods(RuleForm.signal_select, RuleForm.source, 'signals');
        },
        'on_change_destination': function(){
            // Изменяем приемник
            RuleForm.destination = RuleForm._get_value_select(RuleForm.destination_select);
            RuleForm.destination_hidden_input.val(RuleForm.destination);

            // Обновляем select со списком коллбэков
            RuleForm.update_select_methods(RuleForm.callback_select, RuleForm.destination, 'callbacks');
        },
        'update_select_methods': function(select, source, type_methods){
            // Обновляем селект с сигналами или коллбэками
            if (!source){
                select.html("");
                return;
            }

            $.getJSON(
                [RuleForm.get_data_source_url, type_methods, source].join("/"),
                function (data) {
                    var options = "";
                    var current_func = type_methods == 'callbacks' ? RuleForm.callback : RuleForm.signal;
                    $.each(data[type_methods], function(num, func){
                        options = options + '<option value="' + func + '" ' + (func == current_func ? "selected" : "") + ' >' + func + '</option>';
                    });
                    select.html(options);
                }
            );
        },
        'init': function(){
            // Инициализируем параметры формы
            RuleForm.source = RuleForm.source_hidden_input.val();
            RuleForm.destination = RuleForm.destination_hidden_input.val();
            RuleForm.signal = RuleForm.signal_hidden_input.val();
            RuleForm.callback = RuleForm.callback_hidden_input.val();

            // Навешиваем обработчики на смену источника и приемника
            RuleForm.source_select.on('change', RuleForm.on_change_source);
            RuleForm.destination_select.on('change', RuleForm.on_change_destination);

            // Обновляем селекты коллбэков и сигналов
            RuleForm.update_select_methods(RuleForm.callback_select, RuleForm.destination, 'callbacks');
            RuleForm.update_select_methods(RuleForm.signal_select, RuleForm.source, 'signals');
        }
    };
    
    $(function(){
        RuleForm.init();
    })
})(jQuery);
