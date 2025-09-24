# LocalBill – GST Invoice Maker

A simple desktop application to generate GST-compliant invoices for local businesses. Built with Python and Tkinter.

## Features
- Add multiple items with price, quantity, and GST percentage
- Calculates GST and total amount automatically
- Customer name and contact fields (optional)
- Generates and saves invoices as CSV files in the `data/` folder
- Simple, user-friendly interface

## How to Use
1. **Run the application:**
   ```sh
   python main.py
   ```
2. **Enter customer details** (optional).
3. **Add items:** Enter item name, price, quantity, and select GST%. Click "Add Item" for each product.
4. **View bill:** All items and totals are shown in the table.
5. **Generate invoice:** Click "Generate Invoice" to save the bill as a CSV file in the `data/` folder.

## Example Output
A generated CSV invoice looks like this:

```
Item,Price,Quantity,GST%,Total
dhokla ,250.0,1,5,262.5
samosa ,100.0,5,5,525.0
```

## Requirements
- Python 3.x
- Tkinter (usually included with Python)

## Project Structure
- `main.py` – Main application code
- `data/` – Folder where invoices are saved as CSV files

---

Feel free to use, modify, and share this project!!
