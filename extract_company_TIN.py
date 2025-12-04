"""
This file reads CVSI Sales Invoice Monthly 2025 RTS.xlsx and extract companies and their TINs.
This creates two dicts: one that maps companies to TINs and another that maps TINs to companies.
It then saves these dicts to files.
"""
import openpyxl
import json

company_dict = {}
tin_dict = {}

def is_row_ignorable(row):
	if row[0] is None or row[0] == "" or row[0]=="Date":
		return True
	return False

def is_row_empty(row):
	if ((row[0] is None or row[0] == "") and
			(row[1] is None or row[1] == "") and
			(row[2] is None or row[2] == "") and
			(row[3] is None or row[3] == "") and
			(row[4] is None or row[4] == "")):
		return True
	return False


def process_row(row,i:int):
	print(f"Processing row {i}")
	company = row[1]
	tin = row[4]
	if company not in company_dict:
		company_dict[company] = tin
	else:
		if company_dict[company] != tin:
			print(f"WARNING: Company '{company}' has multiple TINs: '{company_dict[company]}' and '{tin}' are"
			      f" not equal:{company_dict[company] != tin} in row {i+1}")

	if tin not in tin_dict:
		tin_dict[tin] = company
	else:
		if tin_dict[tin] != company:
			print(f"WARNING: TIN '{tin}' has multiple companies: '{tin_dict[tin]}' and '{company}' in row {i+1}")


def main():
	the_file = "data/CVSI Sales Invoice Monthly 2025 RTS.xlsx"
	START_ROW = 5
	wb = openpyxl.load_workbook(the_file)
	sheet = wb.active
	for i,row in enumerate(sheet.iter_rows(min_row=START_ROW, values_only=True,max_row=90 )):
		if is_row_ignorable(row):
			continue
		process_row(row,i+START_ROW)
	with open("output/company_tin_dict.json", "w") as f:
		json.dump(company_dict, f)
	with open("output/tin_company_dict.json", "w") as f:
		json.dump(tin_dict, f)



if __name__ == "__main__":
	main()
