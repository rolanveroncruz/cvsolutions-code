"""
In this script, we go through the tin_company_dict.json and check that the TIN is in the database, then check if the companies
match. Log them if they don't.
"""
import json
import xmlrpc.client
from rpcutils import get_rpc_info
from Config import Config

def check_in_database(models, uid, config, tin, company_name):
	""" Check if the TIN is in the database"""
	domain = [('vat', '=', f"{tin}")]
	options = {
		'fields': ['name']
	}
	ids = models.execute_kw(config.DB, uid, config.API_KEY, 'res.partner', 'search_read', [domain], options)
	if len(ids) == 1:
		if ids[0]['name'] == company_name:
			return
		else:
			print(f"{tin} is in the database but \'{ids[0]['name']}\'(Database) != '{company_name}' (file)")
	else:
		print(f"{tin} from {company_name} is not in the database")

def main():
	input_file = "output/tin_company_dict.json"
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	with open(input_file, "r") as f:
		tin_company_dict = json.load(f)

	for tin, company_name in tin_company_dict.items():
		check_in_database(models=models, uid=uid, config=config, tin=tin, company_name=company_name)




if __name__ == "__main__":
	main()



