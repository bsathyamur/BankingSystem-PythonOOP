from sqlalchemy import create_engine,MetaData,Table
from sqlalchemy import select,insert,update,and_,or_,func
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from random import randint
import logging

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
    def __repr__(self):
        return self.message
    
class bankTransactionLog:
    
    def __init__(self):
        # Adding information related to logger
        self.logger = logging.getLogger('dev')
        self.logger.setLevel(logging.INFO)
        self.fileHandler = logging.FileHandler('bank_transaction_log.log')
        self.fileHandler.setLevel(logging.INFO)
        self.logger.addHandler(self.fileHandler)
        self.formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
        self.fileHandler.setFormatter(self.formatter)
        
    def logTransaction(self,info):
        self.logger.info(info)
        
class bankDatabase:
    
    global dbUrl 
    
    dbUrl = "sqlite:///BankingSystem-DB.db"
    
    def __init__(self):
        self.log = bankTransactionLog()
                    
    @contextmanager
    def db_connect(self,dbURL):
        engine = create_engine(dbUrl)
        try:
            self.log.logTransaction('opening connection to database')
            connection = engine.connect()
            yield connection
        finally:
            self.log.logTransaction('closing connection to database')
            connection.close()
            engine.dispose()   
    
class bankUser:
    def __init__(self):
        self.db =  bankDatabase()
        self.log = bankTransactionLog()
        
    def createUser(self,f_name,l_name,u_type,dsgnation = None)->int:
        """
        Creates a unique user id for employee or customer
        Parameters
        ----------
        f_name : string
            First name.
        lastname : string
            Last name
        u_type : string
            user type - E for employee and C for customer
        dsgnation : string
            designation - expected only for employee
        Returns
        -------
        int
            user id if successful, -1 otherwise
        """
        
        self.log.logTransaction("Open createUser")

        try:    
            # Validate input arguments
            if len(f_name) <= 0:
                raise ValidationError("Validation Error: First name is empty")
            elif len(l_name) <= 0:
                raise ValidationError("Validation Error: Last name is empty")
            elif u_type not in ('E','C'):
                raise ValidationError("Validation Error: Invalid user type")
            elif u_type == 'E' and (len(str(dsgnation)) <= 0 or dsgnation is None):
                raise ValidationError("Validation Error: For User Employee designation is required")
            
            # Initialize the user cnt to -1 as default
            user_cnt = -1
        
            # Create a unique user id
            while user_cnt != 0:
                u_id = randint(1,100000)
            
                with self.db.db_connect(dbUrl) as db_engine:
            
                    # Check if the user id doesn't exist
                    metadata = MetaData(bind=db_engine)
                    user = Table('user', metadata, autoload_with=db_engine)
                    stmt = select([user])
                    stmt = stmt.where(user.columns.user_id == u_id)
                
                    result = db_engine.execute(stmt).fetchall()
                    user_cnt = len(result)
                
            with self.db.db_connect(dbUrl) as db_engine:
                metadata = MetaData(bind=db_engine)
                user = Table('user', metadata, autoload_with=db_engine)
                
                now = datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                
                # Insert the user id into the user table                       
                if u_type == 'E':
                    stmt_user = insert(user).values(user_id = u_id,user_type = u_type,user_create_dt = formatted_date,
                                                first_name=f_name,last_name=l_name,designation=dsgnation,status='ACTIVE')
                else:
                    stmt_user = insert(user).values(user_id = u_id,user_type = u_type,user_create_dt = formatted_date,
                                                first_name=f_name,last_name=l_name,designation=None,status='ACTIVE')
                result = db_engine.execute(stmt_user)
                row_cnt = result.rowcount
                
            # If insert into user id is successful 
            if row_cnt == 1:
                self.log.logTransaction('Close createUser')                
                return u_id
            else:
                raise ValidationError("Account creation Failed")
            
        except ValidationError as e:
            self.log.logTransaction('Exception: CreateUser')
            print(e.message)
            return -1
        
    def authenticateUser(self,u_id,u_type,f_name) -> bool:
        """
        Authenticates a user id based on user id and first name values
        Parameters
        ----------
        u_id : int
            user id
        u_type : string
            user type - E for employee and C for customer
        f_name : string
            first name
        Returns
        -------
        bool
            True if successful, False otherwise
        """

        self.log.logTransaction("Open authenticateUser")    

        try:
            if len(str(u_id)) <= 0:
                    raise ValidationError("Validation Error: User ID is required.")
            if len(str(f_name)) <= 0 or f_name is None:
                raise ValidationError("Validation Error:First name is required.")  
                
            user_cnt = -1
        
            with self.db.db_connect(dbUrl) as db_engine:
            
                # Check if the user id doesn't exist
                metadata = MetaData(bind=db_engine)
                user = Table('user', metadata, autoload_with=db_engine)       
            
                stmt = select([user])
                stmt = stmt.where( and_(user.columns.user_id == u_id, 
                                        func.lower(user.columns.first_name) == f_name.lower(),
                                        user.columns.user_type == u_type,
                                        user.columns.status == 'ACTIVE') 
                                 )
                result = db_engine.execute(stmt).fetchall()
                
                user_cnt = len(result)
                
                if user_cnt == 1:
                    self.log.logTransaction("Close authenticateUser")                     
                    return True
                else:
                    raise ValidationError("Authentication Error: User ID is not valid")
            
        except ValidationError as e:
            self.log.logTransaction("Exception: authenticateUser")  
            print(e.message)
            return False

