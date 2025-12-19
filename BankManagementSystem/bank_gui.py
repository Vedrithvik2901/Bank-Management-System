"""
Bank Account Management System - Complete GUI with Tkinter
Ready to run - just update credentials!
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import sys

try:
    from bank_database import BankDatabase
except ImportError:
    print("Error: Make sure bank_database.py is in the same folder!")
    sys.exit(1)


class BankManagementApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Account Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        self.USERNAME = "SYS"
        self.PASSWORD = "oracle@express"  
        self.DSN = "localhost:1521/XE"
        
        self.db = BankDatabase(self.USERNAME, self.PASSWORD, self.DSN)
        self.current_customer = None
        self.current_accounts = []
        
        if not self.db.connect():
            messagebox.showerror("Connection Error", 
                               "Failed to connect to Oracle Database!\nPlease check your credentials.")
            self.root.destroy()
            return
        
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()

        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True)

        title = tk.Label(main_frame, text="🏦 BANK MANAGEMENT SYSTEM", 
                        font=('Arial', 28, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=30)

        login_frame = tk.Frame(main_frame, bg='#34495e', padx=40, pady=30)
        login_frame.pack()
        
        tk.Label(login_frame, text="Customer Login", font=('Arial', 18, 'bold'),
                bg='#34495e', fg='white').grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(login_frame, text="Email:", font=('Arial', 12), 
                bg='#34495e', fg='white').grid(row=1, column=0, sticky='e', padx=10, pady=10)
        self.email_entry = tk.Entry(login_frame, font=('Arial', 12), width=30)
        self.email_entry.grid(row=1, column=1, pady=10)
        self.email_entry.insert(0, "rahul.sharma@email.com")  # Default for testing

        tk.Label(login_frame, text="Password:", font=('Arial', 12),
                bg='#34495e', fg='white').grid(row=2, column=0, sticky='e', padx=10, pady=10)
        self.password_entry = tk.Entry(login_frame, font=('Arial', 12), width=30, show='*')
        self.password_entry.grid(row=2, column=1, pady=10)
        self.password_entry.insert(0, "hashed_password_123")  # Default for testing

        login_btn = tk.Button(login_frame, text="LOGIN", font=('Arial', 12, 'bold'),
                            bg='#27ae60', fg='white', width=15, command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Handle login"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter email and password")
            return
        
        customer = self.db.customer_login(email, password)
        
        if customer:
            self.current_customer = customer
            messagebox.showinfo("Success", f"Welcome, {customer['full_name']}!")
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password")
    
    def show_dashboard(self):
        """Display main dashboard"""
        self.clear_window()

        top_frame = tk.Frame(self.root, bg='#34495e', height=80)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text=f"Welcome, {self.current_customer['full_name']}", 
                font=('Arial', 16, 'bold'), bg='#34495e', fg='white').pack(side='left', padx=20, pady=25)
        
        tk.Button(top_frame, text="LOGOUT", font=('Arial', 10, 'bold'),
                 bg='#e74c3c', fg='white', command=self.logout).pack(side='right', padx=20, pady=20)

        content_frame = tk.Frame(self.root, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True)

        menu_frame = tk.Frame(content_frame, bg='#2c3e50', width=200)
        menu_frame.pack(side='left', fill='y')
        menu_frame.pack_propagate(False)
        
        tk.Label(menu_frame, text="MENU", font=('Arial', 14, 'bold'),
                bg='#2c3e50', fg='white').pack(pady=20)
        
        menu_buttons = [
            ("🏠 Dashboard", self.show_account_summary),
            ("💳 My Accounts", self.show_my_accounts),
            ("💰 Deposit", self.show_deposit_screen),
            ("💸 Withdraw", self.show_withdraw_screen),
            ("🔄 Transfer", self.show_transfer_screen),
            ("📊 Transactions", self.show_transactions_screen)
        ]
        
        for text, command in menu_buttons:
            tk.Button(menu_frame, text=text, font=('Arial', 11), bg='#34495e',
                     fg='white', width=18, height=2, bd=0, 
                     command=command).pack(pady=5, padx=10)
        
        self.content_area = tk.Frame(content_frame, bg='#ecf0f1')
        self.content_area.pack(side='right', fill='both', expand=True)
        
        self.show_account_summary()
    
    def logout(self):
        """Handle logout"""
        self.current_customer = None
        self.current_accounts = []
        self.show_login_screen()
    
    def clear_content_area(self):
        """Clear content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    
    def show_account_summary(self):
        """Display account summary"""
        self.clear_content_area()
        
        tk.Label(self.content_area, text="Account Summary", font=('Arial', 20, 'bold'),
                bg='#ecf0f1').pack(pady=20)
        
        # Get summary data
        summary = self.db.get_account_summary(self.current_customer['customer_id'])
        accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
        
        # Summary cards
        cards_frame = tk.Frame(self.content_area, bg='#ecf0f1')
        cards_frame.pack(pady=20)
        
        cards = [
            ("Total Accounts", summary['total_accounts'], '#3498db'),
            ("Total Balance", f"₹{summary['total_balance']:,.2f}", '#27ae60'),
            ("Total Transactions", summary['total_transactions'], '#e67e22')
        ]
        
        for title, value, color in cards:
            card = tk.Frame(cards_frame, bg=color, width=200, height=120)
            card.pack(side='left', padx=15)
            card.pack_propagate(False)
            
            tk.Label(card, text=title, font=('Arial', 12), 
                    bg=color, fg='white').pack(pady=10)
            tk.Label(card, text=str(value), font=('Arial', 18, 'bold'),
                    bg=color, fg='white').pack(pady=10)

        tk.Label(self.content_area, text="Your Accounts", font=('Arial', 16, 'bold'),
                bg='#ecf0f1').pack(pady=20)
        
        tree_frame = tk.Frame(self.content_area, bg='#ecf0f1')
        tree_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        columns = ('Account Number', 'Type', 'Balance', 'Status')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for acc in accounts:
            tree.insert('', 'end', values=(
                acc['account_number'],
                acc['account_type'],
                f"₹{acc['balance']:,.2f}",
                acc['status']
            ))
        
        tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)

    
    def show_my_accounts(self):
        """Display detailed account information"""
        self.clear_content_area()
        
        tk.Label(self.content_area, text="My Accounts", font=('Arial', 20, 'bold'),
                bg='#ecf0f1').pack(pady=20)
        
        accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
        
        for acc in accounts:
            acc_frame = tk.Frame(self.content_area, bg='white', relief='raised', bd=2)
            acc_frame.pack(pady=10, padx=30, fill='x')

            header = tk.Frame(acc_frame, bg='#3498db')
            header.pack(fill='x')
            
            tk.Label(header, text=acc['account_type'], font=('Arial', 14, 'bold'),
                    bg='#3498db', fg='white').pack(side='left', padx=20, pady=10)
            
            tk.Label(header, text=f"₹{acc['balance']:,.2f}", font=('Arial', 16, 'bold'),
                    bg='#3498db', fg='white').pack(side='right', padx=20, pady=10)

            details = tk.Frame(acc_frame, bg='white')
            details.pack(fill='x', padx=20, pady=15)
            
            info = [
                ("Account Number:", acc['account_number']),
                ("Interest Rate:", f"{acc['interest_rate']}%"),
                ("Opened On:", acc['created_date']),
                ("Status:", acc['status'])
            ]
            
            for i, (label, value) in enumerate(info):
                row = i // 2
                col = i % 2
                
                tk.Label(details, text=label, font=('Arial', 10, 'bold'),
                        bg='white', fg='#7f8c8d').grid(row=row, column=col*2, sticky='w', padx=10, pady=5)
                tk.Label(details, text=value, font=('Arial', 10),
                        bg='white', fg='#2c3e50').grid(row=row, column=col*2+1, sticky='w', padx=10, pady=5)

    
    def show_deposit_screen(self):
        """Display deposit form"""
        self.clear_content_area()
        
        tk.Label(self.content_area, text="Deposit Money", font=('Arial', 20, 'bold'),
                bg='#ecf0f1').pack(pady=30)
        
        form_frame = tk.Frame(self.content_area, bg='white', padx=40, pady=30)
        form_frame.pack()
        
        tk.Label(form_frame, text="Select Account:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
        account_options = [f"{acc['account_number']} ({acc['account_type']})" 
                          for acc in accounts]
        
        self.deposit_account_var = tk.StringVar()
        account_menu = ttk.Combobox(form_frame, textvariable=self.deposit_account_var,
                                   values=account_options, font=('Arial', 11), width=35, state='readonly')
        account_menu.grid(row=0, column=1, pady=10, padx=10)
        if account_options:
            account_menu.current(0)
        
        tk.Label(form_frame, text="Amount:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=10)
        self.deposit_amount = tk.Entry(form_frame, font=('Arial', 12), width=35)
        self.deposit_amount.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Description:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=10)
        self.deposit_desc = tk.Entry(form_frame, font=('Arial', 12), width=35)
        self.deposit_desc.grid(row=2, column=1, pady=10, padx=10)
        self.deposit_desc.insert(0, "Cash Deposit")

        tk.Button(form_frame, text="DEPOSIT", font=('Arial', 12, 'bold'),
                 bg='#27ae60', fg='white', width=20,
                 command=self.process_deposit).grid(row=3, column=0, columnspan=2, pady=30)
    
    def process_deposit(self):
        """Process deposit transaction"""
        account_str = self.deposit_account_var.get()
        if not account_str:
            messagebox.showwarning("Error", "Please select an account")
            return
        
        account_number = account_str.split()[0]
        amount_str = self.deposit_amount.get().strip()
        description = self.deposit_desc.get().strip()
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Amount must be positive")
                return
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number")
            return
        
        if self.db.deposit_money(account_number, amount, description):
            messagebox.showinfo("Success", f"₹{amount:,.2f} deposited successfully!")
            self.deposit_amount.delete(0, 'end')
            self.show_account_summary()
        else:
            messagebox.showerror("Error", "Deposit failed!")
    
    
    def show_withdraw_screen(self):
        """Display withdrawal form"""
        self.clear_content_area()
        
        tk.Label(self.content_area, text="Withdraw Money", font=('Arial', 20, 'bold'),
                bg='#ecf0f1').pack(pady=30)
        
        form_frame = tk.Frame(self.content_area, bg='white', padx=40, pady=30)
        form_frame.pack()

        tk.Label(form_frame, text="Select Account:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
        account_options = [f"{acc['account_number']} ({acc['account_type']}) - ₹{acc['balance']:,.2f}" 
                          for acc in accounts]
        
        self.withdraw_account_var = tk.StringVar()
        account_menu = ttk.Combobox(form_frame, textvariable=self.withdraw_account_var,
                                   values=account_options, font=('Arial', 11), width=45, state='readonly')
        account_menu.grid(row=0, column=1, pady=10, padx=10)
        if account_options:
            account_menu.current(0)

        tk.Label(form_frame, text="Amount:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=10)
        self.withdraw_amount = tk.Entry(form_frame, font=('Arial', 12), width=45)
        self.withdraw_amount.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(form_frame, text="Description:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=10)
        self.withdraw_desc = tk.Entry(form_frame, font=('Arial', 12), width=45)
        self.withdraw_desc.grid(row=2, column=1, pady=10, padx=10)
        self.withdraw_desc.insert(0, "Cash Withdrawal")

        tk.Button(form_frame, text="WITHDRAW", font=('Arial', 12, 'bold'),
                 bg='#e74c3c', fg='white', width=20,
                 command=self.process_withdrawal).grid(row=3, column=0, columnspan=2, pady=30)
    
    def process_withdrawal(self):
        """Process withdrawal transaction"""
        account_str = self.withdraw_account_var.get()
        if not account_str:
            messagebox.showwarning("Error", "Please select an account")
            return
        
        account_number = account_str.split()[0]
        amount_str = self.withdraw_amount.get().strip()
        description = self.withdraw_desc.get().strip()
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Amount must be positive")
                return
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number")
            return
        
        if self.db.withdraw_money(account_number, amount, description):
            messagebox.showinfo("Success", f"₹{amount:,.2f} withdrawn successfully!")
            self.withdraw_amount.delete(0, 'end')
            self.show_account_summary()
        else:
            messagebox.showerror("Error", "Withdrawal failed! Check balance.")
        
    def show_transfer_screen(self):
        """Display transfer form - DEMONSTRATES ACID PROPERTIES"""
        self.clear_content_area()
        
        tk.Label(self.content_area, text="Transfer Money", font=('Arial', 20, 'bold'),
                bg='#ecf0f1').pack(pady=30)

        info_frame = tk.Frame(self.content_area, bg='#f39c12', padx=15, pady=10)
        info_frame.pack(fill='x', padx=50, pady=10)
        
        tk.Label(info_frame, text="🔒 ACID Properties: Both accounts updated atomically or transaction fails completely",
                font=('Arial', 10, 'bold'), bg='#f39c12', fg='white').pack()
        
        form_frame = tk.Frame(self.content_area, bg='white', padx=40, pady=30)
        form_frame.pack()

        tk.Label(form_frame, text="From Account:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
        account_options = [f"{acc['account_number']} - ₹{acc['balance']:,.2f}" 
                          for acc in accounts]
        
        self.transfer_from_var = tk.StringVar()
        from_menu = ttk.Combobox(form_frame, textvariable=self.transfer_from_var,
                                values=account_options, font=('Arial', 11), width=40, state='readonly')
        from_menu.grid(row=0, column=1, pady=10, padx=10)
        if account_options:
            from_menu.current(0)

        tk.Label(form_frame, text="To Account Number:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=1, column=0, sticky='w', pady=10)
        self.transfer_to = tk.Entry(form_frame, font=('Arial', 12), width=40)
        self.transfer_to.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(form_frame, text="Amount:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=10)
        self.transfer_amount = tk.Entry(form_frame, font=('Arial', 12), width=40)
        self.transfer_amount.grid(row=2, column=1, pady=10, padx=10)

        tk.Button(form_frame, text="TRANSFER MONEY", font=('Arial', 12, 'bold'),
                 bg='#9b59b6', fg='white', width=20,
                 command=self.process_transfer).grid(row=3, column=0, columnspan=2, pady=30)
    def create_stat_card(self, parent_frame, title, value, unit="", color='#3498db'):
        """Creates a stylized card to display a single statistic."""
        card_frame = tk.Frame(parent_frame, bg=color, bd=0, relief='flat', padx=20, pady=15)
        card_frame.pack(side='left', padx=10, pady=10, fill='x', expand=True)

        # Title Label
        tk.Label(card_frame, text=title, font=('Arial', 14), bg=color, fg='white').pack(anchor='center')
        
        # Value Label
        if unit == '₹':
            # Format currency with commas and two decimal places
            value_text = f"{unit}{value:,.2f}"
        else:
            # Format integer with commas
            value_text = f"{value:,}"
            
        tk.Label(card_frame, text=value_text, font=('Arial', 24, 'bold'), bg=color, fg='white').pack(anchor='center')
        
    def show_admin_dashboard(self):
        """Display the main system dashboard for admin view with aggregate statistics."""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Title
        tk.Label(main_frame, text="System-Wide Dashboard", font=('Arial', 24, 'bold'), 
                 bg='#2c3e50', fg='white').pack(pady=(0, 20))
        
        # Fetch Bank-Wide Statistics
        stats = self.db.get_bank_stats()
        
        stats_frame = tk.Frame(main_frame, bg='#2c3e50')
        stats_frame.pack(fill='x', pady=20)

        if stats:
            # Display Statistics in Cards
            self.create_stat_card(
                stats_frame, 
                "Total Active Accounts", 
                stats.get('total_active_accounts', 0), 
                color='#2ecc71' # Green
            )
            self.create_stat_card(
                stats_frame, 
                "Total Balance", 
                stats.get('total_balance', 0), 
                unit='₹',
                color='#3498db' # Blue
            )
            self.create_stat_card(
                stats_frame, 
                "Total Transactions", 
                stats.get('total_transactions', 0), 
                color='#f39c12' # Yellow/Orange
            )
        else:
            tk.Label(main_frame, text="Could not load bank statistics. Check database connection.", 
                     font=('Arial', 14), bg='#2c3e50', fg='red').pack(pady=20)

        # Log Out Button
        tk.Button(main_frame, text="Log Out", command=self.show_login_screen,
                  bg='#e74c3c', fg='white', font=('Arial', 12, 'bold')).pack(anchor='se', pady=10)
    def create_stat_card(self, parent_frame, title, value, unit="", color='#3498db'):
        """Creates a stylized card to display a single statistic."""
        card_frame = tk.Frame(parent_frame, bg=color, bd=0, relief='flat', padx=20, pady=15)
        card_frame.pack(side='left', padx=10, pady=10, fill='x', expand=True)

        # Title Label
        tk.Label(card_frame, text=title, font=('Arial', 14), bg=color, fg='white').pack(anchor='center')
        
        # Value Label
        if unit == '₹':
            # Format currency with commas and two decimal places
            value_text = f"{unit}{value:,.2f}"
        else:
            # Format integer with commas
            value_text = f"{value:,}"
            
        tk.Label(card_frame, text=value_text, font=('Arial', 24, 'bold'), bg=color, fg='white').pack(anchor='center')
        
    def show_admin_dashboard(self):
        """Display the main system dashboard for admin view with aggregate statistics."""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Title
        tk.Label(main_frame, text="System-Wide Dashboard", font=('Arial', 24, 'bold'), 
                 bg='#2c3e50', fg='white').pack(pady=(0, 20))
        
        # Fetch Bank-Wide Statistics
        stats = self.db.get_bank_stats()
        
        stats_frame = tk.Frame(main_frame, bg='#2c3e50')
        stats_frame.pack(fill='x', pady=20)

        if stats:
            # Display Statistics in Cards
            self.create_stat_card(
                stats_frame, 
                "Total Active Accounts", 
                stats.get('total_active_accounts', 0), 
                color='#2ecc71' # Green
            )
            self.create_stat_card(
                stats_frame, 
                "Total Balance", 
                stats.get('total_balance', 0), 
                unit='₹',
                color='#3498db' # Blue
            )
            self.create_stat_card(
                stats_frame, 
                "Total Transactions", 
                stats.get('total_transactions', 0), 
                color='#f39c12' # Yellow/Orange
            )
        else:
            tk.Label(main_frame, text="Could not load bank statistics. Check database connection.", 
                     font=('Arial', 14), bg='#2c3e50', fg='red').pack(pady=20)

        # Log Out Button
        tk.Button(main_frame, text="Log Out", command=self.show_login_screen,
                  bg='#e74c3c', fg='white', font=('Arial', 12, 'bold')).pack(anchor='se', pady=10)
    def customer_login_attempt(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        customer_info = self.db.customer_login(email, password)
        
        if customer_info:
            self.current_customer = customer_info
            
            # --- START NEW LOGIC FOR ADMIN DASHBOARD ---
            # Assuming you use a specific email (or a flag in the DB) to identify the Admin
            if email.upper() == "SYS_ADMIN@BANK.COM": # Example Admin Email
                self.show_admin_dashboard()
            # --- END NEW LOGIC FOR ADMIN DASHBOARD ---
            
            else:
                self.current_accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
                self.show_customer_dashboard() # Existing customer dashboard
        else:
            messagebox.showerror("Login Failed", "Invalid email or password, or account is inactive.")
                
    def process_transfer(self):
        """Process money transfer - DEMONSTRATES ACID!"""
        from_account_str = self.transfer_from_var.get()
        if not from_account_str:
            messagebox.showwarning("Error", "Please select source account")
            return
        
        from_account = from_account_str.split()[0]
        to_account = self.transfer_to.get().strip()
        amount_str = self.transfer_amount.get().strip()
        
        if not to_account:
            messagebox.showwarning("Error", "Please enter destination account number")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Amount must be positive")
                return
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number")
            return
        
        confirm = messagebox.askyesno("Confirm Transfer",
                                     f"Transfer ₹{amount:,.2f}\nFrom: {from_account}\nTo: {to_account}\n\nProceed?")
        
        if not confirm:
            return
        
        if self.db.transfer_money(from_account, to_account, amount):
            messagebox.showinfo("Success", 
                              f"₹{amount:,.2f} transferred successfully!\n\n" +
                              "ACID Properties Demonstrated:\n" +
                              "✓ Atomicity: Both accounts updated together\n" +
                              "✓ Consistency: Total money remains same\n" +
                              "✓ Isolation: No interference from other transactions\n" +
                              "✓ Durability: Changes are permanent")
            self.transfer_amount.delete(0, 'end')
            self.transfer_to.delete(0, 'end')
            self.show_account_summary()
        else:
            messagebox.showerror("Transfer Failed", 
                               "Transaction failed!\nBoth accounts remain unchanged (Rollback)")

    
    def show_transactions_screen(self):
        """Display transaction history"""
        self.clear_content_area()
        
        tk.Label(self.content_area, text="Transaction History", font=('Arial', 20, 'bold'),
                bg='#ecf0f1').pack(pady=20)
        
        select_frame = tk.Frame(self.content_area, bg='#ecf0f1')
        select_frame.pack(pady=10)
        
        tk.Label(select_frame, text="Select Account:", font=('Arial', 12, 'bold'),
                bg='#ecf0f1').pack(side='left', padx=10)
        
        accounts = self.db.get_customer_accounts(self.current_customer['customer_id'])
        account_options = [f"{acc['account_number']} ({acc['account_type']})" 
                          for acc in accounts]
        
        self.trans_account_var = tk.StringVar()
        account_menu = ttk.Combobox(select_frame, textvariable=self.trans_account_var,
                                   values=account_options, font=('Arial', 11), width=35, state='readonly')
        account_menu.pack(side='left', padx=10)
        if account_options:
            account_menu.current(0)
        
        tk.Button(select_frame, text="Load Transactions", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', command=self.load_transactions).pack(side='left', padx=10)
        
        tree_frame = tk.Frame(self.content_area, bg='white')
        tree_frame.pack(pady=20, padx=30, fill='both', expand=True)
        
        columns = ('Date', 'Type', 'Amount', 'Balance After', 'Description')
        self.trans_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        widths = [150, 120, 120, 120, 250]
        for col, width in zip(columns, widths):
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=width)
        
        self.trans_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.trans_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.trans_tree.configure(yscrollcommand=scrollbar.set)

        if account_options:
            self.load_transactions()
    
    def load_transactions(self):
        """Load transactions for selected account"""
        account_str = self.trans_account_var.get()
        if not account_str:
            return
        
        account_number = account_str.split()[0]

        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        transactions = self.db.get_transaction_history(account_number, limit=100)
        
        for trans in transactions:
            self.trans_tree.insert('', 'end', values=(
                trans['date'],
                trans['type'],
                f"₹{trans['amount']:,.2f}",
                f"₹{trans['balance_after']:,.2f}",
                trans['description']
            ))


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = BankManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()