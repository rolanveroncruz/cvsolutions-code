# Code for CV Solutions Project


## Uploading Sales Data
#### Nov 4, 2025 - Check and Correct Customers
I tried uploading the sales data from "CVSI Sales Invoice 2025.xlsx" as it is the one that contains the items sold (`)
The problem was some customers and many products did not match with the uploaded database. The recommended approach was to match the customers to 
the customers in CVSI Sales Invoice Monthly 2025 RTS.xlsx. Then use their TINs to match the customers in the database.

1. So the first step is to extract the companies and their TINs from "CVSI Sales Invoice Monthly 2025 RTS.xlsx". 
This has already been done. The resulting files are "company_tin_dict.json" and "tin_company_dict.json" (DONE in `extract_company_TIN.py`).

2. Check if the TINs match with a TIN in the database, and if the pulled customer is the same.(Done in `check_TINs_vs_database.py`) 

3. Check that the companies in "CVSI Sales Invoice 2025.xlsx" match with the companies in the database. If one doesn't, revise its name
to match. (Done in `check_sales_invoice_vs_rts.py`).

4. Customers done. Will do products next.


#### Nov 6, 2025—Check and Correct Products
1. We have a product corrections file "Product_Corrections.xlsx". We will use this to correct the products in "CVSI Sales Invoice 2025.xlsx". 
First, we'll check if the corrections in "Product_Corrections.xlsx" match with the products in the database. 
If a correction is not in the database, we'll add it. We're done  with this step, if all the corrections are in the database.
Mostly done in `check_product_corrections_file.py`. Just waiting for confirmation for one item. Will proceed to the next step.
Done. All entries in `product_corrections_dict.json` are in the database.`

2. Assuming the corrections in "Product_Corrections.xlsx" are in the database, we'll now go through the sales invoice and check if the product is in the database. 
If it isn't, check if it has an entry in the product corrections file. If that fails, add it manually. 
Done. All products in "CVSI Sales Invoice 2025.xlsx," possibly after looking up in `product_corrections_dict.json`, are in the database.


#### Nov 9, 2025 - Started uploading sales invoice data.
1. First step was to recheck that all customers and products can have a customer_id and product_id. Done.

2. Next we need to figure out how to create the sales invoice data.

#### NOv 25, 2025. - Done uploading sales invoice data to cv-solutions.odoo.com.

1. Had to change .env data to be able to upload to cv-solutions.odoo.com.
2. Uploaded 2025 Sales Invoice Monthly.xlsx. but with some errors, which i fixed manually.