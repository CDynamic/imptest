# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ve_document_number = fields.Char(
        'Control Number', size=80,
        help="Number used to manage pre-printed invoices, by law you will"
             " need to put here this number to be able to declarate on"
             " Fiscal reports correctly.",store=True)

    withholding_data = fields.Boolean(
        
        help = 'a flag is set to notify that the hold was created'
    )

    withholding_iva_id = fields.Many2one('whithholdings.iva',string='idretenido',required=False)

    def _get_fiscal_period(self, date):
        
        str_date = str(date).split('-')
        vals = 'AÑO '+str_date[0]+' MES '+str_date[1]
        print(date,vals)
        return vals


    def get_partner_alicuot(self, partner):
        self.ensure_one()
        
        if partner.vat_retention:
            alicuot = partner.vat_retention
        else:
            raise UserError(_(
                'Si utiliza Cálculo de impuestos igual a "Alícuota en el '
                'Partner", debe setear el campo de retención de IVA'
                ' en la ficha del partner, seccion Compra'))

        return alicuot

    def compute_withholdings_move(self):
        ret_IVA = self.commercial_partner_id.browse(self.company_id.id)
        tax_totals = json.loads(self.tax_totals_json)
        to_pay_move_lines = self.open_move_line_ids
        iva = tax_totals['groups_by_subtotal']['Base imponible'][0]['tax_group_name'].split(' ')[1].replace('%',"")
        if not to_pay_move_lines:
            raise UserError(_('Nothing to be paid on selected entries'))
        to_pay_partners = self.mapped('commercial_partner_id')
        if len(to_pay_partners) > 1:
            raise UserError(_('Selected recrods must be of the same partner'))

        if tax_totals['amount_total'] > tax_totals['amount_untaxed']:
            if tax_totals['groups_by_subtotal']['Base imponible'][0]['tax_group_name'].find('IVA') > -1:
                selected_debt_taxed = tax_totals['groups_by_subtotal']['Base imponible'][0]['tax_group_amount']

        alicuota = int(ret_IVA.vat_retention) / 100.0
        
        amount =  self.amount_tax * (alicuota)
        ret_IVA.vat_retention
        print(self)
        vals ={
            'report_date' : self.invoice_date,
            'invoice' : self.ref,
            'Núm_Control' : self.l10n_ve_document_number,
            'Núm_ND' : '',
            'Núm_NC' : '',
            'Total_Compra_con_IVA' : self.amount_total,
            'Compras_sin_crédito' : '',
            'Base_Imponible' : self.amount_untaxed,
            'Alicuota' : iva,
            'Monto_IVA' : self.amount_tax,
            'IVA_Retenido' : amount,
            
        }
       
       
        # if self.withholding_data == False:
        #     try:
        iva_id = self.env['whithholdings.iva'].create(vals)
        self.write({'withholding_data':True, 'withholding_iva_id':iva_id})
        

            # except:
            #     raise UserError(_('withholding could not be calculated'))
        # else: 

        #     raise UserError(_('withholding could not be calculateds '))


    def get_taxes_values(self):
        """
        Hacemos esto para disponer de fecha de factura y cia para calcular
        impuesto con código python.
        Aparentemente no se puede cambiar el contexto a cosas que se llaman
        desde un onchange (ver https://github.com/odoo/odoo/issues/7472)
        entonces usamos este artilugio
        """
        invoice_date = self.invoice_date or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
        try:
            self.env.context.invoice_date = invoice_date
            self.env.context.invoice_company = self.company_id
        except Exception:
            pass
        return super().get_taxes_values()

    def _post(self, soft):
        super(AccountMove, self)._post(soft)
        for rec in self:
            if (rec.state == 'posted' and rec.\
                l10n_ve_document_number == False) or rec.\
                    move_type == 'out_refund' and rec.l10n_ve_document_number == '':
                if rec.move_type in ['out_invoice', 'out_refund']:
                    if rec.journal_id.sequence_control_id:        
                        l10n_ve_document_number = rec.env[
                            'ir.sequence'].next_by_code(rec.journal_id.\
                                sequence_control_id.code)
                        rec.write({
                            'l10n_ve_document_number': l10n_ve_document_number})
                    else:
                        raise ValidationError(
                    _("El diario por el cual está emitiendo la factura no"+
                        " tiene secuencia para número de control"))


    def reportWithholdingCertificateInvoceIva(self):
        pass
        # report_obj = self.env['ir.actions.report']
        # report = report_obj._get_report_from_name('l10n_ve_withholding.report_withholding_certificate_invoce_iva')
        # data ={
        #     'move': self,
        #     'doc_model': self.env['whithholdings.iva'],
        #     'docs': self.env['whithholdings.iva'].search([('move_id','=',self.id)])
        # } 




        # print(report.report_action(self),self)
        # return report.with_context(
        #          docs= self.env['whithholdings.iva'].search([('move_id','=',self.id)])
        # ).report_action(None, data=data)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_price(self):
        # ver nota en get_taxes_values
        invoice = self.move_id
        invoice_date = invoice.invoice_date or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
        try:
            self.env.context.invoice_date = invoice_date
            self.env.context.invoice_company = self.company_id
        except Exception:
            pass
        return super()._compute_price()

class VisitReport(models.AbstractModel):

    _name='report.account.move'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('l10n_ve_withholding.report_withholding_certificate_invoce_iva')
        return {
            'doc_ids': docids,
            'doc_model': self.env['account.move'],
            'docs': self.env['account.move'].browse(docids)
        }