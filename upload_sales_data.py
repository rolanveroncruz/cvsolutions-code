
import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config
import datetime
import openpyxl as xl
from upload_sales_data_utils import get_customer_id, get_product_id, upload_sales_invoice
from color_codes import Colors
from sales_invoice import SalesInvoice
import os
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

def create_new_sales_invoice( name, partner_id,  date_order):
	print(f"Creating new sales invoice {name}, {partner_id}, {date_order}")
	return SalesInvoice(name=name, partner_id=partner_id, date_order=date_order)


def process_data_file(models, uid, config, input_file):
	START_ROW = 30
	wb = xl.load_workbook(input_file, data_only=True)
	sheet = wb.active
	not_in_db_count = 0
	blank_lines_count = 0
	sales_invoice = None
	for i,row in enumerate(sheet.iter_rows(min_row=START_ROW, values_only=True)):

		""" 1. Check if the row is a valid/workable line. If it is not, skip it and start counting blank lines.
		If there has been 10 successive blank lines, break; else reset the blank lines counter. 
		"""
		if (row[6] is None or row[6]=="") and (row[8] is None or row[8] == ""):
			blank_lines_count +=1
			if blank_lines_count > 10:
				break
		blank_lines_count = 0

		""" 2. Start assigning row values to variables.
		
		"""
		sales_invoice_id = str(row[6])
		if row[7] is not None:
			date = parse_for_date(str(row[7]))
		else:
			date = None
		customer_name = row[8]
		product_name = row[9]

		product_qty_str = str(row[10]) if row[10] is not None else '1'
		if product_qty_str == "FREE":
			product_qty_str = '0'
		product_qty = int(product_qty_str) if product_qty_str.isnumeric() else 1
		units = row[11] if row[11] is not None else "units"

		unit_price_vat_ex = float(row[13]) if row[13] is not None else 1
		unit_price = float(row[12]) if row[12] is not None else unit_price_vat_ex

		"""" 3. Check for customer and product in DB.
		
		"""
		found_customer, customer_id = get_customer_id(models, uid, config, customer_name)
		found_product, product_id = get_product_id(models, uid, config, product_name)

		""" 4. If customer and product are found in DB, check if the sales invoice is new or the same as the previous one.
		If not the same, upload the old sales invoice then create a new one. Add the order line.
		"""
		if found_customer and found_product:
			print( Colors.GREEN + f"***** Row {i+START_ROW} -Invoice:{sales_invoice_id} Customer:{customer_name} and Product:{product_name} found in DB *****" + Colors.RESET)

			if sales_invoice is None:
				sales_invoice = create_new_sales_invoice(name=sales_invoice_id, partner_id=customer_id, date_order=date)
				continue
			elif sales_invoice.name != sales_invoice_id:
				print(f"New invoice found: {sales_invoice_id} different from old {sales_invoice.name}")
				si_id = upload_sales_invoice(models, uid, config, sales_invoice)
				print(f"Uploaded sales invoice {si_id}")
				print(f"Creating new sales invoice {sales_invoice_id}")
				sales_invoice = create_new_sales_invoice(name=sales_invoice_id, partner_id=customer_id, date_order=date)

			sales_invoice.add_order_line(product_id=product_id, qty=product_qty, price_unit=unit_price)

		else:
			print(Colors.RED + f"!!!!! Row {i+START_ROW} - Customer:{customer_name} and Product:{product_name} NOT found in DB !!!!!" + Colors.RESET)




def main():

	# prepare problem_upload-1.json
	if not os.path.isfile("output/problem_upload.json"):
		problem_upload = {'problem_si': []}
		with open("output/problem_upload.json", "w") as f:
			json.dump(problem_upload, f)

	input_file = "data/CVSI SALES INVOICE 2025.xlsx"
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	process_data_file(models=models, uid=uid, config=config, input_file=input_file)


if __name__ == "__main__":
	main()