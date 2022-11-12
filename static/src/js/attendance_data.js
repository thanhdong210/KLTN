odoo.define('kltn.AttendanceDataTemplate', function (require) {
    "use strict";


    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var QWeb = core.qweb;

    var AttendanceDataTemplate = AbstractAction.extend({
        template: "kltn.AttendanceDataTemplate",
        

        start: function () {
            var self = this;
            if (self.login_employee) {
                self.$el.html(QWeb.render('kltn.AttendanceDataTemplate', { widget: self.login_employee }));
            }
        }

    });

    core.action_registry.add('hr_attendance_data', AttendanceDataTemplate);

    return AttendanceDataTemplate;

});
