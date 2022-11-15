# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalMedicalRecord(models.Model):
    _name = "hospital.medical_record"
    _description = "Hospital Medical Record"
    _rec_name = 'ref'

    ref = fields.Char(string='Medical Record ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(comodel_name='hospital.patient', string='Patient', store=True, required=True)
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', string='Doctor', store=True, required=True)

    rep_type = fields.Selection(
        [('inpatient', 'Inpatient'), ('outpatient', 'Outpatient')], string='Patient Type', default='outpatient')
    rep_date = fields.Date(string='Report Date', tracking=True, default=fields.Date.context_today)
    rep_medicine = fields.Char(string='Medicine')
    rep_description = fields.Html()
    rep_anticipated_discharge_date = fields.Date(string='Date Discharge')
    rep_checkoutDate = fields.Date(string='CheckOut Date')
    rep_checkinDate = fields.Date(string='CheckIn Date')
    active = fields.Boolean(string='Active', default=True, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.medical_record') or _('New')

        res = super(HospitalMedicalRecord, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.medical_record') or _('New')
        return super(HospitalMedicalRecord, self).write(vals)
