odoo.define('kltn.ChartTemplate', function (require) {
    "use strict";


    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var QWeb = core.qweb;

    var ChartTemplate = AbstractAction.extend({
        template: "kltn.ChartTemplate",
        

        start: function () {
            var self = this;
            self.$el.html(QWeb.render('kltn.ChartTemplate', { widget: self.login_employee }));
        }

    });

    core.action_registry.add('hr_chart', ChartTemplate);

    return ChartTemplate;

});
