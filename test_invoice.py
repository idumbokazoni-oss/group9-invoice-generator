import os, tempfile
from invoice_system import Item, Invoice, save_invoice, find_invoice, monthly_summary

inv = Invoice("INV-0001", "Test", "2026-11-01")
inv.add_item(Item("Pen", 2.0, 10))     # 20
inv.add_item(Item("Book", 5.0, 4))     # 20
inv.set_discount(10)                   # -4
assert inv.subtotal() == 40
assert round(inv.tax_amount(), 2) == 5.40
assert round(inv.total(), 2) == 41.40
inv.remove_item(1)
assert inv.subtotal() == 20
p = os.path.join(tempfile.mkdtemp(), "t.json")
save_invoice(inv, p)
assert find_invoice("inv-0001", p).total() == inv.total()
assert find_invoice("INV-9999", p) is None
assert monthly_summary("2026-11", p)[0] == 1
print("All tests passed")
