# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class LanguageSpoke(models.Model):
    _name = "language.spoken"
    _description = "Language Spoken"

    name = fields.Char(string='Language')
    color = fields.Integer()

    _sql_constraints = [
        ('unique_category_name', 'unique(name)', 'Name must be unique')
    ]


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _description = "Doctor"
    _rec_name = 'ref'

    ref = fields.Char(string='Doctor ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    # department_id = fields.Many2one(comodel_name='hospital.department', string='Department', store=True)
    doc_email = fields.Char(string='Email Address')
    doc_ic = fields.Char(string='IC / Passport Number')
    doc_maritalStatus = fields.Selection([('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
                                         string='Marital Status')
    age = fields.Float(string='Age', compute='_compute_age', inverse='inverse_compute_age', readonly=True, store=True,
                       digits=(3, 0))
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    doc_DOB = fields.Date(string='Date Of Birth', store=True)
    doc_mobile = fields.Char(string="Phone Number", compute='validate_phone_no', store=True)
    doc_address = fields.Char(string='Address')
    doc_address_state = fields.Char(string='State')
    doc_country = fields.Char(string='Country')
    active = fields.Boolean(string='Active', default=True, readonly=True)

    doc_type = fields.Selection([('specialist', 'Specialist'), ('consultant', 'Consultant')], string='Doctor Type')
    doc_qualification = fields.Char(string='Qualification')
    doc_position = fields.Char(string='Position')
    doc_HOD = fields.Char(string='Head of Department')
    specialist_type = fields.Char(string='Speciality')
    language_id = fields.Many2many('language.spoken', string='Language Spoken')
    appointment_id = fields.One2many(comodel_name='hospital.appointment', inverse_name='doctor_id')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.doctor') or _('New')
        res = super(HospitalDoctor, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.doctor') or _('New')
        return super(HospitalDoctor, self).write(vals)

    @api.constrains('doc_DOB')
    def validate_dob(self):
        for rec in self:
            if rec.doc_DOB and rec.doc_DOB > fields.Date.today():
                raise ValidationError("Invalid Date of Birth, Please Enter Again")

    @api.constrains('doc_mobile')
    def validate_phone_no(self):
        if self.doc_mobile:
            match = re.match("(\\d{3}-\\d{7,8})", self.doc_mobile)
            if not match:
                raise ValidationError('Invalid Phone Number, Please follow this format "XXX-XXXXXXX"\neg: 016-9289983')

    @api.depends('doc_DOB')
    def _compute_age(self):
        for doc in self:
            if doc.doc_DOB:
                years = relativedelta(date.today(), doc.doc_DOB).years
                doc.age = int(years)
            else:
                doc.age = 0

    @api.depends('age')
    def inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.doc_DOB = today - relativedelta(years=rec.age)

    def name_get(self):
        return [(record.id, "(%s) %s" % (record.ref, record.name)) for record in self]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
