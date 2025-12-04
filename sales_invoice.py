from tkinter.font import names


class SalesInvoice:
	def __init__(self, name, partner_id, date_order):
		self.name = name
		self.partner_id = partner_id
		self.client_order_ref = name
		self.date_order = date_order
		self.state = 'done'
		self.order_line = []

	def add_order_line(self, product_id, qty, price_unit):
		print(f"Adding to {self.name} order line {product_id} {qty} {price_unit}")
		line = (0,0,{
			'product_id': product_id,
			'product_uom_qty': qty,
			'price_unit': price_unit
		})
		self.order_line.append(line)
