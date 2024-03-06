from odoo import fields, models, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    promotion_allowance = fields.Monetary()
    health_insurance = fields.Monetary()
