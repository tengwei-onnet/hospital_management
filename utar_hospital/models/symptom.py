from odoo import api, fields, models, _

class HospitalSymptom(models.Model):
    _name = "hospital.symptom"
    _description = "Symptom"
    _rec_name = 'ref'

    ref = fields.Char(string='Symptom ID', store=True, required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string='Name')
    symptom_description = fields.Char(string='Description')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.disease') or _('New')
        res = super(HospitalSymptom, self).create(vals)
        return res

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'hospital.disease') or _('New')
        return super(HospitalSymptom, self).write(vals)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name),
                     ('ref', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
