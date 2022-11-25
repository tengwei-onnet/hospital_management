# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class RiskFactor(models.Model):
    _name = "risk.factor"
    _description = "RiskFactor"

    name = fields.Char(string='Risk Factor(s)')
    color = fields.Integer()

    _sql_constraints = [
        ('unique_category_name', 'unique(name)', 'Name must be unique.')
    ]


class Complication(models.Model):
    _name = "complication"
    _description = "Disease(s) or Condition(s) that Aggravating an existing Disease. "

    name = fields.Char(string='Complication(s)')
    color = fields.Integer()

    _sql_constraints = [
        ('unique_category_name', 'unique(name)', 'Name must be unique.')
    ]


class Prevention(models.Model):
    _name = "prevention"
    _description = "Methods of Preventing an Disease. "

    name = fields.Char(string='Prevention Methods(s)')
    color = fields.Integer()

    _sql_constraints = [
        ('unique_category_name', 'unique(name)', 'Name must be unique.')
    ]


class HospitalDisease(models.Model):
    _name = "hospital.symptom"
    _description = "Symptom"
    _rec_name = 'ref'

    ref = fields.Char(string='Disease ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    disease_overview = fields.Char(string='Overview')
    riskfactor_id = fields.Many2many('risk.factor', string='RiskFactor')
    complication_id = fields.Many2many('complication', string='Complication')
    prevention_id = fields.Many2many('prevention', string='Prevention')

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

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)



