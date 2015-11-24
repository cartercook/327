'''
A basic terminal frontend that reads in a file of event names and numbers of tickets available, 
processes a stream of ticket transactions one at a time, and writes out a file of event 
transactions at the  end of the session.

By Anthony Persico and Carter Cook

TO-DO:
    - make eventList into an OrderedDict
PROBLEMS:
    - haven't tried random input testing for functions
    
Program takes 3 arguments: 1) CurrentEventsFile.txt 2) EventTransactionFile.txt 3) a list of commands
EVENT TRANSACTION FORMAT:[2-digit transaction code] [20 character name] [event date, YYMMDD format] [# tickets in transaction]
EVENT LIST FORMAT:[20 character event name] [# tickets in transaction]
'''

#---------IMPORTS AND GLOBAL VARIABLES----------#
import sys #sys.argv used to read files in as arguments from the command line
import os.path #os.path.isfile used to verify existence of files before opening
import datetime #used later for fetching/comparing dates
logged = None #'admin' or 'sales'
eventTransaction = [] #list of all transaction codes created in session
eventList = [] #list of all events, including created in session



#----------COMMANDS----------#
def login(): #start a Front End session
    global logged, eventTransaction, eventList #import global variables for use in function
    if logged == None:
        if not os.path.isfile(sys.argv[1]): #if the file does not exist
            print "bad argument (1)"
            return 1 #fail
        filein = open(sys.argv[1], 'r') #open for reading
        eventList = filein.read().splitlines() #convert file to array of strings
        filein.close()
        print "Would you like to log in to a sales or admin session?"
        session = getInput() #wait for user input
        if session == "admin" or session == "sales":
            logged = session
            print 'Current Events:\n'+'\n'.join(eventList[:-1]) #print current events
            return 0 #success
    return 1 #failure

def logout(): #end a Front End session
    global logged, eventTransaction, eventList #import global variables
    if logged != None: #if user is logged in
        eventTransaction.append("00                      000000 00000") #add transaction code to array
        eventTransactionFile = '\n'.join(eventTransaction) #convert list to a string delimited by \n
        fileout = open(sys.argv[2], 'w+') #open for writing, create new if non-existent
        fileout.write(eventTransactionFile) #overwrite
        fileout.close()
        logged = None #no longer admin/sales
        eventTransaction = [] #clear arrays
        eventList = []
        return 0 #success
    return 1 #otherwise failure

def create(): #create and allocate tickets for a new event (privileged transaction)
    global logged, eventTransaction, eventList #import global variables
    if logged == "admin":
        print "What is the name of the event you wish to create?"
        eventName = getInput() #wait for user input
        if len(eventName) > 0 and len(eventName) < 21: #restrict invalid name lengths
            eventName = eventName.ljust(20) #left justify event name, pad with spaces
            if getTickets(eventName) == -1: #-1 implies event does not already exist
                print "What date will the event occur? (YYMMDD)"
                inputDate = getInput() #wait for user input
                try: #try to cast to date
                    eventDate = datetime.datetime.strptime(inputDate, "%y%m%d").date() #convert input into datetime.date object
                except: #if cast failed
                    return 1 #return failure
                today = datetime.date.today() #today's date
                twoYears = today + datetime.timedelta(2*365) #date 2 years from now
                if eventDate > today and eventDate < twoYears:
                    print "How many tickets would you like to have available for the event?"
                    try: #try to cast input to int
                        ticketCount = int(getInput()) #wait for user input
                    except: #if cast fails
                        return 1 #user did not input an integer
                    if ticketCount > 0 and ticketCount < 100000: #restrict invalid ticket amounts
                        event = "03 "+eventName+" "+inputDate+" "+str(ticketCount).rjust(5,"0") #convert to proper string format
                        eventTransaction.append(event) #add to master list
                        return 0 #success
    return 1 #otherwise failure

def add(): #add more tickets for an event (privileged transaction)
    global logged, eventTransaction, eventList #import global variables
    if logged == "admin":
        print "What is the name of the event you wish to add tickets to?"
        eventName = getInput() #wait for user input
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = getTickets(eventName)
            if tickets != -1: #-1 implies event does not exist
                print "How many tickets do you want to add?"
                try: #try to cast input to int
                    ticketCount = int(getInput()) #wait for user input
                except: #if user did not input an integer
                    return 1 
                if (ticketCount > 0 and ticketCount < 100000) and (ticketCount + tickets < 100000):
                    event = "04 "+eventName+" 000000 "+str(ticketCount).rjust(5,"0") #convert to proper string format
                    eventTransaction.append(event) #add to master list
                    return 0 #success
    return 1 #failure
                    
