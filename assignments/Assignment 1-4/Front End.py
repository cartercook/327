'''
A basic terminal 
By Anthony Persico and Carter Cook
PROBLEMS: tickets not updated in eventList until logout
EVENT TRANSACTION:[2-digit transaction code] [20 character name] [event date, YYMMDD format] [# tickets in transaction]
EVENT LIST:[20 character event name] [# tickets in transaction]
'''
import datetime #used later for fetching/comparing dates
logged = None #'admin' or 'sales'
eventTransaction = [] #list of all transaction codes created in session
eventList = [] #list of all events, including created in session

#----------COMMANDS----------#
def login():
    global logged #import global variables for use in function
    global eventTransaction
    global eventList
    
    if logged == None:
        filein = open("CurrentEventsFile.txt", 'r')
        eventList = filein.read().splitlines() #convert file to array of strings
        filein.close()
        print "Would you like to log in to a sales or admin session?"
        session = raw_input('>')
        if session == "admin" or session == "sales":
            logged = session
            print 'Current Events:\n'+'\n'.join(eventList[:-1]) #print current events
            return 0
    return 1

def logout():
    global logged #import global variables
    global eventTransaction
    global eventList
    
    if logged != None: #if user is logged in
        eventTransaction.append("00                      000000 00000") #add transaction code to array
        eventTransactionFile = '\n'.join(eventTransaction) #convert list to a string delimited by \n 
        fileout = open("EventTransactionFile.txt", 'w') #open for writing
        fileout.write(eventTransactionFile) #overwrite
        fileout.close()
        logged = None #no longer admin/sales
        eventTransaction = [] #clear arrays
        eventList = []
        return 0 #success
    return 1 #otherwise failure

def create():
    global logged #import global variables
    global eventTransaction
    global eventList
    
    if logged == "admin":
        print "What is the name of the event you wish to create?"
        eventName = raw_input('>')
        if len(eventName) > 0 and len(eventName) < 21: #restrict invalid name lengths
            eventName = eventName.ljust(20) #left justify event name, pad with spaces
            if eventAlreadyExists(eventName) == -1: #if event name not taken
                print "What date will the event occur? (YYMMDD)"
                inputDate = raw_input('>')
                try:
                    eventDate = datetime.datetime.strptime(inputDate, "%y%m%d").date() #convert input into datetime.date object
                except:
                    print "invalid date."
                    return 1
                today = datetime.date.today() #today's date
                twoYears = today + datetime.timedelta(2*365) #date 2 years from now
                if eventDate > today and eventDate < twoYears:
                    print "How many tickets would you like to have available for the event?"
                    ticketCount = int(raw_input('>'))
                    if ticketCount > 0 and ticketCount < 100000: #restrict invalid ticket amounts
                        event = "03 "+eventName+" "+inputDate+" "+str(ticketCount).rjust(5,"0") #convert to proper string format
                        eventTransaction.append(event) #add to master list
                        return 0 #success
    return 1 #otherwise failure

def add():
    global logged #import global variables
    global eventTransaction
    global eventList

    if logged == "admin":
        print "What is the name of the event you wish to add tickets to?"
        eventName = raw_input('>')
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = eventAlreadyExists(eventName)
            if tickets != -1: #must add to an existing event
                print "How many tickets do you want to add?"
                ticketCount = int(raw_input('>'))
                if (ticketCount > 0 and ticketCount < 100000) or ticketcount + tickets < 100000:
                    event = "04 "+eventName+" 000000 "+str(ticketCount).rjust(5,"0") #convert to proper string format
                    eventTransaction.append(event) #add to master list
                    return 0 #success
    return 1 #failure
                    
def delete():
    global logged #import global variables
    global eventTransaction
    global eventList
    
    if logged == "admin":
        print "What is the name of the event you wish to delete?"
        eventName = raw_input('>')
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = eventAlreadyExists(eventName)
            if tickets != -1: #must delete an existing event
                event = "05 "+eventName+" 000000 00000" #convert to proper string format
                eventTransaction.append(event) #add to master list
                return 0 #success
    return 1 #failure

def sell():
    global logged #import global variables
    global eventTransaction
    global eventList
    
    if logged != None:
        print "What is the name of the event you wish to buy tickets to?"
        eventName = raw_input('>')
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = eventAlreadyExists(eventName)
            if tickets != -1: #can only sell tickets from existing events
                print "How many tickets do you want to buy?"
                if logged == "admin":
                    limit = 100000
                elif logged == "sales":
                    limit = 9
                ticketCount = int(raw_input('>'))
                if ticketCount > 0 and ticketCount < limit and ticketcount <= tickets:
                    event = "01 "+eventName+" 000000 "+str(ticketCount).rjust(5,"0") #convert to proper string format
                    eventTransaction.append(event) #add to master list
                    return 0 #success
    return 1 #failure

def reTurn(): #capital T avoids conflicts with python return statement
    global logged #import global variables
    global eventTransaction
    global eventList

    if logged != None:
        print "What is the name of the event you wish to return tickets to?"
        eventName = raw_input('>')
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = eventAlreadyExists(eventName)
            if tickets != -1: #must return to an existing event
                print "How many tickets do you want to return?"
                if logged == "admin":
                    limit = 100000
                elif logged == "sales":
                    limit = 9
                ticketCount = int(raw_input('>'))
                if ticketCount > 0 and ticketCount < limit and ticketcount + tickets < 100000:
                    event = "01 "+eventName+" 000000 "+str(ticketCount).rjust(5,"0") #convert to proper string format
                    eventTransaction.append(event) #add to master list
                    return 0 #success
    return 1 #failure

#----------HELPER FUNCTIONS----------#
def eventAlreadyExists(eventName):
    global eventList #import eventList variable
    
    tickets = -1
    for line in eventList: #for all current events
        if line[0:20] == eventName: #if existing event has same name
            tickets = int(line[21:])
    return tickets

#----------MAIN----------#
def main():
    commands = ["login", "logout", "create", "add", "delete", "sell", "return"] #list of possible user input
    functions = [login, logout, create, add, delete, sell, reTurn] #related functions
    print "'login' to begin a session."
    while True: #loop until exit
        userInput = raw_input('>>') #print '>>' and wait for user input
        if userInput == "close":
            exit()
        indentified = False
        for i in range(len(commands)):
            if userInput == commands[i]: #check if userInput matches each command
                identified = True
                complete = functions[i]() #run corresponding command
                if complete == 1: #if command threw an error
                    print "There was an input error with the "+commands[i]+" function, please try again."
        if not identified: #if command is unrecognised
            print "Unrecognised command."
main()
