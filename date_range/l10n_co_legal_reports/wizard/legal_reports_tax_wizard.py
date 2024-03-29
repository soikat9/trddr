# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RetentionReportTaxWizard(models.TransientModel):
    _name = 'legal.reports.tax.wizard'
    _description = 'Informes Legales de Impuestos y Retenciones Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Compañia',
        required=False,
        ondelete='cascade',
    )
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Rango de Fecha',
    )
    date_from = fields.Date(
        string="Desde",
        required=True
    )
    date_to = fields.Date(
        string="Hasta",
        required=True
    )
    legal_reports_tax_id = fields.Many2one(
        string="Informe de Impuestos y Retenciones",
        comodel_name="legal.reports.tax",
        required=True,
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Terceros',
        required=True,
    )

    @api.onchange("date_range_id", )
    def _onchange_date_range_id(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def generate_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'wizard_values': self.read()[0],
            'tax_ids': self.legal_reports_tax_id.tax_ids.ids,
            'company_id': self.company_id.id,
            'partner_ids': self.partner_ids.ids,
        }
        return self.env.ref('l10n_co_legal_reports.action_legal_report_tax_certification').report_action(self, data=data)

    def button_export_html(self):
        self.ensure_one()
        """
        action = self.env.ref(
            'account_financial_report.action_report_general_ledger')
        """
        action_data = action.read()[0]
        context1 = action_data.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_general_ledger']
        report = model.create(self._prepare_report_general_ledger())
        report.compute_data_for_report()
        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        action_data['context'] = context1
        return action_data

    def button_export_pdf(self):
        self.ensure_one()
        report_type = 'qweb-pdf'
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = 'xlsx'
        return self._export(report_type)
