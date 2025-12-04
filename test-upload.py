import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config



def test_product_upload(models, uid, config, product_id, name=''):
	test_data ={
		'name': f'5442-{name}',
		'client_order_ref': 'Ref:5442',
		'partner_id': 58,
		'date_order': '2025-01-03',
		'order_line': [(0, 0, {'product_id': product_id, 'product_uom_qty': 1, 'price_unit': 323680.0}),
		               (0, 0, {'product_id': 90, 'product_uom_qty': 240, 'price_unit': 234.02}),
		               (0, 0, {'product_id': 91, 'product_uom_qty': 240, 'price_unit': 222.26}),
		               (0, 0, {'product_id': 86, 'product_uom_qty': 500, 'price_unit': 240.0})],
		'state': 'sale'
	}
	new_order_id = 0
	try:
		new_order_id = models.execute_kw(config.DB, uid, config.API_KEY, 'sale.order', 'create', [test_data])
		print(f"{new_order_id}: no problem with: {product_id}")
	except Exception as e:
		print(f"problem with product id:{product_id}")



def test_product_name(models, uid, config, name:str):
	domain = [('name', '=', name)]
	ids= models.execute_kw( config.DB, uid, config.API_KEY, 'product.template', 'search', [domain] )
	print(f"ids are:{ids}")
	return ids

def read_from_product_id(models, uid, config, product_id):
	fields = { 'fields': ['name']}
	product_data = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'read', [product_id], fields)
	print(product_data)


def main():
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	# test_product_name(models=models, uid=uid, config=config, name="PROGRAM CHEMICAL TREATMENT COGEN 2")
	# read_from_product_id(models=models, uid=uid, config=config, product_id=117)
	problem_product_ids = [126, 90, 91, 86, 124]
	for product_id in problem_product_ids:
		test_product_upload(models=models, uid=uid, config=config, product_id=product_id,name='Temp' )



if __name__ == "__main__":
	main()