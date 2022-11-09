# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"
    name = fields.Char(string='Name')
    ref = fields.Char(string='Reference')
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    appointment_id = fields.One2many(comodel_name='hospital.appointment', inverse_name='patient_id')


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _description = "Patient Appointment"
    date = fields.Date(string="Date Appointment")
    ref = fields.Char(string='Reference')
    description = fields.Text(string='Description')
    patient_id = fields.Many2one(comodel_name='hospital.patient')


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




