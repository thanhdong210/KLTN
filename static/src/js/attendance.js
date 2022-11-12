odoo.define('KLTN.attendance', function (require) {
    "use strict";


    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var QWeb = core.qweb;

    var HrAttendanceMode = AbstractAction.extend({
        template: "KLTN.HrAttendanceMode",
        events: {
            'click .display': 'raise_alert',
        },

        raise_alert: function (event) {
            alert("hello");
        },
    });

    core.action_registry.add('hr_dashboard', HrAttendanceMode);

    return HrAttendanceMode;

});