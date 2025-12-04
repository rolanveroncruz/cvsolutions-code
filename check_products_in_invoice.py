"""
This scripts checks the products in "CVSI SALES INVOICE 2025.xlsx". It checks if it is in the odoo database.
If it isn't it checks it against the product_coreections_dict.json file. If it is not in either, we intervene manually.
"""
import xmlrpc.client

from typing import List
from rpcutils import get_rpc_info
from Config import Config
import openpyxl as xl
import json
import datetime

def parse_for_date(date_str: str):
	""" Convert CVSI date format of 'yymmdd' to a datetime.date object"""
	year = "20"
	month = 0
	day = 0
	try:
		year = int("20" + (date_str[0:2]))
		month = int(date_str[2:4])
		day = int(date_str[4:6])
	except ValueError:
		print(f"Error parsing date: {date_str}")
	return datetime.date(year=year, month=month, day=day)


START_ROW=29
def check_sales_file(models, uid, config, xl_file):
	input_file = "output/product_corrections_dict.json"
	with open(input_file, "r") as f:
		product_corrections_dict = json.load(f)


	wb = xl.load_workbook(xl_file)
	sheet = wb.active
	not_in_db_count = 0
	for i,row in enumerate(sheet.iter_rows(min_row=START_ROW, values_only=True)):
		sales_invoice_id = row[6]
		if row[7] is not None:
			date = parse_for_date(str(row[7]))
		else:
			date = None
		product_name = row[9]
		if product_name is not None and product_name != "":
			product_name = product_name.strip()
		if (sales_invoice_id is None or sales_invoice_id=="") and (product_name is None or product_name == ""):
			continue
		in_db = check_product_name_in_db(models=models, uid=uid, config=config, row=i+START_ROW,product_name=product_name)
		if not in_db:
			not_in_db_count +=1
			check_product_name_in_dict(row=i+START_ROW, product_name=product_name, product_corrections_dict=product_corrections_dict)

def check_product_name_in_db(models, uid, config, row, product_name):
	domain_like = [('name', 'ilike', f"{product_name}")]
	found = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'search', [domain_like])
	if len(found) == 1:
		return True
	else:
		return False

def check_product_name_in_dict(row, product_name, product_corrections_dict):
	if product_name in product_corrections_dict.keys():
		return True
	else:
		print(f"In row {row} Product '{product_name}' not found in product_corrections_dict.json")
		return False

def main():
	the_sales_invoice_file = "data/CVSI SALES INVOICE 2025.xlsx"
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	check_sales_file(models=models, uid=uid, config=config, xl_file=the_sales_invoice_file)
	pass

if __name__ == "__main__":
	main()