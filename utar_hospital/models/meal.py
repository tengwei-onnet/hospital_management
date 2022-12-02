# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalMeal(models.Model):
    _name = "hospital.meal"
    _description = "Meal"
    _rec_name = 'name'

    name = fields.Char(string='Name')
    meal_price = fields.Float(string='Meal Price per Day', default=0, digits=(8, 2))
    breakfast = fields.Char(string='Breakfast')
    lunch = fields.Char(string='Lunch')
    dinner = fields.Char(string='Dinner')
    is_muslim = fields.Boolean(string='Muslim', default=False)
    meal_type = fields.Selection([('regular_diet', 'Regular Diet'), ('mechanical_soft_diet', 'Mechanical Soft Diet'),
                                  ('full_liquid_diet', 'Full Liquid Diet'), ('vegetarian_diet', 'Vegetarian Diet')],
                                 string='Meal Type')
    meal_size = fields.Selection([('s_size', 'S'), ('m_size', 'M'), ('l_size', 'L')], string='Meal Size')

    def name_get(self):
        return [(record.id, "%s" % record.name) for record in self]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += [('name', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
