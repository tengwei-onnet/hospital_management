from odoo import api, fields, models, _


class HospitalDiagnosis(models.Model):
    _name = "hospital.diagnosis"
    _description = "Diagnosis"
    _rec_name = 'ref'

    ref = fields.Char(string='Diagnosis ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    diagnosis_description = fields.Char(string='Description')
    risk_id = fields.Many2many('risk', string='Risk')
    expect_id = fields.Many2many('complication', string='Complication')
    result_id = fields.Many2many('prevention', string='Prevention')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.diagnosis') or _('New')
        res = super(HospitalDiagnosis, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.diagnosis') or _('New')
        return super(HospitalDiagnosis, self).write(vals)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
