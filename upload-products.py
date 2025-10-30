import xmlrpc.client
from Config import Config
import openpyxl as xl
from rpcutils import get_rpc_info


def read_from_row(row):
	product_data = {}

	product_data['name'] = row[0].value
	# col=12, part_number

	return product_data

def search_product_by_name(models, uid:int, config:Config, product_data:dict):
	# 1. Define the search domain
	# We search for a product where the 'default_code' (Internal Reference)
	# is equal to the unique reference.
	name = product_data['name']
	domain = [('name', '=', name)]
	# 2. Execute the search operation
	# The 'search' method returns a list of matching product IDs.
	product_ids = models.execute_kw(
		config.DB, uid, config.API_KEY,
		'product.product',
		'search',
		[domain]
	)
	# 3. Check the result
	if product_ids:
		# Product is found. product_ids will contain the list of IDs (e.g., [123]).
		print(
			f"✅ Product with Name'{name}' is already in the database. ID(s): {product_ids}")
		return True
	else:
		# Product is not found. product_ids will be an empty list ([]).
		print(f"❌ Product with Name'{name}' is NOT found. Ready to create.")
		return False

def import_product(models, uid:int, config:Config, row_no:int, product_data:dict):
	"""
	Import product_data.

	:param currency_id:
	:param models:
	:param uid:
	:param config:
	:param product_data: A dict containing product data:'name', 'default_code', 'categ_id'.
	:return: product_id
	"""

	print(f"uploading {product_data['name']}")
	data = {'name': product_data['name'],
	        "type": "consu",
	        }
	if row_no > 29:
		data['categ_id'] = 5
	else:
		data['categ_id'] = 4
	id = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'create', [data])
	return id


def upload_products_from_xl_file(models, uid:int, config:Config, xl_file ):
	"""
	Iterate through rows of the Excel file, then import the product.
	:param currency_id:
	:param models:
	:param uid:
	:param config:
	:param xl_file:
	:param parent_category: The parent category of the products to be imported. This is used to determine the category_id.
	:return:
	"""
	wb = xl.load_workbook(xl_file)
	sheet = wb.active

	for idx,row in enumerate(sheet.iter_rows()):
		if idx < 1:
			continue
		if row[0].value is None or row[0].value == "":
			continue
		product_data = read_from_row(row)
		found = search_product_by_name(models, uid, config, product_data)

		if not found:
			# Import the product
			import_product(models=models, uid=uid, config=config,row_no=idx, product_data=product_data)


def main():
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	data_file = "data/CERTS - RAWMAT & PRODUCTS.xlsx"
	upload_products_from_xl_file(models, uid, config,  data_file)


if __name__ == "__main__":
	main()

