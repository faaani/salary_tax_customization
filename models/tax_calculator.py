# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TaxCalculator(models.Model):
    _name = 'tax.calculator'
    _description = "Tax Calculator"

    name = fields.Char(required=True)
    tax_year = fields.Many2one('calender.year')
    starting_date = fields.Date(related="tax_year.start_date")
    ending_date = fields.Date(related="tax_year.end_date")
    higher_of_amount = fields.Float()
    higher_of_percentage = fields.Float()
    exempt_gross_income = fields.Float()
    minimum_taxable_salary = fields.Float(string="Salary")
    tax_on_min_salary = fields.Float(string="Tax")
    slab_ids = fields.One2many('tax.slab', 'calculator_id')

    @api.constrains('slab_ids', 'starting_date', 'ending_date')
    def _check_double(self):

        record = self.search([('id', '!=', self.id),
                              '|',
                              '|',
                              '&',
                              ('starting_date', '<=', self.starting_date),
                              ('ending_date', '>=', self.starting_date),

                              '&',
                              ('starting_date', '<=', self.ending_date),
                              ('ending_date', '>=', self.ending_date),

                              '&',
                              ('starting_date', '>=', self.starting_date),
                              ('ending_date', '<=', self.ending_date),

                              ])

        if record:
            raise ValidationError(_("Dates are already fall in Price List :: %s" % (record.mapped('name')[0])))

    @api.onchange('slab_ids')
    def _seq_number(self):
        number = 1
        previous_maximum = 0
        previous_base = 0
        for rec in self.slab_ids:
            rec.sequence = number
            if rec.sequence >= 1:
                if rec.sequence == 1:
                    previous_maximum = rec.maximum
                elif rec.sequence > 1:
                    rec.minimum = previous_maximum + 1

                # if previous_base == 0:
                #     previous_base = (rec.maximum - (rec.minimum - 1)) * (rec.percentage / 100)
                #     rec.base = previous_base
                if previous_base >= 0:
                    if rec.base == 0:
                        rec.base = previous_base
                    previous_base = previous_base + ((rec.maximum - (rec.minimum - 1)) * (rec.percentage / 100))
                previous_maximum = rec.maximum
            number = number + 1


class TaxSlab(models.Model):
    _name = 'tax.slab'
    _description = "Tax Slab"
    _order = 'sequence, id'

    name = fields.Many2one('salary.category')
    minimum = fields.Integer()
    maximum = fields.Integer()
    base = fields.Float()
    sequence = fields.Integer()
    percentage = fields.Float()

    calculator_id = fields.Many2one('tax.calculator')

    @api.constrains('minimum', 'maximum')
    def _check_maximum(self):
        for order in self:
            if order.minimum > order.maximum:
                raise ValidationError(
                    _('Max value of slab : %s, is less then Minimum which should not.' % (order.name.name))
                )


class SalaryCategory(models.Model):
    _name = 'salary.category'
    _description = "Salary Category"

    name = fields.Char(required=True)
