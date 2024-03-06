# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    exempt_from_tax = fields.Boolean()
    is_income_tax_rule = fields.Boolean()