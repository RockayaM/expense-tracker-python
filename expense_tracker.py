#Expense Tracker Application:
#This program allows users to add, view, edit, delete, search, and summarise expenses.
#Expense data is persisted using a CSV file (expenses.csv) using pandas.
#Debit entries are treated as spending, while credit entries represent income.
#Data is automatically loaded on startup and saved when the program exits.

import os
import pandas as pd

#Loads expense records from expenses.csv if it exists and returns them as a list of dictionaries
def load_expenses_from_csv():
    if not os.path.exists("expenses.csv"):
        return []
    df = pd.read_csv("expenses.csv")
    expenses = df.to_dict(orient='records')
    for record in expenses:
        record["id"] = int(record["id"])
        record["amount"] = float(record["amount"])
        notes = record.get("notes", "")
        if pd.isna(notes):
            record["notes"] = ""
    return expenses

#Saves the current expense records to expenses.csv
def save_expenses_to_csv(expenses):
    df = pd.DataFrame(expenses)
    df.to_csv("expenses.csv", index=False)

#Displays the main menu options
def show_menu():
    print("1. Add expense")
    print("2. Delete expense")
    print("3. Edit expense")
    print("4. View expenses")
    print("5. Show summary")
    print("6. Search or filter")
    print("7. Exit")

#Generates the next unique expense ID
def get_next_id(expenses):
    if not expenses:
        return 1
    return max(record["id"] for record in expenses) + 1

#Prompts the user for details, validates inputs, and appends a new expense record
def add_expense(expenses):
    new_id = get_next_id(expenses)
    while True:
        date = input("Enter date (YYYY-MM-DD): ").strip()
        dt = pd.to_datetime(date, format="%Y-%m-%d", errors="coerce")
        if pd.isna(dt):
            print("Invalid date. Please use YYYY-MM-DD (e.g., 2026-01-08).")
            continue
        date = dt.strftime("%Y-%m-%d")
        break
    category = input("Enter category: ")
    category = category.strip().lower()

    while True:
        amount = input("Enter an amount: ")
        try:
            amount_float = float(amount)
        except ValueError:
            print("Invalid amount, try again")
            continue
        if amount_float <= 0:
            print("Amount should be greater than 0")
            continue
        elif amount_float > 0:
            amount = amount_float
            break

    while True:
        expense_type = input("Type (d=debit, c=credit):")
        formatted_expense = expense_type.lower().strip()
        if formatted_expense == "d":
            expense_type = "debit"
            break
        elif formatted_expense == "c":
            expense_type = "credit"
            break
        else:
            print("Please enter d or c")
            continue
    notes = input("Notes (optional): ")
    record = {
        "id": new_id,
        "date": date,
        "category": category,
        "amount": amount,
        "type": expense_type,
        "notes": notes
    }
    expenses.append(record)
    print(f"Added expense with ID {new_id}")

#Delete an expense by ID after confirming with the user
def delete_expense(expenses):
    if not expenses:
        print("No expenses to delete.")
        return
    view_expenses(expenses)
    delete_id = input("Enter ID to delete: ")
    try:
        integer_id = int(delete_id)
    except ValueError: 
        print("Invalid ID")
        return
    found_record = None
    for record in expenses:
        if record["id"] == integer_id:
            found_record = record
            break
    if found_record == None:
        print("No expense with that ID")
        return
    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm == "y":
        expenses.remove(found_record)
        print("Expense deleted.")
    else:
        print("Deletion cancelled.")
        
#Edit an existing expense by ID and press Enter to keep current values       
def edit_expense(expenses):
    if not expenses:
        print("No expenses to edit.")
        return
    view_expenses(expenses)
    edit_id = input("Enter ID to edit: ")
    try:
        integer_id = int(edit_id)
    except ValueError:
        print("Invalid ID")
        return
    found_record = None
    for record in expenses:
        if record["id"] == integer_id:
            found_record = record
            break
    if found_record == None:
        print("No expense with that ID.")
        return
    print("Editing expense: ", found_record)

    print("Current date:", found_record['date'])
    while True:
        new_date = input("New date (YYYY-MM-DD, press Enter to keep current): ").strip()
        if not new_date: 
            break
        dt = pd.to_datetime(new_date, format="%Y-%m-%d", errors="coerce")
        if pd.isna(dt):
            print("Invalid date. Please use YYYY-MM-DD (e.g., 2026-01-08).")
            continue
        found_record["date"] = dt.strftime("%Y-%m-%d")
        break

    print("Current category:", found_record["category"])
    new_category = input("New category (press Enter to keep current category): ").strip()
    if new_category:
        found_record["category"] = new_category

    print("Current amount:", found_record['amount'])
    new_amount = input("New amount (press Enter to keep current): ").strip()
    if new_amount:
        while True:
            try:
                new_amount_float = float(new_amount)
            except ValueError:
                print("Invalid amount, try again.")
                new_amount = input("New amount (press Enter to keep current): ").strip()
                continue
            if new_amount_float <= 0:
                print("Amount must be greater than 0")
                new_amount = input("New amount (press Enter to keep current): ").strip()
                continue
            else:
                found_record["amount"] = new_amount_float
                break

    print("Current type: ", found_record["type"])
    new_type = input("New type (d=debit, c=credit, press Enter to keep): ").strip().lower()
    if new_type:
        while True:
            if new_type == "d":
                found_record["type"] = "debit"
                break
            elif new_type == "c":
                found_record["type"] = "credit"
                break
            else:
                print("Please enter d or c")
                new_type = input("New type (d=debit, c=credit, press Enter to keep): ").strip().lower()

    print("Current notes: ", found_record['notes'])
    new_notes = input("New notes (press Enter to keep current): ").strip()
    if new_notes:
        found_record['notes'] = new_notes
    print("Expense updated.")

