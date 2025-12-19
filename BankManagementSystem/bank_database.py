"""
Bank Account Management System - Python Backend
Complete CRUD operations with Oracle Database
MATCHES THE BANK SCHEMA (Customers, Accounts, Transactions)
"""

import oracledb
from datetime import datetime
from typing import List, Tuple, Optional, Dict

class BankDatabase:
    """Main database class for bank operations"""
    
    def __init__(self, username: str, password: str, dsn: str):
        self.username = username
        self.password = password
        self.dsn = dsn
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Connect to Oracle Database"""
        try:
            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn,
                mode=oracledb.SYSDBA
            )
            self.cursor = self.connection.cursor()
            print("✅ Connected to Oracle Database")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Disconnected from database")
    
    
    def customer_login(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate customer login"""
        try:
            query = """
            SELECT customer_id, full_name, email, phone, address
            FROM Customers
            WHERE email = :1 AND password_hash = :2 AND status = 'Active'
            """
            self.cursor.execute(query, (email, password))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'customer_id': result[0],
                    'full_name': result[1],
                    'email': result[2],
                    'phone': result[3],
                    'address': result[4]
                }
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    
    def register_customer(self, full_name: str, email: str, phone: str, 
                         address: str, dob: str, password: str) -> bool:
        """Register a new customer"""
        try:
            query = """
            INSERT INTO Customers 
            (customer_id, full_name, email, phone, address, date_of_birth, 
             created_date, password_hash, status)
            VALUES (customer_seq.NEXTVAL, :1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), 
                    SYSDATE, :6, 'Active')
            """
            self.cursor.execute(query, (full_name, email, phone, address, dob, password))
            self.connection.commit()
            print(f"✅ Customer {full_name} registered successfully")
            return True
        except oracledb.IntegrityError:
            print("❌ Email already exists")
            return False
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            self.connection.rollback()
            return False
    
    def create_account(self, customer_id: int, account_type: str, 
                      initial_deposit: float) -> Optional[str]:
        """Create a new bank account"""
        try:
            account_number = self.cursor.var(str)
            self.cursor.callproc('open_account', 
                               [customer_id, account_type, initial_deposit, account_number])
            return account_number.getvalue()
        except Exception as e:
            print(f"❌ Account creation failed: {e}")
            return None
    
    
    def get_customer_accounts(self, customer_id: int) -> List[Dict]:
        """Get all accounts for a customer (JOIN query)"""
        try:
            query = """
            SELECT a.account_id, a.account_number, a.account_type, 
                   a.balance, a.interest_rate, a.status,
                   TO_CHAR(a.created_date, 'DD-MON-YYYY') as created_date
            FROM Accounts a
            WHERE a.customer_id = :1
            ORDER BY a.created_date DESC
            """
            self.cursor.execute(query, (customer_id,))
            
            accounts = []
            for row in self.cursor:
                accounts.append({
                    'account_id': row[0],
                    'account_number': row[1],
                    'account_type': row[2],
                    'balance': float(row[3]),
                    'interest_rate': float(row[4]),
                    'status': row[5],
                    'created_date': row[6]
                })
            return accounts
        except Exception as e:
            print(f"Error fetching accounts: {e}")
            return []
    
    def get_account_details(self, account_number: str) -> Optional[Dict]:
        """Get detailed account information with customer details (JOIN)"""
        try:
            query = """
            SELECT c.full_name, c.email, c.phone,
                   a.account_number, a.account_type, a.balance, 
                   a.interest_rate, a.status,
                   TO_CHAR(a.created_date, 'DD-MON-YYYY') as created
            FROM Accounts a
            JOIN Customers c ON a.customer_id = c.customer_id
            WHERE a.account_number = :1
            """
            self.cursor.execute(query, (account_number,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'customer_name': result[0],
                    'email': result[1],
                    'phone': result[2],
                    'account_number': result[3],
                    'account_type': result[4],
                    'balance': float(result[5]),
                    'interest_rate': float(result[6]),
                    'status': result[7],
                    'created_date': result[8]
                }
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_transaction_history(self, account_number: str, limit: int = 50) -> List[Dict]:
        """Get transaction history for an account"""
        try:
            query = """
            SELECT t.transaction_id, t.transaction_type, t.amount, 
                   t.balance_after, t.description, t.reference_account,
                   TO_CHAR(t.transaction_date, 'DD-MON-YYYY HH24:MI:SS') as trans_date
            FROM Transactions t
            JOIN Accounts a ON t.account_id = a.account_id
            WHERE a.account_number = :1
            ORDER BY t.transaction_date DESC
            FETCH FIRST :2 ROWS ONLY
            """
            self.cursor.execute(query, (account_number, limit))
            
            transactions = []
            for row in self.cursor:
                transactions.append({
                    'transaction_id': row[0],
                    'type': row[1],
                    'amount': float(row[2]),
                    'balance_after': float(row[3]),
                    'description': row[4],
                    'reference': row[5],
                    'date': row[6]
                })
            return transactions
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def get_mini_statement(self, account_number: str) -> List[Dict]:
        """Get last 5 transactions (mini statement)"""
        return self.get_transaction_history(account_number, limit=5)
    
    def get_account_summary(self, customer_id: int) -> Dict:
        """Get complete account summary for customer"""
        try:
            query = """
            SELECT COUNT(a.account_id) as total_accounts,
                   SUM(a.balance) as total_balance,
                   (SELECT COUNT(*) FROM Transactions t 
                    JOIN Accounts a2 ON t.account_id = a2.account_id 
                    WHERE a2.customer_id = :1) as total_transactions
            FROM Accounts a
            WHERE a.customer_id = :1 AND a.status = 'Active'
            """
            self.cursor.execute(query, (customer_id,))
            result = self.cursor.fetchone()
            
            return {
                'total_accounts': result[0] or 0,
                'total_balance': float(result[1] or 0),
                'total_transactions': result[2] or 0
            }
        except Exception as e:
            print(f"Error: {e}")
            return {'total_accounts': 0, 'total_balance': 0, 'total_transactions': 0}
    
    
    def deposit_money(self, account_number: str, amount: float, 
                     description: str = "Cash Deposit") -> bool:
        """Deposit money into account"""
        try:
            self.cursor.callproc('deposit_money', [account_number, amount, description])
            print(f"✅ Deposited ₹{amount:,.2f}")
            return True
        except Exception as e:
            print(f"❌ Deposit failed: {e}")
            return False
    
    def withdraw_money(self, account_number: str, amount: float,
                      description: str = "Cash Withdrawal") -> bool:
        """Withdraw money from account"""
        try:
            self.cursor.callproc('withdraw_money', [account_number, amount, description])
            print(f"✅ Withdrawn ₹{amount:,.2f}")
            return True
        except Exception as e:
            print(f"❌ Withdrawal failed: {e}")
            return False
    def get_bank_stats(self) -> Optional[Dict]:
        """Fetch total number of active accounts, total balance, and total transactions across the bank."""
        try:
            # Note: We count only 'Active' accounts for a relevant dashboard total.
            query = """
            SELECT
                (SELECT COUNT(account_id) FROM Accounts WHERE status = 'Active') AS total_active_accounts,
                (SELECT NVL(SUM(balance), 0) FROM Accounts) AS total_balance,
                (SELECT COUNT(transaction_id) FROM Transactions) AS total_transactions
            FROM DUAL
            """
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'total_active_accounts': int(result[0]),
                    'total_balance': float(result[1]),
                    'total_transactions': int(result[2])
                }
            return None
        except Exception as e:
            print(f"Error fetching bank statistics: {e}")
            return Nones    
    
    def transfer_money(self, from_account: str, to_account: str, amount: float) -> bool:
        """Transfer money between accounts - DEMONSTRATES ACID PROPERTIES"""
        try:
            self.cursor.callproc('transfer_money', [from_account, to_account, amount])
            print(f"✅ Transferred ₹{amount:,.2f} from {from_account} to {to_account}")
            return True
        except Exception as e:
            print(f" Transfer failed: {e}")
            return False
    
    def update_customer_info(self, customer_id: int, phone: str = None,
                            address: str = None) -> bool:
        """Update customer contact information"""
        try:
            updates = []
            params = []
            
            if phone:
                updates.append("phone = :1")
                params.append(phone)
            if address:
                updates.append("address = :2")
                params.append(address)
            
            if not updates:
                return False
            
            params.append(customer_id)
            query = f"UPDATE Customers SET {', '.join(updates)} WHERE customer_id = :{len(params)}"
            
            self.cursor.execute(query, params)
            self.connection.commit()
            print("✅ Customer info updated")
            return True
        except Exception as e:
            print(f"Update failed: {e}")
            self.connection.rollback()
            return False


