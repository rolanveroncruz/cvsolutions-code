"""
In this script we check the product corrections file. We open the file, going through each row, and checking if the
product name is in the database. Add it if it isn't, add it manually. Then, we save the data of the products into a json file
with "product_name_for_correction":"product_name_in_database".
"""
import json
import xmlrpc.client

import openpyxl
from typing import List
from rpcutils import get_rpc_info
from Config import Config
import openpyxl as xl

corrections_dict = {}

def check_corrected_name(models, uid, config, corrected_name:str)->bool:
	""" Check if the corrected name is in the database"""
	domain_exact= [('name', '=', f"{corrected_name}")]
	found = models.execute_kw(config.DB, uid, config.API_KEY, 'product.template', 'search', [domain_exact])
	if len(found) == 1:
		return True
	else:
		return False



def process_row(models, uid, config, row_num:int, row:List[any]):
	old_name = row[1].replace(":", "")
	old_name = old_name.strip()
	correct_name = row[2]
	found = check_corrected_name(models, uid, config, correct_name)
	if not found:
		print(f"WARNING: Product '{correct_name}' not found in database in row {row_num}")
	else:
		corrections_dict[old_name] = correct_name




def main():
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	input_file = "data/PRODUCTS CORRECTIONS.xlsx"
	START_ROW = 3
	wb = xl.load_workbook(input_file)
	sheet = wb.active
	for i, row in enumerate(sheet.iter_rows(min_row=START_ROW, values_only=True)):
		process_row(models, uid, config, START_ROW+i, row)

	with open("output/product_corrections_dict.json", "w") as f:
		json.dump(corrections_dict, f)



if __name__ == "__main__":
	main()