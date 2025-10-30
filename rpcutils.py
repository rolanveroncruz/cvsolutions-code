import xmlrpc.client
from Config import Config

def get_rpc_info(config:Config)-> int:
	info = xmlrpc.client.ServerProxy(f"{config.HOST}/xmlrpc/2/common")
	print(f"version:{info.version()}")
	try:
		uid = info.authenticate(config.DB, config.USER_EMAIL, config.API_KEY, {})
		print(f"uid:{uid}")
		return uid
	except Exception as e:
		print(f"authenticate error:{e}")
		exit(1)
