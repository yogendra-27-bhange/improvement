import ttkbootstrap as tb
from ttkbootstrap.constants import *

import csv
from datetime import datetime
from fpdf import FPDF
import os
import webbrowser

# Global list to store invoice data
invoice_items = []

# GST % options
gst_options = [5, 12, 18, 28]

def add_item():
    item = item_entry.get()
    try:
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
        gst = int(gst_var.get())
        item_discount_type = item_discount_type_var.get()
        item_discount_value = float(item_discount_value_var.get()) if item_discount_value_var.get() else 0.0
    except ValueError:
        tb.messagebox.show_error("Input Error", "Enter valid numeric values.")
        return

    # Calculate per-item discount
    if item_discount_type == "Percent":
        discount_amt = price * item_discount_value / 100
    elif item_discount_type == "Amount":
        discount_amt = item_discount_value
    else:
        discount_amt = 0.0
    price_after_discount = max(price - discount_amt, 0)
    gst_amount = (price_after_discount * gst / 100)
    total_price = (price_after_discount + gst_amount) * quantity

    invoice_items.append([item, price, quantity, gst, round(total_price, 2), item_discount_type, item_discount_value])

    update_table()
    clear_fields()

def update_table():
    for row in bill_table.get_children():
        bill_table.delete(row)
    subtotal = 0
    for idx, row in enumerate(invoice_items):
        bill_table.insert("", "end", values=row[:5] + row[5:])
        subtotal += row[4]
    # Apply overall discount
    discount_type = overall_discount_type.get()
    discount_value = overall_discount_value.get()
    if discount_type == "Percent":
        overall_discount_amt = subtotal * discount_value / 100
    elif discount_type == "Amount":
        overall_discount_amt = discount_value
    else:
        overall_discount_amt = 0.0
    grand_total = max(subtotal - overall_discount_amt, 0)
    total_var.set(f"₹ {round(grand_total, 2)}")
    subtotal_var.set(f"₹ {round(subtotal, 2)}")
    discount_var.set(f"-₹ {round(overall_discount_amt, 2)}")

def clear_fields():
    item_entry.delete(0, tb.END)
    price_entry.delete(0, tb.END)
    quantity_entry.delete(0, tb.END)
    gst_var.set(gst_options[0])
    item_discount_type_var.set("None")
    item_discount_value_var.set(0.0)