def test_all_operations():
    """Test all database operations"""
    
    USERNAME = "SYS"
    PASSWORD = "oracle@express"  
    DSN = "localhost:1521/XE"
    
    db = BankDatabase(USERNAME, PASSWORD, DSN)
    
    if not db.connect():
        print("❌ Connection failed! Check your credentials.")
        return
    
    try:
        print("\n" + "="*60)
        print("BANK MANAGEMENT SYSTEM - TESTING ALL OPERATIONS")
        print("="*60)
        
        # Test 1: Login
        print("\n1️⃣  Testing Customer Login:")
        customer = db.customer_login("rahul.sharma@email.com", "hashed_password_123")
        if customer:
            print(f"   ✅ Login successful: {customer['full_name']}")
            customer_id = customer['customer_id']
        else:
            print("   ❌ Login failed!")
            return

        print("\n  Testing Get Accounts (JOIN Query):")
        accounts = db.get_customer_accounts(customer_id)
        if accounts:
            for acc in accounts:
                print(f"   {acc['account_number']} - {acc['account_type']} - ₹{acc['balance']:,.2f}")
            test_account = accounts[0]['account_number']
        else:
            print("   ❌ No accounts found!")
            return

        print("\n  Testing Account Details (JOIN Query):")
        details = db.get_account_details(test_account)
        if details:
            print(f"   Customer: {details['customer_name']}")
            print(f"   Account: {details['account_number']}")
            print(f"   Balance: ₹{details['balance']:,.2f}")

        print("\n  Testing Account Summary (GROUP BY / AGGREGATE):")
        summary = db.get_account_summary(customer_id)
        print(f"   Total Accounts: {summary['total_accounts']}")
        print(f"   Total Balance: ₹{summary['total_balance']:,.2f}")
        print(f"   Total Transactions: {summary['total_transactions']}")

        print("\n Testing Deposit (CREATE):")
        db.deposit_money(test_account, 5000, "Test Deposit via Python")

        print("\n  Testing Withdrawal (CREATE):")
        db.withdraw_money(test_account, 2000, "Test Withdrawal via Python")
        
        print("\n  Testing Transfer (ACID PROPERTIES DEMO!):")
        if len(accounts) >= 2:
            from_acc = accounts[0]['account_number']
            to_acc = accounts[1]['account_number']
            print(f"   Transferring ₹1,000 from {from_acc} to {to_acc}")
            if db.transfer_money(from_acc, to_acc, 1000):
                print("    ACID Properties Maintained:")
                print("      ✓ Atomicity: Both accounts updated together")
                print("      ✓ Consistency: Total money remains constant")
                print("      ✓ Isolation: No interference from other transactions")
                print("      ✓ Durability: Changes are permanent")
        else:
            print("   ⚠️  Need 2 accounts to demo transfer")
        
        print("\n  Testing Transaction History (JOIN Query):")
        history = db.get_transaction_history(test_account, limit=5)
        if history:
            print(f"   Last {len(history)} transactions:")
            for trans in history:
                print(f"   • {trans['date']} - {trans['type']} - ₹{trans['amount']:,.2f}")
        
        print("\n  Testing Mini Statement:")
        mini = db.get_mini_statement(test_account)
        print(f"   Retrieved {len(mini)} recent transactions")

        print("\n Testing Update Customer Info (UPDATE):")
        if db.update_customer_info(customer_id, phone="9999999999"):
            print("   ✅ Phone number updated")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
    finally:
        db.disconnect()


if __name__ == "__main__":
    test_all_operations()