odoo.define('KLTN.Dashboard', function (require) {
    "use strict";


    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var QWeb = core.qweb;

    var HrDashboard = AbstractAction.extend({
        template: "KLTN.HrDashboardMain",
        events: {
            'click .display_attendance': 'display_attendance',
        },

        display_attendance: function (event) {
            var self = this;
            self.$el.html(QWeb.render('KLTN.HrAttendanceMode'));
        },

        init: function (parent, context) {
            this._super(parent, context);
            this.employee_login = false;
        },

        willStart: function () {
            var def = this._fetchDashboardDatas()
            return Promise.all([this._super.apply(this, arguments), def]);
        },

        _fetchDashboardDatas: function () {
            var self = this;
            var def1 = $.Deferred();
            this._rpc({
                model: 'hr.employee',
                method: 'get_detail_employee',
                args: [[this.login_employee]],
                context: session.user_context,
            }).then(function (result) {
                if (result && result.length) {
                    self.login_employee = result[0];
                }
                def1.resolve()
            });

            // var def1 = $.Deferred();
            // this._rpc({
            //     model: 'hr.employee',
            //     method: 'get_detail_employee',
            //     args: [[this.login_employee]],
            //     context: session.user_context,
            // }).then(function (result) {
            //     if (result && result.length) {
            //         self.login_employee = result[0];
            //     }
            //     def1.resolve()
            // });
            return def1;
        },

        start: function () {
            var self = this;
            if (self.login_employee) {
                self.$el.html(QWeb.render('KLTN.HrDashboardMain', { widget: self.login_employee }));
            }
        }

    });

    core.action_registry.add('hr_dashboard', HrDashboard);

    return HrDashboard;

});