class bankAccounts:
    
    def __init__(self):
        self.db =  bankDatabase()
        self.log = bankTransactionLog()        

    def validateAccount(self,u_id,account_no,action_choice)->bool:
        """
        Validate if the account number provided is valid and 
        returns if a match is found

        Parameters
        ----------
        u_id : int
            user id
        account_no : string
            customer account number
        action_choice : string
            user selected action - deposit/withdrawal/view balance/pay balance

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        self.log.logTransaction("Open validateAccount")

        try:
            with self.db.db_connect(dbUrl) as db_engine:
                acct_cnt = 0
                metadata = MetaData(bind=db_engine)
                cust_accounts = Table('cust_accounts', metadata, 
                                        autoload_with=db_engine)
                stmt = select([cust_accounts])                        
                
                if action_choice == 1:
                    stmt = stmt.where( or_(cust_accounts.columns.acct_type == 'Checking',
                                           cust_accounts.columns.acct_type == 'Savings'))
                    stmt = stmt.where( 
                                       and_(cust_accounts.columns.user_id == u_id,
                                           cust_accounts.columns.acct_no == account_no,
                                           cust_accounts.columns.acct_sts == 'ACTIVE')
                                     ) 
                elif action_choice in (2,3):                  
                    stmt = stmt.where( 
                                       and_(cust_accounts.columns.user_id == u_id,
                                           cust_accounts.columns.acct_no == account_no,
                                           cust_accounts.columns.acct_sts == 'ACTIVE')
                                     )                     
                elif action_choice == 4:                  
                    stmt = stmt.where( or_(cust_accounts.columns.acct_type == 'Loan',
                                           cust_accounts.columns.acct_type == 'Credit')
                                     )
                    stmt = stmt.where(and_(cust_accounts.columns.user_id == u_id,
                                           cust_accounts.columns.acct_no == account_no,
                                           cust_accounts.columns.acct_sts == 'ACTIVE')
                                     )
                elif  u_id is None:
                    stmt = stmt.where( 
                                       and_(cust_accounts.columns.acct_no == account_no,
                                           cust_accounts.columns.acct_sts == 'ACTIVE')
                                     )                     

                result = db_engine.execute(stmt).fetchall()
                acct_cnt = len(result)
                
            if acct_cnt == 1:
                self.log.logTransaction("Close validateAccount")                
                return True
            else:
                raise ValidationError("Validation Error: Account not found")
                
        except ValidationError as e:
            self.log.logTransaction("Exception: validateAccount")            
            print(e.message)
            return False

    def addAccount(self,u_id,f_name,account_type,avail_bal) -> int:

        """
        Creates a new customer account
        Parameters
        ----------
        u_id : int
            user id
        f_name: string
            first name
        account_type : string
            account type
        avail_bal : int
            initial deposit amount or approved credit/loan amount
        Returns
        -------
        int
            account number if successful, -1 otherwise
        """
        
        self.log.logTransaction("Open addAccount")

        try:    
            # Validate input arguments
            if len(str(u_id)) <= 0:
                raise ValidationError("Validation Error: Customer ID is required")
            elif avail_bal <= 0:
                raise ValidationError("Validation Error: Balance amount cannot be negative/zero")
            else:
                # Check if the user id and firstname is valid
                with self.db.db_connect(dbUrl) as db_engine:
            
                    # Check if the user id doesn't exist
                    metadata = MetaData(bind=db_engine)
                    user = Table('user', metadata, autoload_with=db_engine)
                    stmt = select([user])                    
                    stmt = stmt.where( and_(user.columns.user_id == u_id, 
                                        func.lower(user.columns.first_name) == f_name.lower(),
                                        user.columns.user_type == "C") 
                                 )
                
                    result = db_engine.execute(stmt).fetchall()
                    user_cnt = len(result)               
                
                    if user_cnt == 1:
                        # Generate unique acct number
                        acct_cnt = -1
                        cust_accounts = Table('cust_accounts', metadata, 
                                                  autoload_with=db_engine)
                        
                        while acct_cnt == -1:
                            account_no = randint(100001,1000000) 
                            # Check if the account number doesn't exist
                            stmt = select([cust_accounts])
                            stmt = stmt.where(cust_accounts.columns.acct_no == account_no)
                            result = db_engine.execute(stmt).fetchall()
                            acct_cnt = len(result) 
                    
                        stmt_acct = insert(cust_accounts).values(user_id = u_id,
                                                                 acct_type = account_type,
                                                                 available_bal = avail_bal,
                                                                 remaining_bal=0,
                                                                 acct_no=account_no,
                                                                 acct_sts='ACTIVE')
                        result = db_engine.execute(stmt_acct)
                        row_cnt = result.rowcount
                        
                        if row_cnt == 1:
                            self.log.logTransaction("Close addAccount")                            
                            return account_no
                        else:
                            raise ValidationError("Account creation failed.")
                    else:                    
                        errmsg = """
                                Error: 
                                    Customer ID: {user_id}, 
                                    First name: {fname}
                                not found.
                                """.format(user_id = u_id,fname = f_name)
                        raise ValidationError(errmsg)
        
        except ValidationError as e:
            self.log.logTransaction("Exception: addAccount")                
            print(e.message)
            return -1
        
        
class bankTransactions:
    
    def __init__(self):
        self.db =  bankDatabase()  
        self.log = bankTransactionLog()           

    def validateTransaction(func):
        @wraps(func)
        def wrapped(self,u_id,acctno,amt):
            
            try:
                if u_id is not None:
                    if len(str(u_id)) <= 0:
                        raise ValidationError("Error: User ID cannot be blank")
                elif len(str(acctno)) <= 0 or acctno == 0:
                    raise ValidationError("Error: Account no cannot be blank or zero")
                elif amt is not None:
                    if amt <= 0:
                        raise ValidationError("Error: Transaction amount cannot be negative/zero")
            
                return func(self,u_id,acctno,amt)
            
            except ValidationError as e:
                print(e.message)
                return False
                
        return wrapped
    
    @validateTransaction
    def depositAmt(self,u_id : int,acctno : int,depositAmt :  int) -> bool:
        """
        Deposit the amount to the customer account
        Parameters
        ----------
        u_id : int
            user id
        acctno: int
            account number
        depositAmt : int
            Deposit amount to the account
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        
        self.log.logTransaction("Open depositAmt")   

        try:
            row_cnt = 0
        
            with self.db.db_connect(dbUrl) as db_engine:
                metadata = MetaData(bind=db_engine)
                cust_accounts = Table('cust_accounts', metadata, autoload_with=db_engine)
            
                current_bal = select([cust_accounts.columns.available_bal])

                if u_id is not None:
                    current_bal = current_bal.where(and_(cust_accounts.columns.user_id==u_id,
                                                         cust_accounts.columns.acct_no==acctno))
                else:
                    current_bal = current_bal.where(cust_accounts.columns.acct_no==acctno)

                current_bal = current_bal.limit(1)
                
                rslt_amt = db_engine.execute(current_bal).fetchall()
                new_amt = int(rslt_amt[0].available_bal) + depositAmt
            
                stmt = update(cust_accounts)

                if u_id is not None:
                    stmt = stmt.where(and_(cust_accounts.columns.user_id==u_id,
                                           cust_accounts.columns.acct_no==acctno))
                else:
                    stmt = stmt.where(cust_accounts.columns.acct_no==acctno)

                stmt = stmt.values(available_bal = new_amt )
            
                result = db_engine.execute(stmt)
            
                row_cnt = result.rowcount
            
            if row_cnt != 0:
                self.log.logTransaction("Close depositAmt")                  
                print("""
                         Amount ${amt} successfully deposited 
                         into the account {acct}, 
                         New Balance is ${newamt}
                    """.format(amt = depositAmt,acct = acctno,newamt = new_amt))
                return True
            else:
                raise ValidationError("Error: Deposit transaction failed.")
        except ValidationError as e:
            self.log.logTransaction("Exception: depositAmt")              
            print(e.message)
            return False           
     
    @validateTransaction    
    def withdrawAmt(self,u_id,acctno,withdrawAmt) -> bool:   

        """
        Withdraw amount from the customer account
        Parameters
        ----------
        u_id : int
            user id
        acctno: int
            account number
        withdrawAmt : int
            withdrawal amount from the account
        Returns
        -------
        bool
            True if successful, False otherwise
        """        
        
        self.log.logTransaction("Open withdrawAmt")        
        
        try:
            row_cnt = 0
        
            with self.db.db_connect(dbUrl) as db_engine:
                metadata = MetaData(bind=db_engine)
                cust_accounts = Table('cust_accounts', metadata, autoload_with=db_engine)
            
                current_bal = select([cust_accounts.columns.available_bal,
                                      cust_accounts.columns.acct_type,
                                      cust_accounts.columns.remaining_bal])
                current_bal = current_bal.where(and_(cust_accounts.columns.user_id==u_id,
                                                     cust_accounts.columns.acct_no==acctno))
                current_bal = current_bal.limit(1)
                
                rslt_amt = db_engine.execute(current_bal).fetchall()
                curr_amt = int(rslt_amt[0].available_bal)
                account_type = rslt_amt[0].acct_type
                remain_bal = int(rslt_amt[0].remaining_bal)
                
                if curr_amt <= 0:
                    raise ValidationError("""
                                            Current balance is zero/negative. 
                                            Funds cannot be withdrawn
                                          """)
                elif curr_amt < withdrawAmt:
                    msg = """
                            Withdrawal amount is greater 
                            than current balance ${curramt}
                          """.format(curramt = curr_amt)
                    raise ValidationError(msg)
                
                avail_new_amt = curr_amt - int(withdrawAmt)
                remain_new_amt = 0
                
                if account_type in ('Loan','Credit'):
                    remain_new_amt = remain_new_amt + withdrawAmt
                    
                stmt = update(cust_accounts)
                stmt = stmt.where(and_(cust_accounts.columns.user_id==u_id,
                                       cust_accounts.columns.acct_no==acctno))
                stmt = stmt.values(available_bal = avail_new_amt,
                                   remaining_bal = remain_new_amt)
            
                result = db_engine.execute(stmt)
            
                row_cnt = result.rowcount
            
            if row_cnt != 0:
                if account_type in ('Checking','Savings'):
                    msg = """
                             Amount ${amt} successfully withdrawn 
                             from the {acct} account {acctnum}, 
                             New available balance is ${newamt}.
                         """.format(amt = withdrawAmt,acct = account_type,
                                acctnum = acctno,newamt = avail_new_amt)
                else:
                    msg = """
                             Amount ${amt} successfully withdrawn 
                             from the {acct} account {acctnum}, 
                             New available balance is ${newamt},
                             New payment balance is ${pymt}.
                         """.format(amt = withdrawAmt,acct = account_type,
                                acctnum = acctno,newamt = avail_new_amt,
                                    pymt = remain_new_amt)                    
                
                print(msg)
                self.log.logTransaction("Close withdrawAmt")                  
                return True
            else:
                raise ValidationError("Error: Withdrawal transaction failed.")
        except ValidationError as e:
            self.log.logTransaction("Exception: withdrawAmt")              
            print(e.message)
            return False 
    
    @validateTransaction
    def showBalance(self,u_id,acctno,amt = None) -> bool:              
        """
        Show balance amount in the customer account
        Parameters
        ----------
        u_id : int
            user id
        acctno: int
            account number
        amt : int 
            defaulted to None
        Returns
        -------
        bool
            True if successful, False otherwise
        """  
        self.log.logTransaction("Open showBalance")    

        try:
            row_cnt = 0
        
            with self.db.db_connect(dbUrl) as db_engine:
                metadata = MetaData(bind=db_engine)
                cust_accounts = Table('cust_accounts', metadata, autoload_with=db_engine)
            
                current_bal = select([cust_accounts.columns.available_bal,
                                      cust_accounts.columns.acct_type,
                                      cust_accounts.columns.remaining_bal])
                if u_id is not None:
                    current_bal = current_bal.where(and_(cust_accounts.columns.user_id==u_id,
                                                         cust_accounts.columns.acct_no==acctno))
                else:
                    current_bal = current_bal.where(cust_accounts.columns.acct_no==acctno)
                    
                current_bal = current_bal.limit(1)
                
                rslt_amt = db_engine.execute(current_bal).fetchall()
                curr_amt = int(rslt_amt[0].available_bal)
                account_type = rslt_amt[0].acct_type
                remain_bal = int(rslt_amt[0].remaining_bal)
            
                row_cnt = len(rslt_amt)
            
            if row_cnt != 0:
                if account_type in ('Checking','Savings'):
                    msg = """
                             Available balance in {acct} account {acctnum}, 
                             is ${curramt}.
                         """.format(acct = account_type,
                                    acctnum = acctno,curramt = curr_amt)
                else:
                    msg = """
                             Available balance in {acct} account {acctnum}, 
                             is ${curramt} and payment balance is ${pymtamt}.
                         """.format(acct = account_type,
                                    acctnum = acctno,
                                    curramt = curr_amt,
                                    pymtamt = remain_bal
                                   )                  
                
                print(msg)

                self.log.logTransaction("Close showBalance")                    
                return True
            else:
                raise ValidationError("Error: View balance transaction failed.")
        except ValidationError as e:
            self.log.logTransaction("Exception: showBalance")             
            print(e.message)
            return False 
 
    @validateTransaction   
    def payBalance(self,u_id,acctno,paymentAmt) -> bool:              
        """
        Pay balance amount in the credit / loan account
        Parameters
        ----------
        u_id : int
            user id
        acctno: int
            account number
        paymentAmt : int 
            payment amount
        Returns
        -------
        bool
            True if successful, False otherwise
        """  
        
        self.log.logTransaction("Open: payBalance") 

        try:
            row_cnt = 0
        
            with self.db.db_connect(dbUrl) as db_engine:
                metadata = MetaData(bind=db_engine)
                cust_accounts = Table('cust_accounts', metadata, autoload_with=db_engine)
            
                current_bal = select([cust_accounts.columns.available_bal,
                                      cust_accounts.columns.acct_type,
                                      cust_accounts.columns.remaining_bal])
                current_bal = current_bal.where(and_(cust_accounts.columns.user_id==u_id,
                                                     cust_accounts.columns.acct_no==acctno))
                current_bal = current_bal.limit(1)
                
                rslt_amt = db_engine.execute(current_bal).fetchall()
                curr_amt = int(rslt_amt[0].available_bal)
                account_type = rslt_amt[0].acct_type
                remain_bal = int(rslt_amt[0].remaining_bal)
                
                avail_new_amt = curr_amt + int(paymentAmt)
                remain_new_amt = remain_bal - int(paymentAmt)
                    
                stmt = update(cust_accounts)
                stmt = stmt.where(and_(cust_accounts.columns.user_id==u_id,
                                       cust_accounts.columns.acct_no==acctno))
                stmt = stmt.values(available_bal = avail_new_amt,
                                   remaining_bal = remain_new_amt)
            
                result = db_engine.execute(stmt)
            
                row_cnt = result.rowcount
            
            if row_cnt != 0:
                msg = """
                             Payment amount ${amt} successfully posted
                             to the {acct} account {acctnum}, 
                             New available balance is ${newamt},
                             New payment balance is ${pymt}.
                      """.format(amt = paymentAmt,acct = account_type,
                                acctnum = acctno,newamt = avail_new_amt,
                                    pymt = remain_new_amt)                    
                
                print(msg)
                self.log.logTransaction("Close: payBalance")                 
                return True
            else:
                raise ValidationError("Error: payment transaction failed.")
        except ValidationError as e:
            self.log.logTransaction("Exception: payBalance")              
            print(e.message)
            return False


