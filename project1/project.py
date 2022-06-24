from datetime import datetime
import mysql
import mysql.connector

# Create Database Connection
mydb = mysql.connector.connect(host="localhost", user="root",
           password="1234", database="BankDb", auth_plugin='mysql_native_password')


# Function to get the number of rows in the Account table to generate next Id
def getNumRows(): 
    sql = "select count(*) as cnt from tblAccount"
    cursor = mydb.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()

    if result is not None:
        return result[0] + 1
    else: 
        return 1

# Function to create new Account Number 
def nextAccountNumber():
    rowCount = getNumRows() + 1000
    return "AC-" + str(rowCount)

# Function to Register a New Customer and assign a new Account 
def createAccount():
    # Get Customer Data
    firstName = input("Please enter your First Name: ")
    lastName = input("Please enter your Last Name: ")
    street = input("Please enter your Street Address: ")
    city = input("Please enter your City Name: ")
    state = input("Please enter your State code: ")
    phone = input("Please enter your Phone Number: ")
    email = input("Please enter your Email: ")


    # Create query and parameters insert into database
    customerSQL = "INSERT INTO tblCustomer (firstName, lastName, street, city, state, phone, email) "
    customerSQL = customerSQL + " VALUES(%s, %s, %s, %s, %s, %s, %s)"
    parameters = (firstName, lastName, street, city, state, phone, email)
    cursor = mydb.cursor()
    cursor.execute(customerSQL, parameters)
    mydb.commit()

    # Notify the user about customer creation and its customer id
    print("Customer has been created and Saved to database")
    print("Customer Id: %d" % (cursor.lastrowid))

    # Create Account for the Customer
    accountNumber = nextAccountNumber()
    customerId = 1 #cursor.lastrowid 
    balance = 0 
    accountSQL = "INSERT INTO tblAccount VALUES(%s, %s, %s, %s)"
    parameters2 = (accountNumber, customerId, balance, 'active')
    cursor.execute(accountSQL, parameters2)
    mydb.commit()
    
    print("\nAccount has been created and assigned to Customer")
    print("Account Number:   %s" % accountNumber)
    print("Customer Id:      %d" % customerId)
    print("Account Balance:  %.2f" % balance)
    print("Account Status:  %s" % 'active')

# Function to add a successful transaction to the tblTransactions
def storeTransaction(accNo, trsAmount, trsType):

    # today's date
    now = datetime.now()
    trsDate = now.strftime('%Y-%m-%d')

    cursor = mydb.cursor()
    accountSQL = """INSERT INTO tblTransaction (TransactionId, AccountNumber, TransactionDate, 
    TransactionAmount, TransactionType) values(null, '%s', '%s', %.2f, '%s')""" % (accNo, trsDate, trsAmount, trsType) 
    # print(accountSQL)
    
    cursor.execute(accountSQL)
    mydb.commit()
    print("%s Transaction has been saved" % (trsType))

# function to display all the Customer Details including Personal 
# and all the accounts associated to the Customer
def displayCustomerAndAccounts():
    # read customer id
    customerId = 0 

    try: 
        customerId = int(input("Please enter Customer Id: "))

        customerSQL = '''Select * from tblCustomer where CustomerId="%d"''' % (customerId)
        cursor = mydb.cursor()
        cursor.execute(customerSQL)
        result = cursor.fetchone()

        if result == None:
            print("No Customer Found with this Id %d" % customerId)
        else: 
            print("Customer Details:")
            print("Customer Id:         %s" % result[0])
            print("Customer Name:       %s %s" % (result[1], result[2]))
            print("Street Address:      %s" % result[3])
            print("City:                %s" % result[4])
            print("State:               %s" % result[5])
            print("Phone Number:        %s" % result[6])
            print("Email:               %s" % result[7])

            accountSQL = '''SELECT * FROM tblAccount WHERE CustomerId="%d"''' % (customerId)
            cursor.execute(accountSQL)
            result = cursor.fetchall()

            print("\nCustomer Accounts: ")
            print("%15s %10s %10s" % ('Account Number', 'Balance', "Status"))

            for row in result:
                print("%15s %10s %10s" % (row[0], float(row[2]), row[3]))

            # Iterate all account
    except ValueError:
        print("Invalid Id entered")                

# Helper function to get the balance of a Given account
def getBalance(accountNumber): 

    accountSQL = '''Select Balance from tblAccount where AccountNumber="%s"''' % (accountNumber)
    cursor = mydb.cursor()
    cursor.execute(accountSQL)
    result = cursor.fetchone()

    if result == None:
        print("No Account found with this Account Number %s" % accountNumber)
        return -1
    else:
        return float(result[0])

# Function to Check the Balance of the account. 
def checkBalance():
    accountNumber = input("Please enter Account Number: ")
    accountNumber = accountNumber.upper()
    balance = getBalance(accountNumber)

    if balance >= 0:
            print("Account %s Current Balance is: %.2f" % (accountNumber, balance))

