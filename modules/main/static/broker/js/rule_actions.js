/*
   Логика работы с объектом Rule брокера в админке
*/
function ruleManager(source, typeMethod){
    this.getDataSourceMethods = '/broker/source/get_methods';
    this.source = source;
    this.typeMethod = typeMethod;
};

ruleManager.prototype.get_methods_for_cls = function(){
    var self = this;
    $.getJSON(
        [self.getDataSourceMethods, self.typeMethod, self.source].join("/"),
        function (data) {
            if (data[self.typeMethod]) {
                $('select[name=' + self.typeMethod + ']').triggerHandler(
                    'Rule.' + self.typeMethod + '.update_select', {
                        'methods': data[self.typeMethod]
                    }
                );
            }
        }
    );
};
