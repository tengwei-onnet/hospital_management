# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalMedicalRecord(models.Model):
    _name = "hospital.medical_record"
    _description = "Hospital Medical Record"
    _rec_name = 'ref'

    @api.model
    def default_get(self, fields):
        res = super(HospitalMedicalRecord, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['patient_id'] = self.env.context.get('active_id')
        return res

    ref = fields.Char(string='Medical Record ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(comodel_name='hospital.patient', string='Patient', store=True, required=True)
    doctor_id = fields.Many2one(comodel_name='hospital.doctor', string='Doctor', store=True, required=True)
    ward_id = fields.Many2one(comodel_name='hospital.ward', string='Ward', store=True, domain="[('available', '=', True)]")
    disease_id = fields.Many2many(comodel_name='hospital.disease', string='Disease', store=True)
    meal_id = fields.Many2one(comodel_name='hospital.meal', string='Meal', store=True)

    doctor_phone_no = fields.Char(string="Phone Number", related='doctor_id.doc_mobile', invisible=True)

    ward_type = fields.Selection(related='ward_id.ward_type', string='Ward Type')

    rep_type = fields.Selection(
        [('inpatient', 'Inpatient'), ('outpatient', 'Outpatient')], string='Patient Type', default='outpatient')
    rep_date = fields.Date(string='Report Date', tracking=True, default=fields.Date.context_today)
    medicine_id = fields.Many2many(comodel_name='product.product', string='Medicine', store=True)
    rep_description = fields.Html()
    rep_anticipated_discharge_date = fields.Date(string='Date Discharge')
    rep_checkoutDate = fields.Date(string='CheckOut Date')
    rep_checkinDate = fields.Date(string='CheckIn Date')
    active = fields.Boolean(string='Active', default=True, readonly=True)
    remark = fields.Html()

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

    def action_send_whatsapp(self):
        if not self.doctor_phone_no:
            raise ValidationError("Missing phone number in this record")

        new_str = self.doctor_id.doc_mobile
        valid_phone_no = new_str.replace("-", "")

        msg = "Good Day Dr " + self.doctor_id.name + ", your in-charged patient is planned to be discharged tomorrow." + \
              "%0aFull Name:%09%09%09%09" + str(self.patient_id.name) + "%0aMedical Record ID:%09%09%09" + str(self.ref) + \
              "%0aRoom No:%09%09%09%09" + str(self.ward_id.room_id.ref) + "%0aWard No:%09%09%09%09%09" + str(self.ward_id.ref) + \
              "%0aAnticipated discharge date:%09" + str(self.rep_anticipated_discharge_date)

        whatsapp_url = 'https://api.whatsapp.com/send?phone=+6' + valid_phone_no + '&text=' + msg

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_url
        }
