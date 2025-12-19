# Bank Account Management System – Oracle Database

This project implements a complete **Bank Account Management System** using **Oracle Database (21c XE)** and **PL/SQL**.

It demonstrates enterprise-level database design concepts including:
- Normalized schema design
- Referential integrity using foreign keys
- Sequence-based primary key generation
- Stored procedures and transaction control
- ACID-compliant fund transfers
- Indexing for performance optimization
- Views for reporting and analytics

---

## 🔧 Technologies Used
- Oracle Database 21c Express Edition
- Oracle SQL Developer / SQL*Plus
- PL/SQL
- SQL (DDL, DML)

---

## 🗂 Database Components

### Tables
- Customers
- Accounts
- Transactions

### Other Objects
- Sequences for auto-generated IDs
- Indexes for performance optimization
- Stored procedures for business logic
- Views for summaries and analytics

---

## ▶️ How to Run

1. Install **Oracle Database 21c XE**
2. Open **Oracle SQL Developer**
3. Connect to your database
4. Run the script:
   ```sql
   @BMS_schema.sql
