"""
This script will download the sales information from Odoo.
The parent model is the sale.order. It has the following fields:
- name (Order Reference, e.g. SO5648)
- date_order
- partner_id
- amount_total
- state
The child model is the sale.order.line. It has the following fields:
- order_id (link_bank to parent model)
- product_id
- product_uom_qty
- price_unit
- price_subtotal

"""
import xmlrpc.client

import pandas as pd

from rpcutils import get_rpc_info
from Config import Config
from datetime import date
import openpyxl as xl

def fetch_lines(models, uid, config, start_date_str, end_date_str):
	domain = [
		['order_id.date_order', '>=', start_date_str],
		['order_id.date_order' , '<=', end_date_str],
		['order_id.state', 'in', ['sale', 'done']],
	]
	sol_fields = [
		"order_id",
		"order_partner_id",
		"product_id",
		"name",
		"product_uom_qty",
		"qty_delivered",
		"qty_invoiced",
		"price_unit",
		"price_subtotal",
		"price_total",
		"currency_id",
		"company_id",
		"create_date",
	]

	lines = models.execute_kw(config.DB, uid, config.API_KEY,
	                          'sale.order.line',
	                          'search_read',
	                          [domain],
	                          { "fields":sol_fields,
	                            "limit": 0,
	                            })
	print(f"Fetched {len(lines)} lines")
	return lines


def get_product_uom_info(models, uid, config, sol_lines):
	product_ids = list({line["product_id"][0] for line in sol_lines if line.get("product_id")})
	product_uom_info = {}
	if product_ids:
		product_records = models.execute_kw(
			config.DB, uid, config.API_KEY,
			'product.product', 'search_read',
			[[["id", "in", product_ids]]],
			{"fields": ["uom_id"],
			 "limit": 0}
		)
		product_uom_info = {
			rec["id"]: rec.get("uom_id")[1] for rec in product_records
		}
	return product_uom_info


def get_order_info(models, uid, config, order_ids):
	order_fields = ["name", "date_order", "state"]
	if order_ids:
		order_records = models.execute_kw(config.DB, uid, config.API_KEY,
	                               'sale.order', 'search_read',
	                               [[["id", "in", order_ids]]],
	                                 {"fields": order_fields,
	                                  "limit":0,
	                                  },)
		order_info = { rec["id"]:rec for rec in order_records}
		return order_info


def save_lines_to_rows(sol_lines, order_info, product_uom_info):
	rows = []
	for line in sol_lines:
		order_m2o = line.get("order_id") or False
		partner_m2o = line.get("order_partner_id") or False
		product_m2o = line.get("product_id") or False

		order_id = order_m2o[0] if order_m2o else None
		order = order_info.get(order_id, {}) if order_id else{}

		product_id = product_m2o[0] if product_m2o else None
		uom_m2o = product_uom_info.get(product_id, None)
		uom_name = uom_m2o if uom_m2o else None

		ordered_qty = line.get("product_uom_qty") or 0
		unit_price = line.get("price_unit") or 0.0
		subtotal = line.get("price_subtotal") or 0.0
		total_with_tax = line.get("price_total") or 0.0

		rows.append({
			"Order ID": order_id,
			"S Inv#": order_m2o[1] if order_m2o else None,
			"Order Date": order.get("date_order"),
			"Order State": order.get("state"),

			"Customer" : partner_m2o[1] if partner_m2o else None,
			"Product": product_m2o[1] if product_m2o else None,
			 "Units":uom_name,
			"Line Description": line.get("name"),

			"Qty Ordered": line.get("product_uom_qty"),
			"Qty Delivered": line.get("qty_delivered"),
			"Qty Invoiced": line.get("qty_invoiced"),

			"Unit Price(VAT-IN)": round(line.get("price_unit") or 0.0,2),
			"Unit Price(VAT-EX)":round(line.get("price_unit")/1.12 or 0.0,2),
			"SI Billed Amt (VAT-IN)": line.get("price_subtotal"),
			"TOTAL AMT(VAT-EX)": "",
			"VAT AMT": "",
			"Total (with tax)": line.get("price_total"),
		})
	return rows

def save_rows_to_excel(rows):
	print(f"Saving {len(rows)} rows to excel")
	df = pd.DataFrame(rows)
	# TODO: Covert Order Date to date
	df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce").dt.date
	df["TOTAL AMT(VAT-EX)"] = df["Unit Price(VAT-EX)"] * df["Qty Ordered"]
	df["VAT AMT"] = df["TOTAL AMT(VAT-EX)"] - df["SI Billed Amt (VAT-IN)"]

	# Sort by Order Name (Sales invoice number) from earliest to latest
	df.sort_values(by=["S Inv#"], inplace=True, ignore_index=True)

	columns_order = [ "S Inv#", "Order Date", "Order State",
	                  "Customer", "Product",  "Qty Ordered", "Units",
	                  "Unit Price(VAT-IN)", "Unit Price(VAT-EX)", "TOTAL AMT(VAT-EX)", "VAT AMT"]
	df = df[[c for c in columns_order if c in df.columns]]
	df.to_excel("output/sales_report.xlsx", index=False)
	print("Saved to output/sales_report.xlsx")


def main():
	today = date.today()
	start_of_year = date(today.year, 1, 1)
	start_date_str = f"{start_of_year.isoformat()} 00:00:00"
	end_date_str = f"{today.isoformat()} 23:59:59"
	config = Config()
	uid = get_rpc_info(config)
	models = xmlrpc.client.ServerProxy(f'{config.HOST}/xmlrpc/2/object')
	sol_lines = fetch_lines(models, uid, config, start_date_str, end_date_str)
	product_uom_info = get_product_uom_info(models, uid, config, sol_lines)
	order_ids = list({line["order_id"][0] for line in sol_lines if line.get("order_id")})
	order_info = get_order_info(models, uid, config, order_ids)
	rows = save_lines_to_rows(sol_lines, order_info, product_uom_info)
	save_rows_to_excel(rows)

if __name__ == "__main__":
	main()
