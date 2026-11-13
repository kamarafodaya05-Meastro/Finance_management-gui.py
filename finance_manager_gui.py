"""
Personal Finance Manager - Tkinter GUI Version
Author: FODAY A. KAMARA -- Group 5
ID: 003860
Course: Computer Science
Module: Principle of Structured Programming
Lecturer: Mr. Kanga

Same features as the console version, in a graphical window:
- Add income and expenses with input validation
- Tables (Treeview) for income and expense records
- Live summary: total income, total expenses, remaining money
- Savings goal tracking with progress bar
- Financial advice
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------------------------------------------- data
income_records = []
expense_records = []
savings_goal = 0.0

# Widgets that need to be reached from several functions
ui = {}

# ---------------------------------------------------------------- colors
BG = "#f4f6f8"
GREEN = "#1e8e3e"
RED = "#d93025"
ORANGE = "#e37400"
BLUE = "#1a73e8"


# ---------------------------------------------------------------- logic
def parse_amount(text):
    """Return a positive float from text, or None if invalid."""
    try:
        value = int(text.strip())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a numeric value.")
        return None
    if value <= 0:
        messagebox.showerror("Invalid input", "Amount must be greater than zero.")
        return None
    return value


def add_income():
    amount = parse_amount(ui["income_amount"].get())
    if amount is None:
        return
    source = ui["income_source"].get().strip()
    if not source:
        messagebox.showerror("Invalid input", "Income source cannot be blank.")
        return

    income_records.append({"amount": amount, "source": source})
    ui["income_amount"].delete(0, tk.END)
    ui["income_source"].delete(0, tk.END)
    refresh_all()


def add_expense():
    amount = parse_amount(ui["expense_amount"].get())
    if amount is None:
        return
    category = ui["expense_category"].get().strip()
    if not category:
        messagebox.showerror("Invalid input", "Expense category cannot be blank.")
        return

    expense_records.append({"amount": amount, "category": category})
    ui["expense_amount"].delete(0, tk.END)
    ui["expense_category"].delete(0, tk.END)
    refresh_all()


def set_savings_goal():
    global savings_goal
    try:
        goal = float(ui["goal_entry"].get().strip())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a numeric value.")
        return
    if goal < 0:
        messagebox.showerror("Invalid input", "Goal cannot be negative.")
        return

    savings_goal = goal
    refresh_all()


def delete_selected(tree, records):
    selection = tree.selection()
    if not selection:
        messagebox.showinfo("Nothing selected", "Select a row to delete first.")
        return
    index = tree.index(selection[0])
    del records[index]
    refresh_all()


def get_advice(total_income, remaining):
    if remaining < 0:
        return "Warning: You are spending more than you earn. Reduce unnecessary expenses.", RED
    if total_income == 0:
        return "Add income records to get a more useful financial summary.", ORANGE
    if remaining / total_income < 0.2:
        return "Try to save more. Aim for at least 20% of your income.", ORANGE
    return "Great job! You are managing your finances well. Keep tracking your expenses.", GREEN


# ---------------------------------------------------------------- display
def refresh_tables():
    for tree, records, key in (
        (ui["income_tree"], income_records, "source"),
        (ui["expense_tree"], expense_records, "category"),
    ):
        tree.delete(*tree.get_children())
        for number, record in enumerate(records, start=1):
            tree.insert("", tk.END, values=(number, record[key], f"{record['amount']:.2f}"))


def refresh_summary():
    total_income = sum(item["amount"] for item in income_records)
    total_expense = sum(item["amount"] for item in expense_records)
    remaining = total_income - total_expense

    ui["total_income"].config(text=f"Total Income: {total_income:.2f}")
    ui["total_expense"].config(text=f"Total Expenses: {total_expense:.2f}")
    ui["remaining"].config(
        text=f"Remaining Money: {remaining:.2f}",
        fg=RED if remaining < 0 else GREEN,
    )

    # Savings goal section
    if savings_goal > 0:
        rate = (remaining / total_income * 100) if total_income > 0 else 0
        percent = max(0, min(100, remaining / savings_goal * 100))
        ui["progress"]["value"] = percent
        if remaining >= savings_goal:
            message, color = f"Congratulations! You met your savings goal of {savings_goal:.2f}!", GREEN
        else:
            message, color = f"You need {savings_goal - remaining:.2f} more to reach your goal.", ORANGE
        ui["goal_status"].config(text=f"Savings Rate: {rate:.2f}%   |   {message}", fg=color)
    else:
        ui["progress"]["value"] = 0
        ui["goal_status"].config(text="No savings goal set.", fg="gray")

    advice, color = get_advice(total_income, remaining)
    ui["advice"].config(text=advice, fg=color)


def refresh_all():
    refresh_tables()
    refresh_summary()


# ---------------------------------------------------------------- layout
def make_table(parent, second_column):
    frame = tk.Frame(parent, bg=BG)
    tree = ttk.Treeview(frame, columns=("no", "name", "amount"), show="headings", height=6)
    tree.heading("no", text="#")
    tree.heading("name", text=second_column)
    tree.heading("amount", text="Amount")
    tree.column("no", width=40, anchor="center")
    tree.column("name", width=180)
    tree.column("amount", width=100, anchor="e")

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame, tree


def build_entry_panel(parent, title, label_text, color, amount_key, name_key, add_command, tree_key, records, column):
    panel = tk.LabelFrame(parent, text=title, fg=color, bg=BG, font=("Segoe UI", 11, "bold"), padx=10, pady=8)

    tk.Label(panel, text="Amount:", bg=BG).grid(row=0, column=0, sticky="w")
    ui[amount_key] = ttk.Entry(panel, width=18)
    ui[amount_key].grid(row=0, column=1, padx=6, pady=3)

    tk.Label(panel, text=label_text, bg=BG).grid(row=1, column=0, sticky="w")
    ui[name_key] = ttk.Entry(panel, width=18)
    ui[name_key].grid(row=1, column=1, padx=6, pady=3)

    ttk.Button(panel, text="Add", command=add_command).grid(row=0, column=2, rowspan=2, padx=6, sticky="ns")

    table_frame, tree = make_table(panel, column)
    ui[tree_key] = tree
    table_frame.grid(row=2, column=0, columnspan=3, pady=(8, 4), sticky="nsew")

    ttk.Button(
        panel, text="Delete Selected",
        command=lambda: delete_selected(tree, records),
    ).grid(row=3, column=0, columnspan=3, sticky="e")

    panel.columnconfigure(1, weight=1)
    return panel


def build_ui(root):
    root.title("Personal Finance Manager")
    root.configure(bg=BG)
    root.minsize(900, 600)

    tk.Label(root, text="Personal Finance Manager", bg=BG, fg=BLUE,
             font=("Segoe UI", 18, "bold")).pack(pady=(12, 4))

    # Income and expense panels side by side
    top = tk.Frame(root, bg=BG)
    top.pack(fill="both", expand=True, padx=12)
    top.columnconfigure((0, 1), weight=1)

    build_entry_panel(top, "Income", "Source:", GREEN, "income_amount", "income_source",
                      add_income, "income_tree", income_records, "Source"
                      ).grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    build_entry_panel(top, "Expenses", "Category:", ORANGE, "expense_amount", "expense_category",
                      add_expense, "expense_tree", expense_records, "Category"
                      ).grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    # Savings goal
    goal_frame = tk.LabelFrame(root, text="Savings Goal", bg=BG, font=("Segoe UI", 11, "bold"), padx=10, pady=8)
    goal_frame.pack(fill="x", padx=12, pady=8)
    tk.Label(goal_frame, text="Monthly savings goal:", bg=BG).grid(row=0, column=0, sticky="w")
    ui["goal_entry"] = ttk.Entry(goal_frame, width=16)
    ui["goal_entry"].grid(row=0, column=1, padx=6)
    ttk.Button(goal_frame, text="Set Goal", command=set_savings_goal).grid(row=0, column=2)
    ui["progress"] = ttk.Progressbar(goal_frame, length=250, maximum=100)
    ui["progress"].grid(row=0, column=3, padx=12)
    ui["goal_status"] = tk.Label(goal_frame, text="", bg=BG)
    ui["goal_status"].grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

    # Summary
    summary = tk.LabelFrame(root, text="Summary", bg=BG, font=("Segoe UI", 11, "bold"), padx=10, pady=8)
    summary.pack(fill="x", padx=12, pady=(0, 12))
    ui["total_income"] = tk.Label(summary, bg=BG, fg=BLUE, font=("Segoe UI", 11))
    ui["total_expense"] = tk.Label(summary, bg=BG, fg=ORANGE, font=("Segoe UI", 11))
    ui["remaining"] = tk.Label(summary, bg=BG, font=("Segoe UI", 11, "bold"))
    for column, key in enumerate(("total_income", "total_expense", "remaining")):
        ui[key].grid(row=0, column=column, padx=15, sticky="w")
    ui["advice"] = tk.Label(summary, bg=BG, font=("Segoe UI", 10, "italic"))
    ui["advice"].grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(6, 0))

    refresh_all()


def main():
    root = tk.Tk()
    build_ui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
