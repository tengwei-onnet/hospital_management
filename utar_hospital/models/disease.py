# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalDisease(models.Model):
    _name = "hospital.disease"
    _description = "Disease"
    _rec_name = 'ref'

    ref = fields.Char(string='Disease ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    disease_overview = fields.Html()
    disease_cause = fields.Char(string='Cause')
    disease_riskfactor = fields.Char(string='Risk Factor')
    disease_complication = fields.Char(string='Complication')
    disease_prevention = fields.Html()
    color = fields.Integer()

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.disease') or _('New')
        res = super(HospitalDisease, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.disease') or _('New')
        return super(HospitalDisease, self).write(vals)

    def name_get(self):
        return [(record.id, "(%s) %s" % (record.ref, record.name)) for record in self]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
