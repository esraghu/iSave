import sys
import time
#sys.path.append("C:\Program Files (x86)\Google\google_appengine")

#from google.appengine.api import users
#from google.appengine.ext import ndb

import webapp2
from urllib2 import Request, urlopen, URLError
import json

def getToken(clientID, password):
    request = Request("http://corporate_bank.mybluemix.net"\
                      "/corporate_banking/mybank/authenticate_client?"\
                      "client_id={0}&password={1}".format(clientID,password))
    try:
        response = urlopen(request)
        respJson = json.loads(response.read())
        #response will be a string in the format [{"token":"5b7437e85234"}]
        return respJson[0]['token'].encode()
    except URLError, e:
        pass

def checkCode(url):
    request = Request(url)

    try:
        response = urlopen
        response = urlopen(request)
        respJson = json.loads(response.read())
        code = respJson[0]['code'].encode()
        if code != 200:
            return False
        else:
            return respJson[1]
    except URLError, e:
        pass
        
def getAccInfo(clientID):
    request = Request("http://participant_mapping.mybluemix.net/banking/icicibank/participantmapping?client_id={}".format(clientID))
    try:
            response = urlopen(request)
            allinfo = json.loads(response.read())
            return (allinfo[0]["account_no"].encode(), allinfo[0]["cust_id"].encode())
            
    except URLError, e:
            print "Got the error code: ", e

#def getAccSummary(clientID, token, accNo):
#    request = Request("

txnRef = 100000
txn_rec = []

class Account():
    
    """ Root class to create various accounts with regular attributes
    """
    #accountNumber = ndb.IntegerProperty('accNo')
    #accountType = ndb.StringProperty('accType')
    #accountHolder = ndb.StringProperty('name')
    #accountBalance = ndb.FloatProperty('bal')
    def __init__(self, account_number, account_holder, account_type="Savings", current_balance=0):
        self.account_number = account_number
        self._account_type = account_type
        self.name = account_holder
        self._balance = current_balance

    def debit_the_account(self, amount):
        if (self._balance - amount) > 0:
            self._balance -= amount
            print self._balance
            return True
        else:
            return False

    def credit_the_account(self, amount):
        self._balance += amount
        print self._balance

    def get_account_no(self):
        return self.account_number
                      
    def account_info(self):
        return "Account Number: {0} "  \
               "Account Type: {1} "    \
               "Account Holder: {2} "  \
               "Current Balance: {3} " \
               .format(self.account_number, self._account_type, self.name, self._balance)

class Goal(Account):
    """ This class extends from the class Account
    """

    def __init__(self, account_number, account_holder, account_type="Savings", current_balance=0, target = 5000, period = 90):
        Account.__init__(self, account_number, account_holder, account_type, current_balance)
        self._target = target
        self._period = period

    def goal_info(self):
        return str(self.account_info()) + \
               "Goal Target: {0}" \
               "Goal Period: {1}" \
               .format(self._target, self._period)
        
def incr_txn_ref():
    global txnRef
    txnRef = txnRef + 1

def add_transaction(from_acc, to_acc, amount, txn_reason):
    global txn_rec
    _timestamp = time.time()
    _from_acc = from_acc.account_number
    _to_acc = to_acc.account_number
    _amount = amount
    _txn_reason = txn_reason
    incr_txn_ref()
    txn_rec.append((
                txnRef,
               _timestamp,
               _from_acc,
               _to_acc,
               _amount,
               _txn_reason))
    return True

def transact(from_acc, to_acc, amount, txn_reason=""):
    if isinstance(from_acc, Account) and isinstance(to_acc, Account):
        if from_acc.debit_the_account(amount):
            to_acc.credit_the_account(amount)
            if add_transaction(from_acc, to_acc, amount, txn_reason):
                #print("Transaction added successfully")
                return 0
            else:
                # We now need to reverse the transaction as we couldn't
                # write the transaction successfully.
                #print("Transaction reversed")
                to_acc.debit_the_account(amount)
                from_acc.credit_the_account(amount)
                return 1
            from_acc.account_info()
            to_acc.account_info()
        else:
            #print("Insufficient funds in {}".format(from_acc.account_number))
            return 2

#Let's add some accounts and transactions to start with
source = Account(123456,"Savings","Raghunandan",50000)
goal1 = Goal(123457,"Goal1","Raghunandan",0,5000,90)
goal2 = Goal(123457,"Goal2","Raghunandan",0,8000,45)

##print source.account_info()
##print goal1.goal_info()
##print goal2.goal_info()

##transact(source, goal1, 50, "daily static")
##transact(source, goal2, 97.50, "daily percent spend")
##transact(source, goal1, 15, "daily match tea spend")

##print source.account_info()
##print goal1.goal_info()
##print goal2.goal_info()

##print txn_rec

clientID = "l.narasimhan@gmail.com"
password = "ICIC4471"
token = getToken(clientID, password)
#sourceAccNo = int(getAccInfo(clientID))
#sourceAcc = Account(*getAccSummary)

def varget(var):
    return var
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.write(source.account_info())
        self.response.write(goal1.goal_info())
        self.response.write(goal2.goal_info())
        self.response.write("Transactions so far" + str(txn_rec))

class AddGoalPage(webapp2.RequestHandler):
    def get(self):
        goalname = self.request.get("goal")
        accname = self.request.get("accname")
        target = self.request.get("target")
        period = self.request.get("period")
        exec(goalname + "= Goal(123457,goalname,accname,0,target,period)")
        exec("goalinfo = " + goalname + ".goal_info()")
        self.response.write(goalinfo)
             
class TransactPage(webapp2.RequestHandler):
    def get(self):
        src = self.request.get("src")
        #exec("srcAcc = {}" + src)
        self.response.write(src)
        dest = self.request.get("dest")
        #exec("destAcc = " + dest)
        amount = int(self.request.get("amount"))
        reason = self.request.get("reason")
        x = transact(varget(src), varget(dest), amount, reason)
        if x == 0:
            self.response.write("Transfer successful")
        elif x == 1:
            self.response.write("Transfer failed")
        elif x == 2:
            self.response.write("Improper Accounts")
        else:
            self.response.write("Response from transact function is : {}".format(x))
        
        
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/addgoal', AddGoalPage),
    ('/transact', TransactPage)
    ],debug=True)