def delete(): #cancel tickets and delete an event (privileged transaction)
    global logged, eventTransaction, eventList #import global variables
    if logged == "admin":
        print "What is the name of the event you wish to delete?"
        eventName = getInput() #wait for user input
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = getTickets(eventName)
            if tickets != -1: #-1 implies event does not exist
                removeEvent(eventName)
                event = "05 "+eventName+" 000000 00000" #convert to proper string format
                eventTransaction.append(event) #add to master list
                return 0 #success
    return 1 #failure

def sell(): #sell tickets for an event
    global logged, eventTransaction, eventList #import global variables
    if logged != None:
        print "What is the name of the event you wish to buy tickets to?"
        eventName = getInput() #wait for user input
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = getTickets(eventName)
            if tickets != -1: #-1 implies event does not exist
                print "How many tickets do you want to buy?"
                if logged == "admin":
                    limit = 100000
                elif logged == "sales":
                    limit = 9
                try: #try to cast input to int
                    ticketCount = int(getInput()) #wait for user input
                except: #if user did not input an integer
                    return 1
                if ticketCount > 0 and ticketCount < limit and ticketCount <= tickets:
                    event = "01 "+eventName+" 000000 "+str(ticketCount).rjust(5,"0") #convert to proper string format
                    eventTransaction.append(event) #add to master list
                    return 0 #success
    return 1 #failure

def reTurn(): #return sold tickets for an event
    global logged, eventTransaction, eventList #import global variables
    if logged != None:
        print "What is the name of the event you wish to return tickets to?"
        eventName = getInput() #wait for user input
        if len(eventName) > 0 and len(eventName)< 21: #restrict invalid lengths
            eventName = eventName.ljust(20) #left justify name
            tickets = getTickets(eventName)
            if tickets != -1: #-1 implies event does not exist
                print "How many tickets do you want to return?"
                if logged == "admin":
                    limit = 100000
                elif logged == "sales":
                    limit = 9
                try: #try to cast input to int
                    ticketCount = int(getInput())
                except: #if user did not input an integer
                    return 1 
                if ticketCount > 0 and ticketCount < limit and (ticketCount + tickets < 100000):
                    event = "02 "+eventName+" 000000 "+str(ticketCount).rjust(5,"0") #convert to proper string format
                    eventTransaction.append(event) #add to master list
                    return 0 #success
    return 1 #failure



#----------HELPER FUNCTIONS----------#
def getTickets(eventName): #returns the number of tickets an event has, -1 if it doesn't exist
    global eventList #import eventList variable
    tickets = -1
    for line in eventList: #for all current events
        if line[0:20] == eventName: #if existing event has same name
            tickets = int(line[21:])
    return tickets

def getInput(): #just so that we can easily trace input for debugging
    line = sys.stdin.readline()
    if line == "": #serves as python's EOF
        exit() #exists if EOF fed into input
    return line.rstrip("\n")

def removeEvent(eventName):
    global eventList
    for i in range (0,len(eventList)): #for all current events
        if eventList[i][0:20] == eventName: #if existing event has same name
            if i == len(eventList)-1:
                eventList = eventList[:i]
            else:
                eventList = eventList[:i] + eventList[i+1:]



#----------MAIN----------#
def main(): #ask for commands, execute them, repeat
    global inputStack #import inputStack for use inside main
    args = len(sys.argv)-1 #number of arguments passed in via command line
    if args != 2: #currentEvents.txt and eventFile.txt
        print "2 arguments required"
        exit()
    commands = ["login", "logout", "create", "add", "delete", "sell", "return"] #list of possible user input
    functions = [login, logout, create, add, delete, sell, reTurn] #related functions
    print "'login' to begin a session."
    while True: #loop until exit
        userInput = getInput() #print '>' and wait for user input
        if userInput == "close":
            exit()
        identified = False
        for i in range(len(commands)):
            if userInput == commands[i]: #check if userInput matches each command
                identified = True
                complete = functions[i]() #run corresponding command
                if complete == 1: #if command threw an error
                    print "There was an input error with the "+commands[i]+" function, please try again."
        if not identified: #if command is unrecognised
            print "Unrecognised command."
main()