try:
    print()
    print("""Enter 
                1 for Employee
                2 for Customer
        """)
    userchoice = int(input())

    while True:
        
        if userchoice == 1:
            print()
            print(""" Enter 
                    1 for create new employee user
                    2 for employee login
                    3 to exit
                """)
            empchoice = int(input())
            bankusr = bankUser()

            if empchoice == 1:
                print()
                print("Enter First name")
                fname = input()
                print("Enter Last name")
                lname = input()
                print("Enter Designation")
                desig = input()
                user_type = "E"
                   
                u_id = bankusr.createUser(fname,lname,user_type,desig)
                
                if u_id != -1:
                    print("Employee User ID successfully created: " + str(u_id))

            elif empchoice == 2:
                print()
                print("Enter user id")
                user_id = input()
                print("Enter first name")
                fname = input()
                user_type = "E"
                authresult = bankusr.authenticateUser(user_id,user_type,fname)
                
                if authresult:
                    print()
                    print("""
                            Enter 
                                1 for create new customer
                                2 for add account to existing customer
                                3 for customer accounts
                        """)
                    custchoice = int(input())
                    
                    if custchoice == 1:
                        print()
                        print("Enter first name")
                        fname = input()
                        print("Enter last name")
                        lname = input()
                        desig = None
                        user_type = "C"
                    
                        u_id = bankusr.createUser(fname,lname,user_type,desig)
                
                        if u_id != -1:
                            print("Customer User ID successfully created: " + str(u_id))
                    
                    elif custchoice == 2:
                        
                        print()
                        print("Enter customer user id")
                        u_id = int(input())
                        print("Enter customer first name")
                        f_name = input()                    
                        print("""
                                Enter 1 for Loan
                                    2 for Credit
                                    3 for checking
                                    4 for Savings
                            """)                            
                        acct_type = int(input())
                        acct1 = bankAccounts()
                        
                        if acct_type in (1,2,3,4):
                            print()
                            print("Enter available balance/initial deposit amount")
                            avail_bal = int(input())
                            
                            if acct_type == 1:
                                acct = "Loan"
                                
                            elif acct_type == 2:
                                acct = "Credit"
                            elif acct_type == 3:
                                acct = "Checking"                           
                            elif acct_type == 4:
                                acct = "Savings" 

                            acct_no = acct1.addAccount(u_id,f_name,acct,avail_bal)
                            
                            if acct_no != -1:
                                msg = """
                                        Customer ID: {user_id}, 
                                        First name: {fname},
                                        Account Type: {acct_type}
                                        Account no: {account_num}
                                    successfully created.
                                    """.format(user_id = u_id,fname = f_name,
                                            acct_type=acct,account_num = acct_no)    
                                print(msg)
                    elif custchoice == 3:
                        print("""
                                Enter 1 for Deposit amount
                                      2 for View Balance
                            """)                            
                        emp_custchoice = int(input())
                        acct2 = bankAccounts()

                        print()
                        print("Enter customer account no")
                        acct_no = int(input())

                        if emp_custchoice == 1:
                            print("Enter deposit amount")
                            deposit_amt = int(input())
                        
                        authresult = acct2.validateAccount(None,acct_no,None)
                        
                        trans = bankTransactions()

                        if authresult:
                            if emp_custchoice == 1:                        
                                result = trans.depositAmt(None,acct_no,deposit_amt)                            
                            else:
                                result = trans.showBalance(None,acct_no,None) 
                    else:
                        print("Error: Invalid choice selected.")
            else:
                break
                
        elif userchoice == 2:
            print()
            print("Enter 1 to login")
            print("Enter 2 to exit")
            cust_choice = int(input())
            
            bankusr2 = bankUser()

            if cust_choice == 1:
                print()
                print("Enter user id")
                u_id = int(input())
                print("Enter first name")
                f_name = input() 
                user_type = "C"
                
                authresult = bankusr2.authenticateUser(u_id,user_type,f_name)
                
                if authresult:
                    print()
                    print("""
                    Enter 1 for Deposit amount
                        2 for Withdraw amount 
                        3 for View balance 
                        4 for Pay balance
                        """)
                    action_choice = int(input())                
                    
                    if action_choice in (1,2,4):
                        print()
                        print("""
                        Enter deposit / withdraw / payment amount
                            """)
                        trans_amt = int(input())  
                        
                    print()
                    print("Enter account no")
                    account_no = int(input())
                    
                    acct2 = bankAccounts()

                    authresult = acct2.validateAccount(u_id,account_no,action_choice)
                                        
                    if authresult:
                        trans2 = bankTransactions()

                        if action_choice == 1:                        
                            result = trans2.depositAmt(u_id,account_no,trans_amt)
                        if action_choice == 2:
                            result = trans2.withdrawAmt(u_id,account_no,trans_amt)
                        if action_choice == 3:
                            result = trans2.showBalance(u_id,account_no,None)                        
                        elif action_choice == 4:
                            result = trans2.payBalance(u_id,account_no,trans_amt)
                        else:
                            result = "Error: Invalid choice selected"
                        
            else:
                break
            
        else:
            break
except ValueError as e1:
    print("Entered input is not a number.")
except Exception as e2:
    print("unhandled exception occurred")