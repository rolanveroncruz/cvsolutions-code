from typing import List


unidentified_customers = {}
unidentified_products = {}

def check_product_exits_exact(product_name: str, models, uid, config)->bool:
	"""
	Check if a product exists in Odoo.
	"""
	domain_exact = [('default_code', '=', product_name)]
	found_exact_ids = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'search', [domain_exact])
	if len(found_exact_ids) == 1:
		return True
	else:
		return False

def check_product_alts(product_name: str, models, uid, config) -> list[str]:
		alts = []
		domain_ilike = [('name', 'ilike', f"%{product_name}")]
		options = {
			'fields': ['name']
		}
		found_ilike_ids = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'search_read', [domain_ilike])
		if found_ilike_ids:
			for item in found_ilike_ids:
				alts.append(item['name'])
		return alts




def check_customer_exists_exact(customer_name: str, models, uid, config)->bool:
	"""
	Check if a customer exists in Odoo.
	"""
	domain_exact = [('name', 'ilike', f"%{customer_name}")]
	found = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'search', [domain_exact])
	if len(found) == 1:
		return True
	else:
		return False


def check_customer_alts(customer_name: str, models, uid, config)->list[str]:
	alts = []
	domain_ilike = [('name', 'ilike', f"%{customer_name}")]
	options = {
		'fields': ['name']
	}
	found_alt_ids = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'search_read', [domain_ilike], options)
	if found_alt_ids:
		for item in found_alt_ids:
			alts.append(item['name'])
	return alts


def save_customer_to_dict(customer_name:str, row:int):
	if customer_name not in unidentified_customers:
		unidentified_customers[customer_name] = []
	unidentified_customers[customer_name].append(row)

def write_customer_dict_to_file():
	with open("output/unidentified_customers.txt", "w") as f:
		for customer, rows in unidentified_customers.items():
			f.write(f"{customer} : {rows}\n")


def save_product_to_dict(product_name:str, row:int):
	if product_name not in unidentified_products:
		unidentified_products[product_name] = []
	unidentified_products[product_name].append(row)

def write_product_dict_to_file():
	with open("output/unidentified_products.txt", "w") as f:
		for customer, rows in unidentified_products.items():
			f.write(f"{customer} : {rows}\n")
