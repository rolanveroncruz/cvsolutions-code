import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config
from typing import Tuple
import json
from sales_invoice import SalesInvoice
import time

def get_customer_id_via_tin(models, uid, config, customer_name:str)->Tuple[bool, int]:
	"""
	Search for the customer's name in company_tin_dict. Then search for the customer's TIN in the Odoo database.
	"""
	with open("output/company_tin_dict.json", "r") as f:
		company_tin_dict = json.loads(f.read())
		if customer_name in company_tin_dict:
			tin = company_tin_dict[customer_name]
			domain_exact= [('vat', '=', f"{tin}")]
			ids = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'search', [domain_exact])
			if len(ids) == 1:
				return True, ids[0]
			else:
				return False, 0
		else:
			return False, 0


def get_customer_id(models, uid, config, customer_name:str)->Tuple[bool, int]:
	"""
	Search for the custommer's name in the Odoo database.
	if found, return the customer id.
	else, try to get the customer id via the company's tax identification number.

	"""

	customer_id = None
	domain_exact= [('name', '=', f"{customer_name}")]
	ids = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'search', [domain_exact])
	if len(ids) != 1:
		try:
			found,customer_id = get_customer_id_via_tin(models, uid, config, customer_name)
			return found, customer_id
		except Exception as e:
			print(f"Error getting customer id for {customer_name}")
			print(e)
	else:
		customer_id = ids[0]
	return True, int(customer_id)


def get_product_id(models, uid, config, product_name:str)->Tuple[bool, int]:
	domain_exact= [('name', '=', f"{product_name}")]
	ids = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'search', [domain_exact])
	if len(ids) == 1:
		return True,ids[0]
	else:
		return  get_product_id_from_corrections(models, uid, config, product_name)



def get_product_id_from_corrections(models, uid, config, product_name)->Tuple[bool,int]:
	with open("output/product_corrections_dict.json", "r") as f:
		product_corrections_dict = json.loads(f.read())
	if product_name in product_corrections_dict:
		corrected_product_name = product_corrections_dict[product_name]
		domain_exact= [('name', '=', f"{corrected_product_name}")]
		ids = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'search', [domain_exact])
		if len(ids) == 1:
			return True,ids[0]
		else:
			return False,0
	return False, 0


def upload_sales_invoice(models:xmlrpc.client.ServerProxy, uid:int, config:Config, sales_invoice:SalesInvoice) -> int:
	so_vals = {
		'name':  sales_invoice.name,
		'client_order_ref': 'Ref:' + sales_invoice.name,
		'partner_id': sales_invoice.partner_id,
		'date_order': sales_invoice.date_order.strftime('%Y-%m-%d'),
		'state': 'sale',
		'order_line': sales_invoice.order_line,
	}
	print("Uploading sales invoice: {", so_vals, "")
	time.sleep(2)
	new_order_id = 0
	try:

		new_order_id = models.execute_kw(config.DB, uid, config.API_KEY, 'sale.order', 'create', [so_vals])
	except Exception as e:
		with open("output/problem_upload.json", "r") as f:
			problem_upload = json.load(f)

		with open("output/problem_upload.json", "w") as f:
			problem_upload['problem_si'].append(so_vals)
			json.dump(problem_upload,f)

	return new_order_id