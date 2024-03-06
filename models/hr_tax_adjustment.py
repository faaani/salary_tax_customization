# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EmployeeExt(models.Model):
    _inherit = 'hr.employee'

    tax_adjustment_ids = fields.One2many('hr.tax.adjustment', 'employee_id')


class HrTaxAdjustment(models.Model):
    _name = 'hr.tax.adjustment'
    _description = 'Hr Tax Adjustment'

    employee_id = fields.Many2one('hr.employee')
    tax_year = fields.Many2one('calender.year')
    previous_income = fields.Float(string='Previous Income')
    category = fields.Char()
    amount = fields.Float(string='Tax Deducted')
