odoo.define('kltn.Dashboard', function (require) {
    "use strict";


    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var session = require('web.session');
    var QWeb = core.qweb;

    var HrDashboard = AbstractAction.extend({
        template: "kltn.HrDashboardMain",
        events: {
            'click .display_attendance': 'display_attendance',
        },

        display_attendance: function (event) {
            var self = this;
            self.$el.html(QWeb.render('kltn.HrAttendanceMode'));
        },

        init: function (parent, context) {
            this._super(parent, context);
            this.employee_login = false;
            this.teammember_list = false;
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
                    // self.teammember_list = result[0]['team_member'];
                }
                def1.resolve()
            });

            // var def2 = $.Deferred();
            // this._rpc({
            //     model: 'hr.employee',
            //     method: 'get_detail_employee',
            //     args: [[this.login_employee]],
            //     context: session.user_context,
            // }).then(function (result) {
            //     if (result && result.length) {
            //         self.teammember_list = [1, 2, 3, 4, 5];
            //     }
            //     def2.resolve()
            // });
            return def1;
        },

        start: function () {
            var self = this;
            
            // for (let i = 0; i < self.login_employee['team_member'].length; i++) {
            //     console.log("@@@@@@@", self.login_employee['team_member'][i].name);
            // } 
            // self.teammember_list = [1, 2, 3, 4, 5]
            console.log("@@@@@@@", self.teammember_list)
            if (self.login_employee) {
                self.$el.html(QWeb.render('kltn.HrDashboardMain', {
                    widget: self.login_employee,
                    employee_name: self.login_employee['employee'][0]['name'],
                    employee_department: self.login_employee['employee'][0]['department_id'][1],
                    employee_id: self.login_employee['employee'][0]['id'],
                    employee_job: self.login_employee['employee'][0]['job_title'],
                    employee_email: self.login_employee['employee'][0]['work_email'],
                    employee_phone: self.login_employee['employee'][0]['work_phone'],
                    team_member: self.teammember_list,
                }));
            }
            // console.log("@@@@@@@", self.teammember_list)
        }



    });

    core.action_registry.add('hr_dashboard', HrDashboard);

    return HrDashboard;

});
