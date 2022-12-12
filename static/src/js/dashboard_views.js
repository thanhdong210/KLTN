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
            'click div.o_attendance_request': 'open_action_attendance_request',
            'click div.o_business_trip': 'open_action_business_trip',
            'click div.o_leave_request': 'open_action_leave_request',
            'click div.o_overtime_request': 'open_action_overtime_request',
        },

        display_attendance: function (event) {
            var self = this;
            self.$el.html(QWeb.render('kltn.HrAttendanceMode'));
        },

        init: function (parent, context) {
            this._super(parent, context);
            this.employee_login = false;
            this.employee_member = false;


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
                    self.employee_member = result[0].team_member;
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
            if (self.login_employee) {
                self.$el.html(QWeb.render('kltn.HrDashboardMain', {
                    the_widget: self,
                    widget: self.login_employee,
                    employee_name: self.login_employee['employee'][0]['name'],
                    employee_department: self.login_employee['employee'][0]['department_id'][1],
                    employee_id: self.login_employee['employee'][0]['id'],
                    employee_job: self.login_employee['employee'][0]['job_title'],
                    employee_email: self.login_employee['employee'][0]['work_email'],
                    employee_phone: self.login_employee['employee'][0]['work_phone'],
                    team_member: self.employee_member,
                }));
            }

            if (self.employee_member) {
                self.$el.find('.o_hrms_team_member').html(QWeb.render('HrTeammember', { team_member: self.employee_member }));
            }
        },

        open_action_attendance_request: function(event){
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: "Attendance Request",
                type: 'ir.actions.act_window',
                res_model: 'hr.attendance.request',
                views: [[false, 'list'], [false, 'form']],
                domain: [['attendance_option', '=', 'attendance_request'], ['id', 'in', this.login_employee['attendance_request_to_approve_ids']]],
                context: {
                    'create': false,
                },
                target: 'current'
            })
        },

        open_action_business_trip: function(event){
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: "Business Trip",
                type: 'ir.actions.act_window',
                res_model: 'hr.attendance.request',
                views: [[false, 'list'], [false, 'form']],
                domain: [['attendance_option', '=', 'business_trip'], ['id', 'in', this.login_employee['business_trip_to_approve_ids']]],
                context: {
                    'create': false,
                },
                target: 'current'
            })
        },

        open_action_leave_request: function(event){
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: "Leave Request",
                type: 'ir.actions.act_window',
                res_model: 'hr.leave.inherit',
                views: [[false, 'list'], [false, 'form']],
                domain: [['id', 'in', this.login_employee['leave_request_to_approve_ids']]],
                context: {
                    'create': false,
                },
                target: 'current'
            })
        },

        open_action_overtime_request: function(event){
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: "Overtime Request",
                type: 'ir.actions.act_window',
                res_model: 'hr.overtime.request',
                views: [[false, 'list'], [false, 'form']],
                domain: [['id', 'in', this.login_employee['overtime_request_to_approve_ids']]],
                context: {
                    'create': false,
                },
                target: 'current'
            })
        },

    });

    core.action_registry.add('hr_dashboard', HrDashboard);

    return HrDashboard;

});