def preview_invoice():
    if not invoice_items:
        tb.messagebox.show_warning("Empty Bill", "Add at least one item.")
        return
    # Create preview window
    preview_win = tb.Toplevel(root)
    preview_win.title("Invoice Preview")
    preview_win.geometry("700x500")
    tb.Label(preview_win, text="Invoice Preview", font=("Segoe UI", 16, "bold"), bootstyle="inverse-primary").pack(pady=10)
    # Table
    cols = ("Item", "Price", "Quantity", "GST%", "Total", "Discount Type", "Discount Value")
    preview_table = tb.Treeview(preview_win, columns=cols, show="headings", bootstyle="info")
    for col in cols:
        preview_table.heading(col, text=col)
        preview_table.column(col, anchor=CENTER, width=90)
    for row in invoice_items:
        preview_table.insert("", "end", values=row)
    preview_table.pack(fill="both", expand=True, padx=10, pady=10)
    # Summary
    summary_frame = tb.Frame(preview_win, bootstyle="light")
    summary_frame.pack(fill="x", padx=10, pady=5)
    tb.Label(summary_frame, text=f"Subtotal: {subtotal_var.get()}", font=("Segoe UI", 11), bootstyle="info").pack(side="left", padx=10)
    tb.Label(summary_frame, text=f"Overall Discount: {discount_var.get()}", font=("Segoe UI", 11), bootstyle="danger").pack(side="left", padx=10)
    tb.Label(summary_frame, text=f"Grand Total: {total_var.get()}", font=("Segoe UI", 12, "bold"), bootstyle="success").pack(side="left", padx=10)
    # Buttons
    btn_frame = tb.Frame(preview_win)
    btn_frame.pack(pady=10)
    def save_and_close():
        preview_win.destroy()
        generate_invoice(save_only=True)
    def cancel():
        preview_win.destroy()
    def save_pdf():
        filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "GST Invoice", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, f"Customer: {cust_name.get()}  Contact: {cust_contact.get()}", ln=True)
        pdf.ln(5)
        # Table header
        pdf.set_font("Arial", "B", 11)
        col_widths = [30, 20, 20, 20, 25, 30, 30]
        headers = ["Item", "Price", "Qty", "GST%", "Total", "Disc Type", "Disc Value"]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, align="C")
        pdf.ln()
        pdf.set_font("Arial", size=10)
        for row in invoice_items:
            for i, val in enumerate(row):
                pdf.cell(col_widths[i], 8, str(val), border=1, align="C")
            pdf.ln()
        pdf.ln(2)
        # Summary
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, f"Subtotal: {subtotal_var.get()}", ln=True)
        pdf.cell(0, 8, f"Overall Discount: {discount_var.get()}", ln=True)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Grand Total: {total_var.get()}", ln=True)
        pdf.output(f"data/{filename}")
        tb.messagebox.show_info("PDF Saved", f"Invoice PDF saved as {filename}")
    save_btn = tb.Button(btn_frame, text="💾 Save Invoice", bootstyle="success", command=save_and_close, width=16)
    save_btn.pack(side="left", padx=10)
    cancel_btn = tb.Button(btn_frame, text="Cancel", bootstyle="danger", command=cancel, width=10)
    cancel_btn.pack(side="left", padx=10)
    pdf_btn = tb.Button(btn_frame, text="🖨️ Save as PDF", bootstyle="info", command=save_pdf, width=14)
    pdf_btn.pack(side="left", padx=10)

