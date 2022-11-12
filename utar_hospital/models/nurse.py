# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalNurse(models.Model):
    _name = "hospital.nurse"
    _description = "Nurse"
    _rec_name = 'ref'

    ref = fields.Char(string='Nurse ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    nurse_position = fields.Char(string='Position')
    # department_id = fields.Many2one(comodel_name='hospital.department', string='Department', store=True)
    nurse_email = fields.Char(string='Email Address')
    nurse_ic = fields.Char(string='IC / Passport Number')
    nurse_maritalStatus = fields.Selection([('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
                                         string='Marital Status')
    age = fields.Float(string='Age', compute='_compute_age', inverse='inverse_compute_age', readonly=True, store=True,
                       digits=(3, 0))
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    nurse_DOB = fields.Date(string='Date Of Birth', store=True)
    nurse_mobile = fields.Char(string="Phone Number", compute='validate_phone_no', store=True)
    nurse_address = fields.Char(string='Address')
    nurse_address_state = fields.Char(string='State')
    nurse_country = fields.Char(string='Country')

    active = fields.Boolean(string='Active', default=True, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.nurse') or _('New')
        res = super(HospitalNurse, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.nurse') or _('New')
        return super(HospitalNurse, self).write(vals)

    @api.constrains('nurse_DOB')
    def validate_dob(self):
        for rec in self:
            if rec.nurse_DOB and rec.nurse_DOB > fields.Date.today():
                raise ValidationError("Invalid Date of Birth, Please Enter Again")

    @api.constrains('nurse_mobile')
    def validate_phone_no(self):
        if self.nurse_mobile:
            match = re.match("(\\d{3}-\\d{7,8})", self.nurse_mobile)
            if not match:
                raise ValidationError('Invalid Phone Number, Please follow this format "XXX-XXXXXXX"\neg: 016-9289983')

    @api.depends('nurse_DOB')
    def _compute_age(self):
        for nurse in self:
            if nurse.nurse_DOB:
                years = relativedelta(date.today(), nurse.nurse_DOB).years
                nurse.age = int(years)
            else:
                nurse.age = 0

    @api.depends('age')
    def inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.nurse_DOB = today - relativedelta(years=rec.age)

    def name_get(self):
        return [(record.id, "(%s) %s" % (record.ref, record.name)) for record in self]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
