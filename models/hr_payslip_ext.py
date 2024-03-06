from odoo import fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        if self.date_from.month == self.date_to.month and self.date_from.year == self.date_to.year:
            current_payslip_month = self.date_from.month
            current_month_gratuity_rule = self.line_ids.filtered(lambda x: x.salary_rule_id.code == 'GRATUITY')
            current_month_gratuity_amount = (current_month_gratuity_rule or 0) and current_month_gratuity_rule.total
            current_gross_salary_rule = self.line_ids.filtered(lambda x: x.salary_rule_id.code == 'GROSS')
            current_income_tax_rule = self.line_ids.filtered(lambda y: y.salary_rule_id.is_income_tax_rule)
            current_exempt_from_tax_rules = self.line_ids.filtered(lambda y: y.salary_rule_id.exempt_from_tax and y.salary_rule_id.code != 'GRATUITY')
            # current_exempt_tax_ids = current_exempt_from_tax_rules.mapped('salary_rule_id.id')
            tax_years = self.env['calender.year'].search([])
            for tax_year in tax_years:
                if self.is_date_in_range(self.date_from, tax_year.start_date, tax_year.end_date):
                    selected_tax_year_months = tax_year.calender_month[1:]
                    tax_calc = self.env['tax.calculator'].search([('tax_year', '=', tax_year.id)], limit=1)
                    past_months = []
                    future_months = 0
                    past_income_tax_paid = 0
                    past_gross_income = 0
                    past_exempt_from_tax = 0
                    past_months_gratuity = 0
                    yearly_income_tax = 0
                    for tax_month in selected_tax_year_months:
                        if current_payslip_month == tax_month.start_date.month:
                            total_monthly_gross_salary = self.contract_id.promotion_allowance + self.contract_id.wage
                            future_months = 12 - future_months
                            past_payslips = []
                            if future_months <= 11:
                                payslips = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id), ('state', 'not in', ['draft', 'cancel'])])
                                for payslip in payslips:
                                    if (payslip.date_from.month, payslip.date_from.year) in past_months:
                                        past_payslips.append(payslip)
                                for past_payslip in past_payslips:
                                    past_payslip_gross = past_payslip.line_ids.filtered(lambda x: x.salary_rule_id.code == 'GROSS')
                                    past_month_gratuity_rule = past_payslip.line_ids.filtered(lambda x: x.salary_rule_id.code == 'GRATUITY')
                                    past_income_tax_rule = past_payslip.line_ids.filtered(lambda y: y.salary_rule_id.is_income_tax_rule)
                                    past_exempt_from_tax_rules = past_payslip.line_ids.filtered(lambda y: y.salary_rule_id.exempt_from_tax and y.salary_rule_id.code != 'GRATUITY')
                                    past_months_gratuity += (past_month_gratuity_rule or 0) and past_month_gratuity_rule.total
                                    past_gross_income += past_payslip_gross.total
                                    past_income_tax = past_income_tax_rule
                                    past_income_tax_paid += past_income_tax.total
                                    for past_exept in past_exempt_from_tax_rules:
                                        past_exempt_from_tax += past_exept.total
                            total_gratuity = past_months_gratuity + current_month_gratuity_amount
                            yearly_gross_salary = (total_monthly_gross_salary * (future_months-1)) + past_gross_income + current_gross_salary_rule.total
                            if yearly_gross_salary <= tax_calc.minimum_taxable_salary:
                                yearly_income_tax += (yearly_gross_salary * tax_calc.tax_on_min_salary)
                            else:
                                exempt_gross_amount = tax_calc.exempt_gross_income * yearly_gross_salary
                                higher_of_amount = tax_calc.higher_of_percentage * yearly_gross_salary
                                if higher_of_amount < tax_calc.higher_of_amount:
                                    higher_of_amount = tax_calc.higher_of_amount
                                exempt_tax_amount = 0
                                if current_exempt_from_tax_rules:
                                    for exempt_rule in current_exempt_from_tax_rules:
                                        exempt_tax_amount += abs(exempt_rule.total) * future_months
                                deducted_yearly_salary = yearly_gross_salary - exempt_gross_amount - exempt_tax_amount - higher_of_amount - past_exempt_from_tax - total_gratuity
                                previous_maximum = 0
                                for slab in tax_calc.slab_ids:
                                    if slab.minimum <= deducted_yearly_salary <= slab.maximum:
                                        deducted_yearly_salary -= previous_maximum
                                        yearly_income_tax = ((deducted_yearly_salary * slab.percentage) / 100) + slab.base
                                        break
                                    else:
                                        previous_maximum = slab.maximum
                            yearly_income_tax -= abs(past_income_tax_paid)
                            yearly_income_tax /= future_months
                            current_income_tax_rule.write({
                                'amount': -yearly_income_tax,
                                'total': -yearly_income_tax
                            })
                        else:
                            future_months += 1
                            past_months.append((tax_month.start_date.month, tax_month.start_date.year))
            return res

    def is_date_in_range(self, date, start_date, end_date):
        return start_date <= date <= end_date


