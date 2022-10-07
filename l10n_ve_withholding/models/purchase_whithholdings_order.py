# from email.policy import default
# from odoo import models, fields, api, _
# from odoo.exceptions import UserError, ValidationError
# from datetime import datetime
# import logging
# import json

# _logger = logging.getLogger(__name__)

# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"

#     withholding_iva = fields.Many2one(
#         string='Selected Debt taxed',
#         compute='_compute_withholding_iva',)

#     def _compute_withholding_iva(self):
#         pass


