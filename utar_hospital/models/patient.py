# -*- coding: utf-8 -*-
import datetime
import re
from datetime import date, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"
    _rec_name = 'ref'

    ref = fields.Char(string='Patient ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    pat_email = fields.Char(string='Email Address')
    pat_ic = fields.Char(string='IC / Passport Number')
    pat_maritalStatus = fields.Selection([('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
                                         string='Marital Status')
    age = fields.Float(string='Age', compute='_compute_age', inverse='inverse_compute_age', readonly=True, store=True,
                       digits=(3, 0))

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', store=True)
    pat_DOB = fields.Date(string='Date Of Birth', store=True)
    pat_height = fields.Integer(string='Height (cm)')
    pat_weight = fields.Float(string='Weight (kg)')
    pat_mobile = fields.Char(string="Phone Number", compute='validate_phone_no', store=True)
    pat_address = fields.Char(string='Address')
    pat_address_state = fields.Char(string='State')
    pat_country = fields.Char(string='Country')
    pat_bloodType = fields.Selection([('o1', 'O'), ('o2', 'O+'), ('o3', 'O-'),
                                      ('a1', 'A'), ('a2', 'A+'), ('a3', 'A-'),
                                      ('b1', 'B'), ('b2', 'B+'), ('b3', 'B-'),
                                      ('ab1', 'AB'), ('ab2', 'AB+'), ('ab3', 'AB-')], string='Blood Type', store=True)
    pat_insurance_name = fields.Char(string='Insurance Name')
    insurance_attachment_id = fields.Many2many('ir.attachment', string="Attachment")
    pat_allergic = fields.Html()
    appointment_id = fields.One2many(comodel_name='hospital.appointment', inverse_name='patient_id')
    active = fields.Boolean(string='Active', default=True, readonly=True)
    bmi_value = fields.Float(string='BMI', compute='calculate_bmi', readonly=True, store=True)
    bmi_result = fields.Char(string='BMI Result', compute='determine_bmi', readonly=True, store=True)
    favourite_ward_type = fields.Selection(
        [('normal', 'Normal'), ('premier', 'Premier'), ('premier_executive', 'Premier Executive'),
         ('single_executive', 'Single Executive')], string='Favourite Ward Type', default='normal'
    )
    medical_record_ids = fields.One2many(comodel_name='hospital.medical_record', inverse_name='patient_id')

    @api.depends('bmi_value')
    def determine_bmi(self):
        for rec in self:
            BMI = rec.bmi_value

            if BMI <= 18.4:
                bmi_result = "BMI Result: Patient is underweight."
            elif BMI <= 24.9:
                bmi_result = "BMI Result: Patient is healthy."
            elif BMI <= 29.9:
                bmi_result = "BMI Result: Patient is over weight."
            elif BMI <= 34.9:
                bmi_result = "BMI Result: Patient is severely over weight."
            elif BMI <= 39.9:
                bmi_result = "BMI Result: Patient is obese."
            else:
                bmi_result = "BMI Result: Patient is severely obese."
            rec.bmi_result = bmi_result

    @api.depends('pat_height', 'pat_weight')
    def calculate_bmi(self):
        for rec in self:
            if rec.pat_height != 0:
                bmi = rec.pat_weight / (rec.pat_height/100)**2
            else:
                bmi = 0

            rec.bmi_value = bmi

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.patient') or _('New')
        res = super(HospitalPatient, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.patient') or _('New')
        return super(HospitalPatient, self).write(vals)

    @api.constrains('pat_DOB')
    def validate_dob(self):
        for rec in self:
            if rec.pat_DOB and rec.pat_DOB > fields.Date.today():
                raise ValidationError("Invalid Date of Birth, Please Enter Again")

    @api.constrains('pat_mobile')
    def validate_phone_no(self):
        if self.pat_mobile:
            match = re.match("(\\d{3}-\\d{7,8})", self.pat_mobile)
            if not match:
                raise ValidationError('Invalid Phone Number, Please follow this format "XXX-XXXXXXX"\neg: 016-9289983')

    @api.depends('pat_DOB')
    def _compute_age(self):
        for doc in self:
            if doc.pat_DOB:
                years = relativedelta(date.today(), doc.pat_DOB).years
                months = relativedelta(date.today(), self.pat_DOB).months
                day = relativedelta(date.today(), self.pat_DOB).days
                doc.age = int(years)
            else:
                doc.age = 0

    @api.depends('age')
    def inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.pat_DOB = today - relativedelta(years=rec.age)

    def schedule_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.appointment',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('utar_hospital.view_hospital_appointment_form').id,
            'target': 'new',
            'context': {'patient_id': self.id}
        }

    def create_medical_record(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.medical_record',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('utar_hospital.view_hospital_medical_record_form').id,
            'target': 'new',
            'context': {'patient_id': self.id}
        }

    def name_get(self):
        return [(record.id, "(%s) %s" % (record.ref, record.name)) for record in self]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _description = "Patient Appointment"
    _rec_name = 'ref'

    @api.model
    def default_get(self, fields):
        res = super(HospitalAppointment, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['patient_id'] = self.env.context.get('active_id')
        return res

    date = fields.Datetime(string="Date Appointment", required=True)
    ref = fields.Char(string='Appointment ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    description = fields.Text(string='Description')
    patient_id = fields.Many2one(comodel_name='hospital.patient', string='Patient', store=True)
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', string='Doctor', store=True)
    active = fields.Boolean(string='Active', default=True, readonly=True)

    patient_phone_no = fields.Char(string="Phone Number", related='patient_id.pat_mobile', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.appointment') or _('New')
        res = super(HospitalAppointment, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.appointment') or _('New')
        return super(HospitalAppointment, self).write(vals)

    def complete_appointment(self):
        for rec in self:
            rec.active = False
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'This Appointment has Completed',
                    'type': 'rainbow_man',
                }
            }

    def action_send_whatsapp(self):
        if not self.patient_phone_no:
            raise ValidationError("Missing phone number in this record")

        new_str = self.patient_id.pat_mobile
        valid_phone_no = new_str.replace("-", "")
        dt = self.date
        dt_plus_12 = dt + timedelta(hours=8)

        msg = "Good Day Sir/Miss, here is _UTAR Hospital_. Your *appointment* is verified. *Please arrive one hours before the appointment time.*" + \
              "%0aFull Name:%09" + str(self.patient_id.name) + "%0aIC No:%09%09" + str(self.patient_id.pat_ic) + \
              "%0aPhone No:%09" + str(self.patient_id.pat_mobile) + "%0aEmail:%09%09" + str(self.patient_id.pat_email) + \
              "%0aDoctor:%09%09" + str(self.doctor_id.name) + "%0aAppointment Date:%09" + str(dt_plus_12)

        whatsapp_url = 'https://api.whatsapp.com/send?phone=+6' + valid_phone_no + '&text=' + msg

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_url
        }
