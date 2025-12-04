# This script checks if the customers in CVSI SALES INVOICE 2025.xlsx are in the RTS database.
# If they aren't we adjust the CVSI SALES INVOICE 2025.xlsx file to include them.

import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config
import openpyxl as xl
import datetime
import json

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
	input_file = "output/company_tin_dict.json"
	with open(input_file, "r") as f:
		company_tin_dict= json.load(f)

	wb = xl.load_workbook(xl_file)
	sheet = wb.active
	not_in_db_count = 0
	for i,row in enumerate(sheet.iter_rows(min_row=START_ROW, values_only=True)):
		sales_invoice_id = row[6]
		if row[7] is not None:
			date = parse_for_date(str(row[7]))
		else:
			date = None
		customer_name = row[8]
		if (sales_invoice_id is None or sales_invoice_id=="") and (customer_name is None or customer_name == ""):
			continue
		in_db = check_customer_name_in_db(models=models, uid=uid, config=config, row=i+START_ROW,customer_name=customer_name )
		if not in_db:
			not_in_db_count +=1
			check_customer_name_in_dict(i+START_ROW, customer_name, company_tin_dict)


def check_customer_name_in_db(models, uid, config, row, customer_name):
	"""
	Check if the customer name is in the Odoo database.
	:return: Bool
	"""
	domain_exact = [('name', '=', f"{customer_name}")]
	found = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'search', [domain_exact])
	if len(found) == 1:
		# print(f"In row:{row} Customer '{customer_name}' found in Odoo database")
		return True
	else:
		print(f"****** In row:{row} Customer '{customer_name}' NOT found in Odoo database")
		return False


def check_customer_name_in_dict(row, customer_name, company_tin_dict):
	"""
	Check if the customer name is in the company_tin_dict.
	:param row:
	:param customer_name:
	:param company_tin_dict:
	:return:
	"""
	if customer_name in company_tin_dict:
		return True
	else:
		print(f"******* In row:{row} Customer '{customer_name}' is not in the RTS database")
		return False

def main():
	the_sales_invoice_file = "data/CVSI SALES INVOICE 2025.xlsx"
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	check_sales_file(models=models, uid=uid, config=config, xl_file=the_sales_invoice_file)

if __name__ == "__main__":
	main()