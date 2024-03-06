{
    'name': 'Human Resources Tax',
    'version': '16.0.0.0.0',
    'summary': 'A module to cater payroll tax needs for organizations',
    'description': 'A module to cater payroll tax needs for organizations',
    'category': 'Human Resources',
    'author': 'Farhan Ashraf',
    'depends': ['hr_payroll', 'sale', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'views/hr_employee.xml',
        'views/tax_calculator.xml',
        'views/calender_year.xml',
        'views/hr_contract_views_ext.xml',
        'views/hr_salary_rule_views_ext.xml',
    ],
    'installable': True,
    'auto_install': False,

}
