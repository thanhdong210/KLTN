from odoo import fields, models, _

class ResourceCalendarInherit(models.Model):
    _inherit = "resource.calendar"
    
    mode = fields.Selection([
        ('begin_end_time', 'By late or soon'),
        ('worked_hours', 'By worked hours'),
    ], string='Mode', store=True, tracking=True, copy=False, default="begin_end_time")
    hour_late = fields.Float(string="Hour late")
    hour_soon = fields.Float(string="Hour soon")
    hour_to_have_one_work_day = fields.Float(string="Hour to have one work day")
    hour_to_have_half_work_day = fields.Float(string="Hour to have half work day")
    


    
    

    
    



    

    


    


