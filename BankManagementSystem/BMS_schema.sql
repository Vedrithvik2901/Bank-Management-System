CREATE TABLE Customers(
    customer_id NUMBER(10) PRIMARY KEY,
    full_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    phone VARCHAR2(15) NOT NULL,
    address VARCHAR2(200),
    date_of_birth DATE,
    created_date DATE DEFAULT SYSDATE,
    password_hash VARCHAR2(100) NOT NULL,
    status VARCHAR2(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

CREATE TABLE Accounts (
    account_id NUMBER(10) PRIMARY KEY,
    customer_id NUMBER(10) NOT NULL,
    account_number VARCHAR2(20) UNIQUE NOT NULL,
    account_type VARCHAR2(20) NOT NULL CHECK (account_type IN ('Savings', 'Current', 'Fixed Deposit')),
    balance NUMBER(15,2) DEFAULT 0 CHECK (balance >= 0),
    interest_rate NUMBER(5,2) DEFAULT 0,
    created_date DATE DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Closed', 'Frozen')),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE Transactions (
    transaction_id NUMBER(15) PRIMARY KEY,
    account_id NUMBER(10) NOT NULL,
    transaction_type VARCHAR2(20) NOT NULL CHECK (transaction_type IN ('Deposit', 'Withdrawal', 'Transfer-In', 'Transfer-Out', 'Interest')),
    amount NUMBER(15,2) NOT NULL CHECK (amount > 0),
    balance_after NUMBER(15,2) NOT NULL,
    transaction_date DATE DEFAULT SYSDATE,
    description VARCHAR2(200),
    reference_account VARCHAR2(20), -- For transfers
    CONSTRAINT fk_account FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
);

CREATE SEQUENCE customer_seq START WITH 1001 INCREMENT BY 1;
CREATE SEQUENCE account_seq START WITH 100001 INCREMENT BY 1;
CREATE SEQUENCE transaction_seq START WITH 1 INCREMENT BY 1;

CREATE INDEX idx_account_number ON Accounts(account_number);

CREATE INDEX idx_customer_email ON Customers(email);

CREATE INDEX idx_transaction_account ON Transactions(account_id);

CREATE INDEX idx_transaction_date ON Transactions(transaction_date);

CREATE INDEX idx_account_customer ON Accounts(customer_id, status);

INSERT INTO Customers VALUES (
    customer_seq.NEXTVAL, 'Rahul Sharma', 'rahul.sharma@email.com', 
    '9876543210', 'Mumbai, Maharashtra', 
    TO_DATE('1995-05-15', 'YYYY-MM-DD'), SYSDATE,
    'hashed_password_123', 'Active'
);

INSERT INTO Customers VALUES (
    customer_seq.NEXTVAL, 'Priya Patel', 'priya.patel@email.com', 
    '9876543211', 'Delhi, India', 
    TO_DATE('1998-08-22', 'YYYY-MM-DD'), SYSDATE,
    'hashed_password_456', 'Active'
);

INSERT INTO Customers VALUES (
    customer_seq.NEXTVAL, 'Amit Kumar', 'amit.kumar@email.com', 
    '9876543212', 'Bangalore, Karnataka', 
    TO_DATE('1990-12-10', 'YYYY-MM-DD'), SYSDATE,
    'hashed_password_789', 'Active'
);

INSERT INTO Customers VALUES (
    customer_seq.NEXTVAL, 'Sneha Reddy', 'sneha.reddy@email.com', 
    '9876543213', 'Hyderabad, Telangana', 
    TO_DATE('1993-03-25', 'YYYY-MM-DD'), SYSDATE,
    'hashed_password_012', 'Active'
);

INSERT INTO Customers VALUES (
    customer_seq.NEXTVAL, 'Vikram Singh', 'vikram.singh@email.com', 
    '9876543214', 'Pune, Maharashtra', 
    TO_DATE('1997-07-18', 'YYYY-MM-DD'), SYSDATE,
    'hashed_password_345', 'Active'
);

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1001,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Savings',50000.00,4.00,SYSDATE - 365,'Active');

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1001,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Current',120000.00,0.00,SYSDATE - 200,'Active');

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1002,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Savings',75000.00,4.00,SYSDATE - 180,'Active');

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1003,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Savings',30000.00,4.00,SYSDATE - 90,'Active');

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1004,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Savings',95000.00,4.00,SYSDATE - 120,'Active');

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1004,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Fixed Deposit',200000.00,6.50,SYSDATE - 60,'Active');

INSERT INTO Accounts VALUES (account_seq.NEXTVAL,1005,'ACC' || LPAD(account_seq.CURRVAL, 10, '0'),'Current',45000.00,0.00,SYSDATE - 30,'Active');

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100001,'Deposit',10000.00,50000.00,SYSDATE - 10,'ATM Deposit',NULL);

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100001,'Withdrawal',5000.00,45000.00,SYSDATE - 8,'ATM Withdrawal',NULL);

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100001,'Transfer-Out',15000.00,30000.00,SYSDATE - 5,'Transfer to Priya','ACC0000100003');

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100003,'Transfer-In',15000.00,75000.00,SYSDATE - 5,'Transfer from Rahul','ACC0000100001');

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100003,'Withdrawal',8000.00,67000.00,SYSDATE - 3,'Online Purchase',NULL);

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100004,'Deposit',20000.00,30000.00,SYSDATE - 7,'Salary Credit',NULL);

