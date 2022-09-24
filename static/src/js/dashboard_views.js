odoo.define('KLTN.Dashboard', function (require) {
"use strict";


var core = require('web.core');
var AbstractAction = require('web.AbstractAction');

var HrDashboard = AbstractAction.extend({
    template: "KLTN.HrDashboardMain",
    events: {
        'click .hrms_overview': 'raise_alert',
    },

    raise_alert: function(event) {
        alert("hello");
    },

    init: function(parent, context) {
        this._super(parent, context);
    },
});

core.action_registry.add('hr_dashboard', HrDashboard);

return HrDashboard;

});