# Function to withdraw funds from the account. The User can only withdraw a positive
# value from the account. The withdrawal amount must be <= current balance
def withdrawAmount():
    try: 
        # Get account number
        accountNumber = input("Please enter Account Number: ")
        accountNumber = accountNumber.upper()

        if isActive(accountNumber):
                
            # Get amount
            amount = float(input("Please enter amount to withdraw: "))

            # check if amount is postive 
            if amount > 0: 
                
                balance = getBalance(accountNumber)

                # check if sufficient funds available 
                if balance >= amount:
                    balance = balance - amount

                    # Deposit amount
                    sql = """UPDATE tblAccount set Balance=%.2f WHERE AccountNumber='%s'""" % (balance, accountNumber)
                    cursor = mydb.cursor()
                    cursor.execute(sql)
                    mydb.commit()

                    # Save Transaction
                    storeTransaction(accountNumber, amount, 'withdrawal')

                    # display new balance
                    print("%.2f amount has been withdrawn" % amount)
                    print("Your new balance is %.2f" % balance)
                else: 
                    print("Insufficient Balance %.2f to withdraw %.2f amount" % (balance, amount))
            
            else: 
                print("You cannot deposit non-positive amount")
        else:
            print("Your account %s is inactive" % accountNumber)
            print("You can only withdraw from an active account")
    except ValueError:
        print("Invalid amount entered - try again")


# Function to perform a Deposit Operation. User can only deposit a positive
# amount and account number must be valid. 
def depositAmount(): 
    
    try: 
        # Get account number
        accountNumber = input("Please enter Account Number: ")
        accountNumber = accountNumber.upper()

        if isActive(accountNumber): 


            # Get amount
            amount = float(input("Please enter amount to deposit: "))

            # check if amount is postive 
            if amount > 0: 
                balance = getBalance(accountNumber) + amount 

                # Deposit amount
                sql = """UPDATE tblAccount set Balance=%.2f WHERE AccountNumber='%s'""" % (balance, accountNumber)
                cursor = mydb.cursor()
                cursor.execute(sql)
                mydb.commit()

                # Save Transaction
                storeTransaction(accountNumber, amount, 'deposit')


                # display new balance
                print("%.2f amount has been deposited" % amount)
                print("Your new balance is %.2f" % getBalance(accountNumber))
            else: 
                print("You cannot deposit non-positive amount")
        else:
            print("Your account %s is inactive" % accountNumber)
            print("You can only deposit in an active account")

    except ValueError:
        print("Invalid amount entered - try again")


# Function to close an account - Account will only be set to inactive
def deactivateAccount():
    # Get account number
    accountNumber = input("Please enter Account Number: ")
    accountNumber = accountNumber.upper()

    if isActive(accountNumber):
        # Decativate
        sql = """UPDATE tblAccount set Status='%s' where AccountNumber='%s'""" % ('inactive', accountNumber)
        cursor = mydb.cursor()
        cursor.execute(sql)
        mydb.commit()

        print("Your account %s has been deactivated")
    else: 
        print("Your acccount %s is already deactivated" % accountNumber)

# Function to check that a given account is active or inactive
def isActive(accountNumber):
    accountSQL = '''Select Status from tblAccount where AccountNumber="%s"''' % (accountNumber)
    cursor = mydb.cursor()
    cursor.execute(accountSQL)
    result = cursor.fetchone()
    if result != None:
        if result[0].lower() == 'active':
            return True 
    return False 

# Function to view all the Transactions of an account
def displayTransactions():
    # Get account number
    accountNumber = input("Please enter Account Number: ")
    accountNumber = accountNumber.upper()

    transSQL = '''Select * from tblTransaction where AccountNumber="%s"''' % (accountNumber)
    cursor = mydb.cursor()
    cursor.execute(transSQL)
    result = cursor.fetchall()

    if result == None:
        print("No Transaction exist for Account Number %s" % accountNumber)
    else:
        print('\nTransactions of Account# %s' % accountNumber) 
        print("%12s %15s %15s %15s %10s" % ('TransID', 'Acc-Number', 'Trans-Date', 'Amount', 'Type'))
        for row in result:
            print("%12s %15s %15s %15.2f %10s" % (row[0], row[1], row[2], float(row[3]), row[4]))

# function to display a menu and take the user's input. 
def menu():
    print("           Welcome to Account Management System")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-")
    print('''
        1. New customer
        2. Deposit an Amount
        3. Withdraw An Amount
        4. Check current balance
        5. Display Customer Details & Accounts
        6. Display Transactions of an Account
        7. Close account
        0. Exit''')
    choice = -1 

    while choice < 0 or choice > 8:
        try:
            choice = int(input("how may I help you? "))

            if choice < 0 or choice > 8: 
                print("Please enter a valid choice 0-7")

        except ValueError: 
            print("Please enter a valid choice 0-7")
    return choice 

if __name__ == "__main__":
    
    # User Selection
    choice = -1 

    # Main Loop 
    while choice != 0:

        # Show menu and get option
        choice = menu()
        print()
        if choice == 1: 
            # new Customer and account
            createAccount()
        elif choice == 2:
            # Deposit
            depositAmount() 
        elif choice == 3:
            # Withdraw
            withdrawAmount() 
        elif choice == 4:
            # Check Balance 
            checkBalance()
        elif choice == 5: 
            # display Customer and Accounts
            displayCustomerAndAccounts()
        elif choice == 6:
            # display transactions
            displayTransactions()
        elif choice == 7:    
            # close an Account 
            deactivateAccount() 
        else: 
            # Exit
            print("GoodBye:")
        print()