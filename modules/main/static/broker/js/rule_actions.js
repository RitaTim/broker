/*
   Логика работы с объектом Rule брокера в админке
*/
function ruleManager(){
    this.get_data_source_methods = '/broker/source/get_methods';
};

ruleManager.prototype.get_methods_for_cls = function(source, type_methods){
    $.getJSON(
        [this.get_data_source_methods, type_methods, source].join("/"),
        function (data) {
            if (data[type_methods]) {
                $.event.trigger('Rule.update_select', {
                    'type_methods': type_methods,
                    'methods': data[type_methods]
                });
            }
        }
    );
};