def generate_invoice(save_only=False):
    if not save_only:
        preview_invoice()
        return
    if not invoice_items:
        tb.messagebox.show_warning("Empty Bill", "Add at least one item.")
        return
    filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(f"data/{filename}", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Item", "Price", "Quantity", "GST%", "Total", "Discount Type", "Discount Value"])
        for row in invoice_items:
            writer.writerow(row)
        writer.writerow(["", "", "", "Subtotal", subtotal_var.get()])
        writer.writerow(["", "", "", "Overall Discount", discount_var.get()])
        writer.writerow(["", "", "", "Grand Total", total_var.get()])
    tb.messagebox.show_info("Success", f"Invoice saved as {filename}")
    invoice_items.clear()
    update_table()

# Invoice History window
def show_invoice_history():
    history_win = tb.Toplevel(root)
    history_win.title("Invoice History")
    history_win.geometry("600x400")
    tb.Label(history_win, text="Invoice History", font=("Segoe UI", 15, "bold"), bootstyle="inverse-primary").pack(pady=10)
    files = [f for f in os.listdir("data") if f.startswith("invoice_") and (f.endswith(".csv") or f.endswith(".pdf"))]
    files.sort(reverse=True)
    file_list = tb.Treeview(history_win, columns=("Name", "Type"), show="headings", height=12, bootstyle="info")
    file_list.heading("Name", text="File Name")
    file_list.heading("Type", text="Type")
    file_list.column("Name", width=350)
    file_list.column("Type", width=80)
    for f in files:
        ext = f.split(".")[-1].upper()
        file_list.insert("", "end", values=(f, ext))
    file_list.pack(fill="both", expand=True, padx=10, pady=10)
    def open_selected():
        sel = file_list.selection()
        if not sel:
            tb.messagebox.show_warning("No Selection", "Select a file to open.")
            return
        fname = file_list.item(sel[0], "values")[0]
        if fname.endswith(".csv"):
            show_csv_invoice(os.path.join("data", fname))
        elif fname.endswith(".pdf"):
            webbrowser.open(os.path.abspath(os.path.join("data", fname)))
    open_btn = tb.Button(history_win, text="Open Selected", bootstyle="primary", command=open_selected)
    open_btn.pack(pady=5)

# Show CSV invoice in a table
def show_csv_invoice(path):
    csv_win = tb.Toplevel(root)
    csv_win.title(f"Invoice: {os.path.basename(path)}")
    csv_win.geometry("700x500")
    tb.Label(csv_win, text=os.path.basename(path), font=("Segoe UI", 13, "bold"), bootstyle="info").pack(pady=8)
    with open(path, newline="") as f:
        reader = list(csv.reader(f))
    if not reader:
        tb.Label(csv_win, text="Empty invoice file.").pack()
        return
    cols = reader[0]
    table = tb.Treeview(csv_win, columns=cols, show="headings", bootstyle="info")
    for col in cols:
        table.heading(col, text=col)
        table.column(col, anchor=CENTER, width=90)
    for row in reader[1:]:
        table.insert("", "end", values=row)
    table.pack(fill="both", expand=True, padx=10, pady=10)

# ===================== GUI SETUP ============================
# Use ttkbootstrap's themed root
root = tb.Window(themename="minty")  # Changed to a more vibrant theme
root.title("LocalBill – GST Invoice Maker")
root.geometry("900x600")

style = tb.Style()

# Initialize all StringVar/DoubleVar after root is created
overall_discount_type = tb.StringVar(value="None")  # None, Percent, Amount
overall_discount_value = tb.DoubleVar(value=0.0)
item_discount_type_var = tb.StringVar(value="None")
item_discount_value_var = tb.StringVar(value="0.0")
subtotal_var = tb.StringVar(value="₹ 0.00")
discount_var = tb.StringVar(value="-₹ 0.00")
total_var = tb.StringVar(value="₹ 0.00")
gst_var = tb.StringVar(value=gst_options[0])

# Modern title label with icon
header_frame = tb.Frame(root, bootstyle="primary", padding=10)
header_frame.pack(fill="x")
title = tb.Label(header_frame, text="🧾 LocalBill – GST Invoice Maker", font=("Segoe UI", 20, "bold"), bootstyle="inverse-primary")
title.pack(pady=5, fill=X, side="left")
history_btn = tb.Button(header_frame, text="📂 Invoice History", bootstyle="info outline", command=show_invoice_history, width=18)
history_btn.pack(pady=5, padx=10, side="right")

main_frame = tb.Frame(root, bootstyle="light", padding=10)
main_frame.pack(padx=10, pady=5, fill="both", expand=True)

# --- Card: Customer Details ---
cust_card = tb.Labelframe(main_frame, text="👤 Customer Details", bootstyle="info", padding=10)
cust_card.pack(fill="x", pady=5)

# Customer Details (optional)
tb.Label(cust_card, text="Customer Name:", bootstyle="secondary").grid(row=0, column=0, padx=5, pady=2, sticky=W)
cust_name = tb.Entry(cust_card, width=25)
cust_name.grid(row=0, column=1, padx=5)

tb.Label(cust_card, text="Contact No.:", bootstyle="secondary").grid(row=0, column=2, padx=5, sticky=W)
cust_contact = tb.Entry(cust_card, width=20)
cust_contact.grid(row=0, column=3, padx=5)

# --- Card: Item Entry ---
item_card = tb.Labelframe(main_frame, text="🛒 Add Item", bootstyle="info", padding=10)
item_card.pack(fill="x", pady=5)

tb.Label(item_card, text="Item:", bootstyle="secondary").grid(row=0, column=0, padx=5, sticky=W)
item_entry = tb.Entry(item_card, width=20)
item_entry.grid(row=0, column=1, padx=5)

tb.Label(item_card, text="Price:", bootstyle="secondary").grid(row=0, column=2, sticky=W)
price_entry = tb.Entry(item_card, width=10)
price_entry.grid(row=0, column=3, padx=5)

tb.Label(item_card, text="Qty:", bootstyle="secondary").grid(row=0, column=4, sticky=W)
quantity_entry = tb.Entry(item_card, width=6)
quantity_entry.grid(row=0, column=5, padx=5)

tb.Label(item_card, text="GST%:", bootstyle="secondary").grid(row=0, column=6, sticky=W)
gst_menu = tb.Combobox(item_card, textvariable=gst_var, values=gst_options, width=5, state="readonly", bootstyle="info")
gst_menu.grid(row=0, column=7, padx=5)

add_btn = tb.Button(item_card, text="➕ Add Item", command=add_item, bootstyle="primary outline", width=14)
add_btn.grid(row=0, column=8, padx=10)

# Per-item discount fields
discount_type_menu = tb.Combobox(item_card, textvariable=item_discount_type_var, values=["None", "Percent", "Amount"], width=8, state="readonly", bootstyle="info")
discount_type_menu.grid(row=1, column=1, padx=5)
discount_value_entry = tb.Entry(item_card, textvariable=item_discount_value_var, width=10)
discount_value_entry.grid(row=1, column=2, padx=5)

# --- Card: Invoice Table ---
table_card = tb.Labelframe(main_frame, text="📋 Invoice Items", bootstyle="info", padding=10)
table_card.pack(fill="both", expand=True, pady=5)

cols = ("Item", "Price", "Quantity", "GST%", "Total", "Discount Type", "Discount Value")
bill_table = tb.Treeview(table_card, columns=cols, show="headings", bootstyle="info")
for col in cols:
    bill_table.heading(col, text=col)
    bill_table.column(col, anchor=CENTER, width=120)
bill_table.pack(fill="both", expand=True)

# Add a style for the table
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
style.configure("Treeview", font=("Segoe UI", 10))

# --- Card: Summary & Actions ---
summary_card = tb.Labelframe(main_frame, text="📊 Summary", bootstyle="info", padding=10)
summary_card.pack(fill="x", pady=5)

# Subtotal
sub_frame = tb.Frame(summary_card, bootstyle="light")
sub_frame.pack(side="left", padx=10)
tb.Label(sub_frame, text="Subtotal:", font=("Segoe UI", 11), bootstyle="secondary").pack(side="left")
tb.Label(sub_frame, textvariable=subtotal_var, font=("Segoe UI", 11, "bold"), bootstyle="info").pack(side="left", padx=5)

# Overall Discount
overall_disc_frame = tb.Frame(summary_card, bootstyle="light")
overall_disc_frame.pack(side="left", padx=10)
tb.Label(overall_disc_frame, text="Overall Discount:", font=("Segoe UI", 11), bootstyle="secondary").pack(side="left")
overall_discount_type_menu = tb.Combobox(overall_disc_frame, textvariable=overall_discount_type, values=["None", "Percent", "Amount"], width=8, state="readonly", bootstyle="info")
overall_discount_type_menu.pack(side="left", padx=2)
overall_discount_value_entry = tb.Entry(overall_disc_frame, textvariable=overall_discount_value, width=8)
overall_discount_value_entry.pack(side="left", padx=2)
tb.Label(overall_disc_frame, textvariable=discount_var, font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=5)

# Grand Total
grand_frame = tb.Frame(summary_card, bootstyle="light")
grand_frame.pack(side="left", padx=10)
tb.Label(grand_frame, text="Grand Total:", font=("Segoe UI", 13), bootstyle="secondary").pack(side="left")
tb.Label(grand_frame, textvariable=total_var, font=("Segoe UI", 13, "bold"), bootstyle="success").pack(side="left", padx=5)

gen_btn = tb.Button(summary_card, text="💾 Generate Invoice", bootstyle="success outline", command=generate_invoice, width=20)
gen_btn.pack(side="right", padx=10)

# Responsive resizing
main_frame.rowconfigure(2, weight=1)
main_frame.columnconfigure(0, weight=1)

root.mainloop()