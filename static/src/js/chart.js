odoo.define('kltn.ChartTemplate', function (require) {
    "use strict";

    var core = require('web.core');
    // var Chart = require('web.Chart');
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var QWeb = core.qweb;



    var ChartTemplate = AbstractAction.extend({
        template: "kltn.ChartTemplate",

        start: function () {
            var self = this;
            self.$el.html(QWeb.render('kltn.ChartTemplate', { widget: self }));
        }


    });

    // var chart = new Chart("chart_example", {
    //     type: "line",
    //     data: {
    //         labels: [10, 20, 30, 40, 50],
    //         datasets: [{
    //             data: [10, 20, 30, 40, 50],
    //             pointBackgroundColor: "black",
    //         }]
    //     },
    //     option: {}
    // });

    core.action_registry.add('hr_chart', ChartTemplate);

    return ChartTemplate;

});
