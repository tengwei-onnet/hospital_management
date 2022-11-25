# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalBilling(models.Model):
    _name = "hospital.billing"
    _description = "Billing"
    _rec_name = 'ref'

    ref = fields.Char(string='Bill ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    doctor_charges = fields.Float(string='Doctor Fee', default=0, digits=(8, 2))
    nursing_charges = fields.Float(string='Nursing Fee', default=0, digits=(8, 2))
    ward_charges = fields.Float(string='Ward Fee', default=0, digits=(8, 2))
    medical_charges = fields.Float(string='Medical Fee', default=0, digits=(8, 2))
    test_charges = fields.Float(string='Lab Test Fee', default=0, digits=(8, 2))
    total_amount = fields.Float(string='Total Amount', default=0, digits=(8, 2), readonly='1', compute='calculate_total_price')
    date_issued = fields.Datetime(string='Date Issued', default=datetime.datetime.now().strftime('%Y-%m-%d 00:00:00'))
    date_paid = fields.Datetime(string='Date Paid', readonly=True)

    treatment_price = fields.Float(string='Treatment Fee', default=0, digits=(8, 2), compute='calculate_treatment_price')
    care_price = fields.Float(string='Care Fee', default=0, digits=(8, 2), compute='calculate_care_price')
    test_price = fields.Float(string='Lab Test Fee', default=0, digits=(8, 2), compute='calculate_test_price')

    medical_record_id = fields.Many2one(comodel_name='hospital.medical_record', string='Medical Report')
    patient_id = fields.Many2one(related='medical_record_id.patient_id')

    active = fields.Boolean(string='Active', default=True, readonly=True)
    cancel = fields.Boolean(string='Cancelled', default=False, invisible=True)

    @api.depends('doctor_charges', 'medical_charges')
    def calculate_treatment_price(self):
        for price in self:
            total_amount = price.doctor_charges + price.medical_charges
            price.treatment_price = total_amount

    @api.depends('nursing_charges', 'ward_charges')
    def calculate_care_price(self):
        for price in self:
            total_amount = price.nursing_charges + price.ward_charges
            price.care_price = total_amount

    @api.depends('test_charges')
    def calculate_test_price(self):
        for price in self:
            total_amount = price.test_charges
            price.test_price = total_amount

    @api.depends('treatment_price', 'care_price', 'test_price')
    def calculate_total_price(self):
        for price in self:
            total_amount = price.treatment_price + price.care_price + price.test_price
            price.total_amount = total_amount

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.billing') or _('New')
        res = super(HospitalBilling, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.billing') or _('New')
        return super(HospitalBilling, self).write(vals)

    def action_paid(self):
        for rec in self:
            rec.active = False
            rec.date_paid = fields.Datetime.now()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Patient Paid the Bill',
                'type': 'rainbow_man',
            }
        }

    def action_restore_bill(self):
        for rec in self:
            rec.active = True
            rec.cancel = False

    def action_cancel_bill(self):
        for rec in self:
            rec.active = False
            rec.cancel = True
