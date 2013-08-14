# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class product_product(osv.osv):
    """ Product Product """
    _name = "product.product"
    _inherit = "product.product"

    def _update_cost(self,cr,uid,ids=None,context=None):

	product_obj = self.pool.get('product.product')
	invoice_obj = self.pool.get('account.invoice')
	invoice_line_obj = self.pool.get('account.invoice.line')

	product_ids = product_obj.search(cr,uid,[('cost_method','=','last_purchase')])

	max_date = 0	
	for product in product_obj.browse(cr,uid,product_ids):
		invoice_line_ids = invoice_line_obj.search(cr,uid,[('product_id','=',product.id)])
		for invoice_line in invoice_line_obj.browse(cr,uid,invoice_line_ids):
			if invoice_line.invoice_id.state in ('paid','open') \
				and invoice_line.invoice_id.date_invoice > max_date \
				and invoice_line.invoice_id.type == 'in_invoice':
	
				price_unit_other_currency = invoice_line.price_unit * invoice_line.invoice_id.currency_id.rate
				vals_product = {
					'standard_price': price_unit_other_currency
					}
				return_id = product_obj.write(cr,uid,product.id,vals_product)
				max_date = invoice_line.invoice_id.date_invoice
				_logger.debug("Updated product " + product.name)
			
	return None

    _columns = {
	        'cost_method': fields.selection([('standard','Standard Price'), 
						('average','Average Price'),
						('last_purchase','Last Purchase')],
						 'Costing Method', required=True,
						help="Standard Price: The cost price is manually updated at the end of a specific period (usually every year). \nAverage Price: The cost price is recomputed at each incoming shipment."),
		}

product_product()

