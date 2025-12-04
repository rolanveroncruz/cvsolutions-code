import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config
import json
from color_codes import Colors

def get_partner_name(models, uid, config, partner_id):
	fields = { 'fields': ['name']}
	product_data = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'read', [partner_id], fields)
	return product_data[0]['name']
	pass

def get_product_name(models, uid, config, product_id):
	fields = { 'fields': ['name']}
	product_data = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'read', [product_id], fields)
	return product_data[0]['name']


def expand_si(models, uid, config, problem_si):
	""" Expand the problem sales invoice"""
	partner_id = problem_si['partner_id']
	partner_name = get_partner_name(models, uid, config, partner_id)
	print(Colors.YELLOW + f" (partner_id:{partner_id}): :{partner_name}" + Colors.RESET)

	for order_line in problem_si['order_line']:
		product_id = order_line[2]['product_id']
		qty = order_line[2]['product_uom_qty']
		price_unit = order_line[2]['price_unit']
		product_name = get_product_name(models, uid, config, product_id)
		print(Colors.YELLOW +f"\t\t\t (product_id:{product_id}):{product_name} qty:{qty} price_unit:{price_unit}"+ Colors.RESET)

def reupload_problem_si(models, uid, config, problem_si):
	""" Reupload the problem sales invoice"""
	problem_si_vals = {
		'name': 'Reupload:' + problem_si['name'],
		'client_order_ref': 'Reupload:' + problem_si['client_order_ref'],
		'date_order': problem_si['date_order'],
		'partner_id': problem_si['partner_id'],
		'order_line': problem_si['order_line'],
		'state': 'sale'
	}

	try:
		print(Colors.CYAN + f"Attempting reuploading {problem_si_vals['date_order']}: {problem_si_vals['name']}" + Colors.RESET)
		new_problem_si_id = models.execute_kw(config.DB, uid, config.API_KEY, 'sale.order', 'create', [problem_si_vals])
		print(Colors.GREEN+ f"Sucess" + Colors.RESET)
	except Exception as e:
		print(Colors.RED+ f"FAIL:" + str(e) + Colors.RESET)
		expand_si(models, uid, config, problem_si,)


def main():
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')

	problem_products = {}
	with open("output/problem_upload.json", "r") as f:
		problem_upload = json.load(f)
		problem_si_s = problem_upload['problem_si']
		print(f"There are {len(problem_si_s)} problematic sales invoices.")
		for problem_si in problem_si_s:
			for problem_line in problem_si['order_line']:
				product_id = problem_line[2]['product_id']
				if product_id not in problem_products:
					problem_products[product_id] = 0
				problem_products[product_id] += 1
			reupload_problem_si(models=models, uid=uid, config=config, problem_si=problem_si)
		print(f"{problem_products}")




if __name__ == "__main__":
	main()
