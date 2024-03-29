# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class LegalReportsTax(models.Model):
    _name = 'legal.reports.tax'
    _description = 'Informes Legales de Impuestos y Retenciones'

    name = fields.Char(
        string='Nombre',
    )
    # Revisar la forma de armar este filtro desde el GUI
    tax_domain = fields.Char(
        string='Filtro',
        default="[('type_tax_use','=','purchase'),('description','ilike','ICA%')]",
    )
    tax_ids = fields.Many2many(
        string='Impuesto(s)/Retencione(s)',
        comodel_name='account.tax',
    )
    template_id = fields.Many2one(
        string='Plantilla informe',
        comodel_name='ir.actions.report',
    )

    def update_tax(self, vals):
        if vals.get('tax_domain') and not vals.get('tax_ids'):
            tax_domain = vals.get('tax_domain')
            tax_ids = False
            try:
                tax_ids = self.env['account.tax'].search(
                    eval( tax_domain )
                )
                vals.update({
                    'tax_ids': [(6, 0, tax_ids.ids)]
                })
            except:
                _logger.debug('Error en el filtro "%s"' % ( tax_domain ))
                raise ValidationError(
                    'Error en el filtro "%s"' % ( tax_domain )
                )
        return vals

    @api.model
    def write(self, vals):
        vals = self.update_tax(vals)
        super(LegalReportsTax, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self.update_tax(vals)
        return super(LegalReportsTax, self).create(vals)

    @api.onchange('tax_domain', )
    def _onchange_field(self):
        if self.tax_domain:
            try:
                self.tax_ids = self.env['account.tax'].search(
                    eval( self.tax_domain )
                )
            except:
                raise ValidationError(
                    'Error en el filtro "%s"' % (self.tax_domain)
                )
