from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CalenderYear(models.Model):
    _name = 'calender.year'
    _description = 'Calender Year'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    code = fields.Char(string="Code", required=True)
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed'), ], default='open')
    name = fields.Char(required=True, string="Tax Calender")
    calender_month = fields.Many2many('calender.month', string="Details")
    company = fields.Many2one('res.company', required=True)

    _sql_constraints = [
        ('name', 'unique (name, company)', 'The name of the Calender Year must be unique!'),
    ]

    def period_close(self):
        account_move_obj = self.env['account.move'].search(
            [('date', '>=', self.start_date), ('date', '<=', self.end_date)
                , ('state', '=', 'draft'), ('company_id', '=', self.env.user.company_id.id)])
        account_invoice_obj = self.env['account.invoice'].search(
            [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date)
                , ('state', '=', 'draft'), ('type', '=', 'out_invoice'),
             ('company_id', '=', self.env.user.company_id.id)])
        account_vendor_bill_obj = self.env['account.invoice'].search(
            [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date)
                , ('state', '=', 'draft'), ('type', '=', 'in_invoice'),
             ('company_id', '=', self.env.user.company_id.id)])
        account_payment_obj = self.env['account.payment'].search(
            [('payment_date', '>=', self.start_date), ('payment_date', '<=', self.end_date)
                , ('state', '=', 'draft'), ('company_id', '=', self.env.user.company_id.id)])
        if account_move_obj:
            raise ValidationError("Please post all entries belongs to this Period")
        elif account_invoice_obj:
            raise ValidationError("Please validate all invoices belongs to this Period")
        elif account_vendor_bill_obj:
            raise ValidationError("Please validate all vendor bills belongs to this Period")
        elif account_payment_obj:
            raise ValidationError("Please post all payment belongs to this Period")
        else:
            self.write({'state': "closed"})

    def reopen_period(self):
        self.write({'state': "open"})

    def create_monthly_periods(self):
        """

        :return:
        """

        l = []
        start_date_object = datetime.strptime(str(self.start_date), "%Y-%m-%d")  # %Y-%m-%d
        end_date_object = datetime.strptime(str(self.end_date), "%Y-%m-%d")
        temp_start_date = start_date_object
        temp2_start_date = start_date_object
        # print("1")
        p = self.env['calender.month'].create({'name': 'opening-closing' + temp_start_date.strftime("%b-%Y"),

                                               'code': temp_start_date.strftime("%b-%Y"),
                                               'start_date': temp_start_date,
                                               'end_date': temp_start_date,
                                               'calender_year_id': self.id,
                                               'open_close': True,
                                               'state': "open"})
        l.append(p.id)

        while True:
            if temp_start_date > end_date_object:
                break

            temp2_start_date = temp_start_date + relativedelta(months=1, days=-1)
            p = self.env['calender.month'].create({'name': temp_start_date.strftime("%b-%Y"),
                                                   'code': temp_start_date.strftime("%b-%Y"),
                                                   'start_date': temp_start_date,
                                                   'end_date': temp2_start_date,
                                                   'calender_year_id': self.id,
                                                   'open_close': False,
                                                   'state': "open"})
            temp_start_date = temp_start_date + relativedelta(months=1)
            l.append(p.id)
        self.calender_month = [(6, 0, l)]
        self.env.cr.commit()


class CalenderMonth(models.Model):
    _name = 'calender.month'
    _description = 'calender month'

    name = fields.Char(string="Period Name ", required=True)
    code = fields.Char(string="Code ")
    calender_year_id = fields.Many2one('calender.year', string='Calender Year', ondelete="cascade")
    start_date = fields.Date(required=True, string="Start of Period", )
    end_date = fields.Date(required=True, string="End of period  ")
    open_close = fields.Boolean(string="Opening/Closing Period")
    company = fields.Many2one('res.company')
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed'), ], default='open')

    _sql_constraints = [
        ('name', 'unique (name, company)', 'The name of the Period must be unique!'),
    ]

    def period_close(self):
        account_move_obj = self.env['account.move'].search(
            [('date', '>=', self.start_date), ('date', '<=', self.end_date)
                , ('state', '=', 'draft'), ('company_id', '=', self.env.user.company_id.id)])
        account_invoice_obj = self.env['account.invoice'].search(
            [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date)
                , ('state', '=', 'draft'), ('type', '=', 'out_invoice'),
             ('company_id', '=', self.env.user.company_id.id)])
        account_vendor_bill_obj = self.env['account.invoice'].search(
            [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date)
                , ('state', '=', 'draft'), ('type', '=', 'in_invoice'),
             ('company_id', '=', self.env.user.company_id.id)])
        account_payment_obj = self.env['account.payment'].search(
            [('payment_date', '>=', self.start_date), ('payment_date', '<=', self.end_date)
                , ('state', '=', 'draft'), ('company_id', '=', self.env.user.company_id.id)])

        if account_move_obj:
            raise ValidationError("Please post all entries belongs to this Period")
        elif account_invoice_obj:
            raise ValidationError("Please validate all invoices belongs to this Period")
        elif account_vendor_bill_obj:
            raise ValidationError("Please validate all vendor bills belongs to this Period")
        elif account_payment_obj:
            raise ValidationError("Please post all payment belongs to this Period")
        else:
            self.write({'state': "closed"})

    def reopen_period(self):
        self.write({'state': "open"})


class AccountMove(models.Model):
    _inherit = "account.move"

    def post(self):
        for rec in self:
            date_jv = rec.date
            calender_year_obj = rec.env['calender.year'].search(
                [('start_date', '<=', date_jv), ('end_date', '>=', date_jv)])
            calender_month_obj = rec.env['calender.month'].search(
                [('open_close', '=', False), ('start_date', '<=', date_jv), ('end_date', '>=', date_jv)])

            inv_date = date_jv
            invdate_year = inv_date.year
            if calender_year_obj:
                if calender_year_obj[0].state != 'closed':
                    if calender_month_obj:
                        if calender_month_obj[0].state != 'closed':
                            return super(AccountMove, rec).post()

                        else:
                            raise ValidationError(
                                "You are trying to access %r calender month that is already closed" %
                                calender_month_obj[
                                    0].name)
                    else:
                        raise ValidationError("month not found")

                else:
                    raise ValidationError(
                        "You are trying to access %r calender year that is already closed" % calender_year_obj[0].name)
            else:
                raise ValidationError("year not found")