#Prints all expenses in a simple table format
def view_expenses(expenses):
    if not expenses:
        print("No expenses recorded.")
        return
    print("ID | Date | Category | Amount | Type | Notes")
    for record in expenses:
        print(record["id"], "|", record["date"], "|", record["category"], "|", record["amount"], "|", record["type"], "|", record["notes"])

#Show spending summaries (daily/weekly/monthly) and the highest spending category
def show_summary(expenses):
    if not expenses:
        print("No expenses recorded.")
        return
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(subset=["date"], inplace=True)
    spend_df = df[df['type'] == 'debit'].copy()
    if spend_df.empty: 
        print("No debit (spending) records to summarise.")
        return
    
    spend_df['date'] = pd.to_datetime(spend_df['date'])
    print("Daily totals: ")
    daily_totals = spend_df.groupby(spend_df["date"].dt.date)["amount"].sum()
    for day, total in daily_totals.items():
        print(f"{day}: {total:.2f}")

    print("Weekly totals: ")
    iso = spend_df["date"].dt.isocalendar()
    weekly_totals = spend_df.groupby([iso["year"], iso["week"]])["amount"].sum()
    for (year, week), total in weekly_totals.items():
        print(f"{year}-W{int(week):02d}: {total:.2f}")

    print("Monthly totals: ")
    month_key = spend_df["date"].dt.to_period("M").astype(str)
    monthly_totals = spend_df.groupby(month_key)["amount"].sum()
    for month, total in monthly_totals.items():
        print(f"{month}: {total:.2f}")

    category_totals = spend_df.groupby("category")["amount"].sum()
    top_category = category_totals.idxmax()
    top_amount = category_totals.max()
    print(f"Highest spending category: {top_category} ({top_amount:.2f})")

    #Extra: calculate total debit, total credit, and net balance
    total_debit = df[df["type"] == "debit"]["amount"].sum()
    total_credit = df[df["type"] == "credit"]["amount"].sum()
    net_balance = total_credit - total_debit
    print(f"Total debit (spending): {total_debit:.2f}")
    print(f"Total credit (income): {total_credit:.2f}")
    print(f"Net balance (credit - debit): {net_balance:.2f}")

#Filter expenses by category, date range, or amount range and display matching records
def search_filter(expenses):
    if not expenses:
        print("No expenses recorded.")
        return
    print("Search/filter")
    print("1. Filter by category")
    print("2. Filter by date range")
    print("3. Filter by amount range")
    print("4. Back")

    choice = input("Choose an option: ").strip()
    df = pd.DataFrame(expenses)
    if choice == "1":
        category = input("Enter category to filter by: ").strip().lower()
        filtered_df = df[df["category"].astype(str).str.lower() == category].copy()

    elif choice == "2":
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        start_dt = pd.to_datetime(start, errors="coerce")
        end_dt = pd.to_datetime(end, errors="coerce")
        if pd.isna(start_dt) or pd.isna(end_dt):
            print("Invalid start or end date.")
            return
        filtered_df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)].copy()

    elif choice == "3":
        min_amt_str = input("Minimum amount: ").strip()
        max_amt_str = input("Maximum amount: ").strip()
        try: 
            min_amt = float(min_amt_str)
            max_amt = float(max_amt_str)
        except ValueError:
            print("Invalid amount range.")
            return
        filtered_df = df[(df["amount"] >= min_amt) & (df["amount"] <= max_amt)].copy()

    elif choice == "4":
        return
    else: 
        print("Invalid choice.")
        return
    if "date" in filtered_df.columns:
        filtered_df["date"] = pd.to_datetime(filtered_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    filtered_expenses = filtered_df.to_dict(orient="records")
    
    if not filtered_expenses:
        print("No matching records found.")
        return
    
    view_expenses(filtered_expenses)

    #Extra: asks user if they want to export the filtered results, if they type y, it saves the same filtered results to a new file
    export = input("Export these results to filtered_expenses.csv? (y/n): ").strip().lower()
    if export == "y":
        filtered_df.to_csv("filtered_expenses.csv", index=False)
        print("Exported to filtered_expenses.csv")
    else:
        print("Export cancelled.")

#Load data, run menu loop, and save on exit
def main():
    expenses = load_expenses_from_csv()
    while True:
        show_menu()
        num = input("Choose a corresponding number: ")
        if num == "1":
            add_expense(expenses)
        elif num == "2":
            delete_expense(expenses)
        elif num == "3":
            edit_expense(expenses)
        elif num == "4":
            view_expenses(expenses)
        elif num == "5":
            show_summary(expenses)
        elif num == "6":
            search_filter(expenses)
        elif num == "7":
            save_expenses_to_csv(expenses)
            print("Saved to expenses.csv. Done, goodbye!")
            break
        else:
            print("Invalid Choice")

main()


