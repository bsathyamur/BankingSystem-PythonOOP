## BANKING SYSTEM - MINI PROJECT - PYTHON OOP

## DESIGN 

The banking system is designed with 2 classes -> 1. Bank and 2. Accounts as represented in the below class diagram:

![pic1](https://github.com/bsathyamur/BankingSystem-PythonOOP/blob/master/class-diagram.jpeg)

The class Accounts inherits from parent class Bank.

Once the user runs the program, an object of the class accounts class is instantiated and the user is prompted with two options - employee or customer. 

If the user selects the option as employee then the following options will be prompted to select - 
* create new employee user
* employee login and 
* exit
                                   
User can create a new employee user by selecting the option "create new employee user". Once a new employee user is created then the option for "employee login" can be selected to login by providing user ID and first name for authentication, once authenticated the user can select one of the below options - 
* create new customer
* Add accounts 
* customer accounts. 
                                  
The user can create new customer ID and then add accounts to the created new customer using the create new customer and add acccounts options. Once customer accounts are created the user can use the option customer accounts to perform operations such as Deposit amount and View Balance.

If the user selects the option as customer then the user will be requested to login and authenticate using user id and first name. Once authenticated the user can select one of the following options to perform banking transactions:
* Deposit amount
* Withdraw amount
* View Balance
* Pay Balance

 All the activity of the program will get logged automatically in a log file bank_transaction_log.log                               
 
 The data is stored in the sqlite database in 2 tables - 


## Instructions for execution
The program can be run from command prompt by executing the below command:
python BankingSystem-Python-OOP.py

The following files should also be present in the same folder - BankingSystem-DB.db