INSERT INTO Transactions VALUES (transaction_seq.NEXTVAL,100004,'Withdrawal',5000.00,25000.00,SYSDATE - 2,'ATM Withdrawal',NULL);

CREATE OR REPLACE PROCEDURE open_account(
    p_customer_id IN NUMBER,
    p_account_type IN VARCHAR2,
    p_initial_deposit IN NUMBER,
    p_account_number OUT VARCHAR2
) AS
    v_account_id NUMBER;
    v_interest_rate NUMBER := 0;
BEGIN

    IF p_account_type = 'Savings' THEN
        v_interest_rate := 4.00;
    ELSIF p_account_type = 'Fixed Deposit' THEN
        v_interest_rate := 6.50;
    END IF;
    
    SELECT account_seq.NEXTVAL INTO v_account_id FROM dual;
    
    p_account_number := 'ACC' || LPAD(v_account_id, 10, '0');
    
    INSERT INTO Accounts VALUES (
        v_account_id,
        p_customer_id,
        p_account_number,
        p_account_type,
        p_initial_deposit,
        v_interest_rate,
        SYSDATE,
        'Active'
    );
    
    IF p_initial_deposit > 0 THEN
        INSERT INTO Transactions VALUES (
            transaction_seq.NEXTVAL,
            v_account_id,
            'Deposit',
            p_initial_deposit,
            p_initial_deposit,
            SYSDATE,
            'Account Opening Deposit',
            NULL
        );
    END IF;
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Account created: ' || p_account_number);
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;

CREATE OR REPLACE PROCEDURE deposit_money(
    p_account_number IN VARCHAR2,
    p_amount IN NUMBER,
    p_description IN VARCHAR2 DEFAULT 'Cash Deposit'
) AS
    v_account_id NUMBER;
    v_new_balance NUMBER;
BEGIN

    SELECT account_id, balance INTO v_account_id, v_new_balance
    FROM Accounts
    WHERE account_number = p_account_number AND status = 'Active';

    v_new_balance := v_new_balance + p_amount;

    UPDATE Accounts
    SET balance = v_new_balance
    WHERE account_id = v_account_id;

    INSERT INTO Transactions VALUES (
        transaction_seq.NEXTVAL,
        v_account_id,
        'Deposit',
        p_amount,
        v_new_balance,
        SYSDATE,
        p_description,
        NULL
    );
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Deposit successful. New balance: ' || v_new_balance);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Account not found or inactive');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
        ROLLBACK;
END;
/

CREATE OR REPLACE PROCEDURE withdraw_money(
    p_account_number IN VARCHAR2,
    p_amount IN NUMBER,
    p_description IN VARCHAR2 DEFAULT 'Cash Withdrawal'
) AS
    v_account_id NUMBER;
    v_current_balance NUMBER;
    v_new_balance NUMBER;
