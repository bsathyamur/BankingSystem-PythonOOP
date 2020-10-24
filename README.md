## BANKING SYSTEM - MINI PROJECT - PYTHON OOP

## CLASS DESIGN AND SYSTEM DESIGN

The banking system is designed with 5 classes -> bankDatabase, bankTransactionLog, bankUser, bankAccounts and bankTransactions as represented in the below class UML diagram:

![pic1](https://github.com/bsathyamur/BankingSystem-PythonOOP/blob/master/class-diagram.jpg)

Once the user runs the program, an object of the class accounts class is instantiated and the user is prompted with two options - employee or customer. 

#### FOR BANK EMPLOYEE OPTION
If the user selects the option as "employee", the following options will be prompted for selection:
* create new employee user
* employee login and 
* exit
                                   
User can create a new employee user by selecting the option "create new employee user". Once a new employee user is created then the option for "employee login" can be selected to login by providing "user ID" and "first name" for authentication. Once authenticated the user will be provided with the below options - 
* create new customer
* Add accounts 
* customer accounts. 
                                  
The user can create new customer ID and then add accounts to the created new customer using the "create new customer" and "add acccounts" options. Once customer accounts are created the user can use the option "customer accounts" to perform operations such as 
* Deposit amount and 
* View Balance.

#### FOR CUSTOMER OPTION
If the user selects the option as customer then the user will be requested to login and authenticate using user id and first name. Once authenticated the user can select one of the following options to perform banking transactions:
* Deposit amount
* Withdraw amount
* View Balance
* Pay Balance

 All the activity of the program will get logged automatically in a log file bank_transaction_log.log which will be available in the same folder.                           
 
 The data is stored in the sqlite database in 2 tables - cust_accounts and user for which the table schema is shown below:

![pic2](https://github.com/bsathyamur/BankingSystem-PythonOOP/blob/master/db-tables.png)

## Instructions for program execution

The program can be run from command prompt by executing the below command:

python BankingSystem-Python-OOP.py

As a pre-requiste, the BankingSystem-DB.db sqlite file should be present in the same folder and sqlAlchemy library should be installed before execution.
