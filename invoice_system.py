"""
Small Business Invoice and Receipt Generator
CSC1101 - Principles of Programming Languages, Africa University
Group 9 - Case 16
"""
import json
import os
from datetime import datetime

DATA_FILE = "invoices.json"
TAX_RATE = 0.15  # 15% tax; change here if the rate changes


class Item:
    """One line on an invoice."""

    def __init__(self, description, unit_price, quantity):
        if not description.strip():
            raise ValueError("Description cannot be empty.")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        if quantity <= 0 or int(quantity) != quantity:
            raise ValueError("Quantity must be a whole number above zero.")
        self.description = description.strip()
        self.unit_price = float(unit_price)
        self.quantity = int(quantity)

    def line_total(self):
        return self.unit_price * self.quantity

    def to_dict(self):
        return {"description": self.description,
                "unit_price": self.unit_price,
                "quantity": self.quantity}


class Invoice:
    """An invoice holding a list of Item objects."""

    def __init__(self, number, customer, date=None, discount_percent=0.0, tax_rate=TAX_RATE):
        self.number = number
        self.customer = customer
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.items = []
        self.discount_percent = discount_percent
        self.tax_rate = tax_rate

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, position):
        """Remove by 1-based position on the invoice."""
        if position < 1 or position > len(self.items):
            raise IndexError("No item at that position.")
        return self.items.pop(position - 1)

    def set_discount(self, percent):
        if percent < 0 or percent > 100:
            raise ValueError("Discount must be between 0 and 100.")
        self.discount_percent = float(percent)

    # --- calculations live here so every total comes from one place ---
    def subtotal(self):
        return sum(item.line_total() for item in self.items)

    def discount_amount(self):
        return self.subtotal() * self.discount_percent / 100

    def tax_amount(self):
        return (self.subtotal() - self.discount_amount()) * self.tax_rate

    def total(self):
        return self.subtotal() - self.discount_amount() + self.tax_amount()

    def receipt(self):
        line = "=" * 56
        out = [line, "SMALL BUSINESS RECEIPT".center(56), line,
               f"Invoice No: {self.number}", f"Customer  : {self.customer}",
               f"Date      : {self.date}", "-" * 56,
               f"{'#':<3}{'Description':<24}{'Price':>9}{'Qty':>5}{'Total':>12}",
               "-" * 56]
        for i, it in enumerate(self.items, 1):
            out.append(f"{i:<3}{it.description[:23]:<24}{it.unit_price:>9.2f}"
                       f"{it.quantity:>5}{it.line_total():>12.2f}")
        out += ["-" * 56,
                f"{'Subtotal':<44}{self.subtotal():>12.2f}",
                f"{'Discount (' + format(self.discount_percent, '.1f') + '%)':<44}"
                f"{-self.discount_amount():>12.2f}",
                f"{'Tax (' + format(self.tax_rate * 100, '.1f') + '%)':<44}"
                f"{self.tax_amount():>12.2f}",
                line, f"{'TOTAL':<44}{self.total():>12.2f}", line,
                "Thank you for your business!"]
        return "\n".join(out)

    def to_dict(self):
        return {"number": self.number, "customer": self.customer,
                "date": self.date, "discount_percent": self.discount_percent,
                "tax_rate": self.tax_rate,
                "items": [i.to_dict() for i in self.items]}

    @staticmethod
    def from_dict(d):
        inv = Invoice(d["number"], d["customer"], d["date"],
                      d["discount_percent"], d["tax_rate"])
        for i in d["items"]:
            inv.add_item(Item(i["description"], i["unit_price"], i["quantity"]))
        return inv


# ---------------- file handling ----------------
def load_all(path=DATA_FILE):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read the invoice file; starting empty.")
        return []


def save_invoice(invoice, path=DATA_FILE):
    """Save or replace an invoice (matched by number)."""
    records = [r for r in load_all(path) if r["number"] != invoice.number]
    records.append(invoice.to_dict())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def find_invoice(number, path=DATA_FILE):
    for r in load_all(path):
        if r["number"].lower() == number.lower():
            return Invoice.from_dict(r)
    return None


def next_invoice_number(path=DATA_FILE):
    return f"INV-{len(load_all(path)) + 1:04d}"


def monthly_summary(month, path=DATA_FILE):
    """Stretch challenge: month is 'YYYY-MM'."""
    invs = [Invoice.from_dict(r) for r in load_all(path) if r["date"].startswith(month)]
    return len(invs), sum(i.total() for i in invs)


# ---------------- console interface ----------------
def ask_number(prompt, kind=float):
    while True:
        try:
            return kind(input(prompt))
        except ValueError:
            print("  Please enter a valid number.")


def edit_invoice(inv):
    while True:
        print("\n1 Add item  2 Remove item  3 Set discount  4 Show receipt  5 Save & finish")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                d = input("  Description: ")
                p = ask_number("  Unit price: ")
                q = ask_number("  Quantity: ", int)
                inv.add_item(Item(d, p, q))
            elif choice == "2":
                inv.remove_item(ask_number("  Item number to remove: ", int))
            elif choice == "3":
                inv.set_discount(ask_number("  Discount %: "))
            elif choice == "4":
                print(inv.receipt())
            elif choice == "5":
                if not inv.items:
                    print("  Add at least one item first.")
                    continue
                save_invoice(inv)
                print(inv.receipt())
                print(f"Saved as {inv.number}.")
                return
            else:
                print("  Invalid choice.")
        except (ValueError, IndexError) as e:
            print(f"  Error: {e}")


def main():
    while True:
        print("\n=== INVOICE & RECEIPT GENERATOR ===")
        print("1 New invoice  2 Find invoice by number  3 Monthly summary  4 Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            customer = input("Customer name: ").strip() or "Walk-in customer"
            edit_invoice(Invoice(next_invoice_number(), customer))
        elif choice == "2":
            inv = find_invoice(input("Invoice number (e.g. INV-0001): ").strip())
            print(inv.receipt() if inv else "No invoice found with that number.")
        elif choice == "3":
            month = input("Month (YYYY-MM): ").strip()
            count, total = monthly_summary(month)
            print(f"{count} invoice(s) in {month}, total sales: {total:.2f}")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
