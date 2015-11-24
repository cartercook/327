'''
The Back Office reads the Master Events File and the Merged Event Transaction File and applies all
transactions to the master events to produce the New Master Events File and the New Current Events
File. Events whose date has passed are removed from the Master Events File.

By Anthony Persico and Carter Cook

MASTER EVENTS FORMAT: [event date, YYMMDD format] [# tickets remaining] [20 character event name]
*events must be sorted by date
MERGED EVENTS FORMAT: [2-digit transaction code] [20 character name] [event date, YYMMDD format] [# tickets in transaction]
*00: end, 01: sell, 02: return, 03: create, 04: add, 05: delete
CURRENT EVENTS FORMAT: [20 character name] [# tickets available]
'''

#---------IMPORTS----------#
import re #regular expressions, for checking syntax of input files
import datetime #used later for fetching/comparing dates

#----------FUNCTIONS----------#
def checkMergedEventSyntax(mergedEvents):
	for line in mergedEvents:
		if not re.match(r'^[0-9]{2} .{20} [0-9]{6} [0-9]{5}\n?$', line): #[2-digit transaction code] [20 character name] [event date, YYMMDD format] [# tickets in transaction]
			logFatalError()

def deleteOldEvents(masterEvents): #delete events from masterEvents if their dates have passed
	for event in masterEvents:
		eventDate = getDate(event) #get the event's date
		today = datetime.date.today() #today's date
		if eventDate < today:
			masterEvents.remove(event)

def checkMasterEventSyntax(masterEvents):
	for line in masterEvents:
		if not re.match(r'^[0-9]{6} [0-9]{5} .{20}\n?$', line): #[event date, YYMMDD format] [# tickets remaining] [20 character event name]
			logFatalError()

def combine(mergedEvents, masterEvents): #update masterEvents using mergedEvents
	for event in mergedEvents:
		code = event[:2] #get mergedEvent transaction code
		if code == "00": #end
			continue #do not add these end-session codes to masterEvents
		elif code == "01": #sell
			name = event[3:23] 
			if alreadyExists(masterEvents, name):
				for i in range(0,len(masterEvents)):
					if masterEvents[i][13:33] == name
						index = i
				tickets = masterEvents[index][7:12]
				ticketsSold = event[31:]
				if (tickets - ticketsSold) > 0:
					tickets = str(tickets - ticketsSold).rjust(5,"0")
					masterEvents[index] = masterEvents[index][:7] + tickets + masterEvents[12:] 
		elif code == "02": #return
			name = event[3:23] 
			if alreadyExists(masterEvents, name):
				for i in range(0,len(masterEvents)):
					if masterEvents[i][13:33] == name
						index = i
				tickets = masterEvents[index][7:12]
				ticketsReturned = event[31:]
				if (tickets + ticketsReturned) < 100000:
					tickets = str(tickets + ticketsReturned).rjust(5,"0")
					masterEvents[index] = masterEvents[index][:7] + tickets + masterEvents[12:]
		elif code == "03": #create
			name = event[3:23] #get mergedEvent name
			if not alreadyExists(masterEvents, name): #else if the new event does not already exist in masterEvents
				event = MergedToMasterFormat(event) #convert it to the proper format
				masterEvents.append(event) #and add it to the masterEvents list
		elif code == "04": #add
			name = event[3:23] 
			if alreadyExists(masterEvents, name):
				for i in range(0,len(masterEvents)):
					if masterEvents[i][13:33] == name
						index = i
				tickets = masterEvents[index][7:12]
				ticketsAdded = event[31:]
				if (tickets + ticketsAdded) < 100000:
					tickets = str(tickets + ticketsAdded).rjust(5,"0")
					masterEvents[index] = masterEvents[index][:7] + tickets + masterEvents[12:]
		elif code == "05": #delete
			name = event[3:23] 
			if alreadyExists(masterEvents, name):
				for i in range(0,len(masterEvents)):
					if masterEvents[i][13:33] == name
						index = i
				masterEvents = masterEvents[:index] + masterEvents[index + 1:]

def createCurrentEvents(masterEvents): #drops the title and ticket count from masterEvents and returns it as a new array
	currentEvents = []
	for line in masterEvents:
		currentEvents.append(line[13:33] + line[6:12]) #[20 character name] [# tickets available]
	currentEvents.append("END                  00000") #line to signify end of currentEvents file
	return currentEvents

#----------HELPER FUNCTIONS----------#
def printArray(array): #one line per item
	print '\n'.join(array) + '\n'

def fileToArray(filename):
	fileIn = open(filename, 'r') #open for reading
	arrayOut = fileIn.read().splitlines() #convert file to array of strings
	fileIn.close()
	return arrayOut

def arrayToFile(array, filename):
	textOut = '\n'.join(array) #convert list to a string delimited by \n
	fileOut = open(filename, 'w+') #open for writing, create new if non-existent
	fileOut.write(textOut) #overwrite
	fileOut.close()

def logFatalError():
	pass
	#print "FATAL ERROR"
	#exit()

def alreadyExists(masterEvents, name): #true when name matches an event name in masterEvents
	exists = False #false until proven otherwise
	for event in masterEvents: #for all master events
		if event[13:33] == name: #if existing event has same name
			exists = True
	return exists

def MergedToMasterFormat(line): #convert a mergedEvent line format to a masterEvent one
	return line[24:36] + line[2:23]

def getDate(line): #returns the masterEvent's date as a date object
	try: #try to cast event time to date object
		eventDate = datetime.datetime.strptime(line[:6], "%y%m%d").date() #convert YYMMDD into datetime.date object
	except: #if cast failed
		logFatalError()
	return eventDate

#----------MAIN----------#
def main():
	masterEvents = fileToArray("masterEvents.txt")
	mergedEvents = fileToArray("mergedEventTransaction.txt")

	print "#---------INPUTS----------#"
	print "masterEvents:"
	printArray(masterEvents)
	print "mergedEvents:"
	printArray(mergedEvents)

	checkMasterEventSyntax(masterEvents) #log a Fatal Error in case of bad syntax
	deleteOldEvents(masterEvents) #remove events dated before today
	checkMergedEventSyntax(mergedEvents) #log a Fatal Error in case of bad syntax
	combine(mergedEvents, masterEvents) #update masterEvents using mergedEvents
	masterEvents.sort(key=lambda x: getDate(x)) #sort masterEvents by date
	currentEvents = createCurrentEvents(masterEvents) #make a new file out of masterEvents
	arrayToFile(masterEvents, "masterEvents.txt") #write masterEvents to file
	arrayToFile(currentEvents, "currentEvents.txt") # write current events to file

	print "#---------OUTPUTS----------#"
	print "masterEvents:"
	printArray(masterEvents)
	print "currentEvents:"
	printArray(currentEvents)

main()