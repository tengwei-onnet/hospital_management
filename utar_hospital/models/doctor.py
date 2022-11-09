# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _description = "Doctor"

    name = fields.Char(string='Name')
    position = fields.Char(string='Position')
    specialized = fields.Char(string='Expert of Field')
    dob = fields.Date(string='Date Of Birth')
    age = fields.Float(string='Age', compute='_compute_age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')

    @api.depends('dob')
    def _compute_age(self):
        if self.dob:
            self.age = (datetime.datetime.now() - self.dob).days / 365
        else:
            self.age = 0




