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
    doctor_charges = fields.Float(string='Doctor Fee')
    nursing_charges = fields.Float(string='Nursing Fee')
    ward_charges = fields.Float(string='Ward Fee')
    medical_charges = fields.Float(string='Medical Fee')
    test_charges = fields.Float(string='Test Fee')
    amount = fields.Float(string='Amount')

    patient_id = fields.Many2one(comodel_name='hospital.patient', string='Patient', store=True)
    active = fields.Boolean(string='Active', default=True, readonly=True)


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