BEGIN

    SELECT account_id, balance INTO v_account_id, v_current_balance
    FROM Accounts
    WHERE account_number = p_account_number AND status = 'Active';

    IF v_current_balance < p_amount THEN
        RAISE_APPLICATION_ERROR(-20001, 'Insufficient balance');
    END IF;
    
    v_new_balance := v_current_balance - p_amount;

    UPDATE Accounts
    SET balance = v_new_balance
    WHERE account_id = v_account_id;

    INSERT INTO Transactions VALUES (
        transaction_seq.NEXTVAL,
        v_account_id,
        'Withdrawal',
        p_amount,
        v_new_balance,
        SYSDATE,
        p_description,
        NULL
    );
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Withdrawal successful. New balance: ' || v_new_balance);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Account not found or inactive');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
        ROLLBACK;
END;
/

CREATE OR REPLACE PROCEDURE transfer_money(
    p_from_account IN VARCHAR2,
    p_to_account IN VARCHAR2,
    p_amount IN NUMBER
) AS
    v_from_id NUMBER;
    v_to_id NUMBER;
    v_from_balance NUMBER;
    v_to_balance NUMBER;
    v_from_new_balance NUMBER;
    v_to_new_balance NUMBER;
BEGIN

    SELECT account_id, balance INTO v_from_id, v_from_balance
    FROM Accounts
    WHERE account_number = p_from_account AND status = 'Active';
 
    SELECT account_id, balance INTO v_to_id, v_to_balance
    FROM Accounts
    WHERE account_number = p_to_account AND status = 'Active';

    IF v_from_balance < p_amount THEN
        RAISE_APPLICATION_ERROR(-20001, 'Insufficient balance for transfer');
    END IF;

    v_from_new_balance := v_from_balance - p_amount;
    v_to_new_balance := v_to_balance + p_amount;

    UPDATE Accounts
    SET balance = v_from_new_balance
    WHERE account_id = v_from_id;

    UPDATE Accounts
    SET balance = v_to_new_balance
    WHERE account_id = v_to_id;

    INSERT INTO Transactions VALUES (
        transaction_seq.NEXTVAL,
        v_from_id,
        'Transfer-Out',
        p_amount,
        v_from_new_balance,
        SYSDATE,
        'Transfer to ' || p_to_account,
        p_to_account
    );

    INSERT INTO Transactions VALUES (
        transaction_seq.NEXTVAL,
        v_to_id,
        'Transfer-In',
        p_amount,
        v_to_new_balance,
        SYSDATE,
        'Transfer from ' || p_from_account,
        p_from_account
    );
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Transfer successful!');
    DBMS_OUTPUT.PUT_LINE('From account new balance: ' || v_from_new_balance);
    DBMS_OUTPUT.PUT_LINE('To account new balance: ' || v_to_new_balance);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('One or both accounts not found');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Transfer failed: ' || SQLERRM);
        ROLLBACK;
END;
/

CREATE OR REPLACE VIEW customer_account_summary AS
SELECT 
    c.customer_id,
    c.full_name,
    c.email,
    a.account_number,
    a.account_type,
    a.balance,
    a.status,
    (SELECT COUNT(*) FROM Transactions t WHERE t.account_id = a.account_id) as total_transactions
FROM Customers c
JOIN Accounts a ON c.customer_id = a.customer_id
WHERE c.status = 'Active';

CREATE OR REPLACE VIEW recent_transactions AS
SELECT 
    c.full_name,
    a.account_number,
    t.transaction_type,
    t.amount,
    t.balance_after,
    TO_CHAR(t.transaction_date, 'DD-MON-YYYY HH24:MI:SS') as transaction_time,
    t.description
FROM Transactions t
JOIN Accounts a ON t.account_id = a.account_id
JOIN Customers c ON a.customer_id = c.customer_id
WHERE t.transaction_date >= SYSDATE - 30
ORDER BY t.transaction_date DESC;

CREATE OR REPLACE VIEW account_statistics AS
SELECT 
    account_type,
    COUNT(*) as total_accounts,
    SUM(balance) as total_balance,
    AVG(balance) as average_balance,
    MAX(balance) as highest_balance,
    MIN(balance) as lowest_balance
FROM Accounts
WHERE status = 'Active'
GROUP BY account_type;

SELECT 'Customers' as Table_Name, COUNT(*) as Count FROM Customers
UNION ALL
SELECT 'Accounts', COUNT(*) FROM Accounts
UNION ALL
SELECT 'Transactions', COUNT(*) FROM Transactions;

SELECT * FROM customer_account_summary;

SELECT * FROM account_statistics;

SELECT  * from recent_transactions;

SELECT * from Accounts;