# -*- coding: utf-8 -*-
import datetime
import datetime
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo import api, fields, models


class HospitalRoom(models.Model):
    _name = "hospital.room"
    _description = "Hospital Room"
    _rec_name = 'ref'

    ref = fields.Char(string='Room ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    ward_ids = fields.One2many(comodel_name='hospital.ward', inverse_name='room_id')
    room_type = fields.Selection(
        [('general_ward', 'General Wards'), ('critical_care', 'Critical Care'), ('isolation_room', 'Isolation Room'),
         ('day_care', 'Day Care'), ('nursery', 'Nursery')], string='Room Type')
    room_block = fields.Selection([('blockA', 'A'), ('blockB', 'B'), ('blockC', 'C'), ('blockD', 'D')], string='Block',
                                  required=True)
    room_floor = fields.Integer(string='Floor')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.room') or _('New')

        res = super(HospitalRoom, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.room') or _('New')
        return super(HospitalRoom, self).write(vals)


class HospitalWard(models.Model):
    _name = "hospital.ward"
    _description = "Room Ward"
    _rec_name = 'ref'

    ref = fields.Char(string='Ward ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    room_id = fields.Many2one(comodel_name='hospital.room', string='Room', store=True)
    ward_price = fields.Float(string='Price for Ward', default=0, digits=(8, 2))
    ward_type = fields.Selection(
        [('deluxe_suite', 'Deluxe Suite'), ('single_bedded', 'Single Bedded'), ('two_bedded', 'Two Bedded'),
         ('four_bedded', 'Four Bedded'), ('high_dependency', 'High Dependency Unit'),
         ('intensive_care', 'Intensive Care Unit'),
         ('isolation_icu', 'Isolation ICU'), ('adult', 'Adult'), ('paediatric', 'Paediatric'),
         ('day_care', 'Day Care Ward'), ('nursery', 'Nursery'), ('incubator', 'Incubator')], string='Ward Type')
    available = fields.Boolean(string='Available', default=True)
    ward_block = fields.Selection(string='Block', related='room_id.room_block', readonly=True, invisible=True, store=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.ward') or _('New')
        res = super(HospitalWard, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.ward') or _('New')
        return super(HospitalWard, self).write(vals)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('room_id.ref', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
    
    def name_get(self):
        return [(record.id, "%s - %s" % (record.ref, record.room_id.ref)) for record in self]
