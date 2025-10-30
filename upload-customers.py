import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config
import openpyxl as xl
import glob
from typing import List


def read_from_row(row, sheet):
	address_data = row[1].value.split(",")
	customer_data = {
		'name': row[0].value,
		'is_company': 'True',
		'street': address_data[0],
		'street2': address_data[1] if len(address_data) > 1 else "",
		'city': address_data[2] if len(address_data) > 2 else sheet.title,
		'vat': row[2].value,

	}

	return customer_data

def search_partner_by_name(models, uid:int, config:Config, partner_data:dict)->tuple[bool, None|List]:
	# 1. Define the search domain
	# We search for a product where the 'default_code' (Internal Reference)
	# is equal to the unique reference.
	name = partner_data['name']
	domain = [('name', '=', name)]
	# 2. Execute the search operation
	# The 'search' method returns a list of matching product IDs.
	partner_ids = models.execute_kw(
		config.DB, uid, config.API_KEY,
		'res.partner',
		'search',
		[domain]
	)
	# 3. Check the result
	if partner_ids:
		# Product is found. product_ids will contain the list of IDs (e.g., [123]).
		print(
			f"✅ Partner with Name'{name}' is already in the database. ID(s): {partner_ids}")
		return True, partner_ids
	else:
		# Product is not found. product_ids will be an empty list ([]).
		print(f"❌ Partner with Name'{name}' is NOT found. Ready to create.")
		return False, None

def upload_partner(models, uid, config, row_no, partner_data):
	print(f"uploading {partner_data['name']}")
	new_contact_id = models.execute_kw(
		config.DB,
		uid,
		config.API_KEY,
		'res.partner',
		'create',
		[partner_data])
	print(f"{partner_data['name']} with new_contact_id:{new_contact_id}")


def update_partner(models, uid, config, row_no, found_ids, partner_data):
	print(f"updating {partner_data['name']}")
	models.execute_kw(
		config.DB,
		uid,
		config.API_KEY,
		'res.partner',
		'write',
		[found_ids[0], partner_data])

def upload_customers_from_xl_file(models, uid, config, data_file, sheet):
	print(f"uploading {data_file}")
	wb = xl.load_workbook(data_file)
	sheet = wb[sheet]

	for idx,row in enumerate(sheet.iter_rows()):
		if idx < 1:
			continue
		if row[0].value is None or row[0].value == "":
			continue
		partner_data = read_from_row(row, sheet)
		found, found_ids = search_partner_by_name(models, uid, config, partner_data)

		if not found:
			# Import the partner_data
			upload_partner(models=models, uid=uid, config=config,row_no=idx, partner_data=partner_data)
		else:
			# Edit the partner_data
			update_partner(models=models, uid=uid, config=config,row_no=idx, found_ids=found_ids, partner_data=partner_data)



def main():
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	data_file = "data/Customer Database.xlsx"
	upload_customers_from_xl_file(models=models, uid=uid, config=config,  data_file=data_file, sheet="Davao")
	upload_customers_from_xl_file(models=models, uid=uid, config=config,  data_file=data_file, sheet="Manila")


if __name__ == "__main__":
	main()
