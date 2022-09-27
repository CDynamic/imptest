# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_date = fields.Date( 
        compute='_compute_payment_date',
        readonly=True,
        required=False,
        string="Payments Date",
        
    )

    communication = fields.Char(
        compute='_compute_communication',
        readonly=True,
    )

    #created to record retention percentages
    comment_withholding = fields.Char('Comment withholding')

    def _get_fiscal_period(self, date):
        
        str_date = str(date).split('-')
        vals = 'AÑO '+str_date[0]+' MES '+str_date[1]
        print(date,vals)
        return vals

    
    # @api.depends('payment_ids.line_ids')
    def _compute_payment_date(self):
      cos= self.env['account.payment.group'].search( [('payment_ids', '=', self.id)])
      self.payment_date = cos.payment_date

    def _compute_communication(self):
      cos= self.env['account.payment.group'].search( [('payment_ids', '=', self.id)])
      self.communication = cos.communication




    @api.onchange('journal_id')
    def _onchange_compute_amount_currency(self):
        for rec in self:
            # pass
            if rec.other_currency and rec.payment_group_id:
                if rec.payment_group_id.payments_amount <= 0:
                    rec.amount = rec.payment_group_id.selected_finacial_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    rec.amount = 0
                    payments_amount = rec.payment_group_id.selected_finacial_debt - \
                        rec.payment_group_id.payments_amount
                    rec.amount = rec.company_id.currency_id._convert(
                        payments_amount, rec.currency_id, rec.company_id, rec.date)
            if not rec.other_currency and rec.payment_group_id:
                rec.amount = rec.payment_group_id.selected_finacial_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    payments_amount = rec.payment_group_id.payments_amount - rec.amount
                    rec.amount = rec.payment_group_id.selected_finacial_debt - \
                        payments_amount

    @api.onchange('date')
    def _onchange_compute_amount_currency_date(self):
        for rec in self:
            if rec.other_currency and rec.payment_group_id:
                rec.amount_company_currency = rec.currency_id._convert(
                    rec.amount, rec.company_id.currency_id,
                    rec.company_id, rec.date)
