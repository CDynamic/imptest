from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class account_move_whithholdings(models.Model):
    _name='whithholdings.iva'

    report_date = fields.Date(readonly=True, required=False, string="Payments Date",)
    invoice = fields.Char()
    Núm_Control = fields.Char()
    Núm_ND = fields.Char()
    Núm_NC = fields.Char()
    Total_Compra_con_IVA = fields.Float()
    Compras_sin_crédito = fields.Float()
    Base_Imponible = fields.Float()
    Alicuota = fields.Char()
    Monto_IVA = fields.Float()
    IVA_Retenido = fields.Float()

    
        
    