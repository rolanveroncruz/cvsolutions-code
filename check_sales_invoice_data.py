# This script checks the CSVI SALES INVOICE 2025.xlsx file by running through the rows
# and chcking if the customer name, and product name are in the database.  If they aren't, log them to files; otherwise
# move on to the next row.
import datetime
import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config
import openpyxl as xl
from customer_and_product_utils import (check_customer_exists_exact, check_product_exits_exact, save_customer_to_dict,
                                        save_product_to_dict, write_customer_dict_to_file, write_product_dict_to_file)

START_ROW=29

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


def check_sales_file(models, uid, config, xl_file):
	wb = xl.load_workbook(xl_file)
	sheet = wb.active
	for i,row in enumerate(sheet.iter_rows(min_row=START_ROW, values_only=True)):
		sales_invoice_id = row[6]
		if row[7] is not None:
			date = parse_for_date(str(row[7]))
		else:
			date = None
		customer_name = row[8]
		product_name = row[9]
		qty = row[10]
		unit_pice = row[12]
		if (sales_invoice_id is None or sales_invoice_id=="") and (customer_name is None or customer_name == ""):
			break
		print(f" Row:{i+START_ROW} Checking customer:{customer_name} and product:{product_name}")
		customer_exists = check_customer_exists_exact(customer_name, models, uid, config)
		if not customer_exists:
			save_customer_to_dict(customer_name, i+1)
		product_exists = check_product_exits_exact(product_name, models, uid, config)
		if not product_exists:
			save_product_to_dict(product_name, i+1)

	print(f"Saving data to files")
	write_customer_dict_to_file()
	write_product_dict_to_file()




def main():
	the_sales_invoice_file = "data/CVSI SALES INVOICE 2025.xlsx"
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	check_sales_file(models, uid, config, the_sales_invoice_file)

if __name__ == '__main__':
	main()