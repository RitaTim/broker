/* 
   Объектом Rule брокера в админке
*/
var Rule = {
    // Текущие значения источника, приемника, сигнала и коллбэка
    'source': undefined,
    'destination': undefined,
    'signal': undefined,
    'callback': undefined,

    // Генерация событий
    'changeSource': function(sourceId){
        // Изменился источник
        this.source = sourceId;
        new ruleManager(this.source, 'signal')
            .get_methods_for_cls();
    },
    'changeDestination': function(destinationId){
        // Изменился приемник
        this.destination = destinationId;
        new ruleManager(this.destination, 'callback')
            .get_methods_for_cls();
    },
    
    'init': function(sourceId, destinationId, signal, callback){
        // Устанавливаем начальные значения Правила
        if (sourceId) {
            this.changeSource(sourceId);
        }
        if (destinationId){
            this.changeDestination(destinationId);
        }
        this.signal = signal;
        this.callback = callback;
    }
};

function prepareOptions(methods, current_method){
    // Возвращает строку опций для селекта из переданных методов (methods)
    var options = "";
    $.each(methods, function(num, method){
        options = options + '<option value="' + method + '" ' + (method == current_method ? "selected" : "") + ' >' + method + '</option>';
    });
    return options;
};

function updateSelectHandler(event, data){
    var $el = $(this);
    $el.html(prepareOptions(data.methods, $el.val() || $el.data('init')));
};

jQuery(document).ready(function(){
    $('select[name=source]').on('change', function() { 
        Rule.changeSource($(this).val());
    });
    $('select[name=destination]').on('change', function() {
        Rule.changeDestination($(this).val());
    });
    $('select[name=signal]').data('init', Rule.signal)
        .on('Rule.signal.update_select', updateSelectHandler);
    $('select[name=callback]').data('init', Rule.callback)
        .on('Rule.callback.update_select', updateSelectHandler);
});
