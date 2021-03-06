#!/usr/bin/env ipython

#Code assumes that the raw csv data (extracted sheet by sheet for each mouse: abcdefgh) is titled like: C2Q175P1_7a.csv where '7' refers to the trial day and 'a' is the specific mouse

#to use this code, replace FILE with 'C2Q175P1_7a' (or respective file name)

##PARSE TIME & DATE##
#define replace_all function
def replace_all(text, dic): #enter text and dictionary of replacements into function
    for i, j in dic.iteritems(): #for each entry i:I, j:J in dic,
        text = text.replace(i, j) #replace former with latter in text
    return text
#define parse_data function
def parse_data(FILE): #separate time and date, correct header
    f1 = open("" + FILE + ".csv").read() #opens original csv file as string 'f1'
    f2 = open("parsed_ " + FILE + ".csv", "w") #creates new file to write the parsed data to via file object 'f2'
						#new file will read: parsed_FILE.csv
    reps = {' ':',', '/':'_', 'RealTime':'Date', 'Event':'Realtime'} #dictionary of desired replacements
	    #entry 0: split date and time; replace the space with comma delimiter
	    #entry 1: replace / in date with _
	    #entries 2,3: adjust column headers
    f1parsed = replace_all(f1, reps) #creates string with edited f1 data
    f2.write(f1parsed) #writes parsed data to file stored in f2
    f2.close() #closes file object
    print ('Parsed data has been written to new file.')

##FILTER TEMPERATURE DATA##
#in column 10 (K), if the difference between numerical lines is less than -0.3 or greater than 0.3, remove line
def filter_temp(FILE): #UPDATE SAVED TO RELEVENT VALUE# #remove temperature readings outside threshold deviation
    f2 = open("parsed_" + FILE + ".csv") #open newly parsed data#
    f3 = open("filtered_parsed_" + FILE + ".csv", "w") #open new file for filtered data#
    f3.write("ElapsedTime,Date,Realtime, , ,I1Num,I1RR-I,I1RR-I(SD),I1HR,I1HR(SD),I2T_Mean,I2T_Mean(SD),I3A_TA,I3A_TA(SD)\r\n") #adds corrected header
    saved = 36.23 #whatever first value in row is; update to each next good value
    f2.readline() #skip first line in f2
    for line in f2: #iterate line by line
        fields = line.split(",") #define fields as comma delimited
        if abs(float(fields[10]) - saved) > 0.30: #if the difference from row_n to row_m is > 0.3, mark row_m as outlier and do not extract data
            f3.write(fields[0]) #extract 'elapsed time' data
            f3.write(",") #set up next field
            f3.write(fields[1]) #extract 'date' data
            f3.write(",") #set up next field
            f3.write(fields[2]) #extract 'real time' data
            f3.write(",,,,,,,,,,,,,") #write blank fields for rest of line
            f3.write('\n') #create new line for next set of data
        else:
            f3.write(line) #for lines with accurate temp readings, extract all data
        saved = float(fields[10]) #update 'saved' value to last non-outlier body temp for each new line
    f2.close() #close file objects
    f3.close()
    print ('Data with filtered body temp has been extraced to new file.') #when done, print completion statement

##CONDITIONAL: EXTRACT ACTIVE/REST DATA##
#active HR:
def activeHR(FILE): #extract data for activity between 3 and 4 units
    f3 = open("filtered_parsed_" + FILE + ".csv") #open filtered data file
    f3.readline() #skip header
    f4 = open("activeHR_" + FILE + ".csv", "w") #open new file for active telemetry data
    f4.write("ElapsedTime,Date,Realtime, , ,I1Num,I1RR-I,I1RR-I(SD),I1HR,I1HR(SD),I2T_Mean,I2T_Mean(SD),I3A_TA,I3A_TA(SD)\r\n") #write in header
    for line in f3: #iterate over filtered data
        fields = line.split(",") #set comma delimiter
        try:
            if float(fields[12]) >= 3 and float(fields[12]) <= 4 #if activity data measures between 3 and 4 units, extract all data in line
                f4.write(line)
            else: #otherwise, extract "time holder fields:" [0]elapsed time, [1]date, and [1]realtime markers and blank row
                f4.write(fields[0]) #extract elapsed time
                f4.write(",") #set up new field
                f4.write(fields[1]) #extract date
                f4.write(",") #set up new field
                f4.write(fields[2]) #extract real time
                f4.write(",,,,,,,,,,,,,") #write blank fields for rest of row
                f4.write('\n') #start next iteration on a new line
        except ValueError, e: #when iteration hits blank field from temperature filtering, ignore the error; write time holder fields and continue iteration
            f4.write(fields[0]) #extract elapsed time
            f4.write(",") #set up new field
            f4.write(fields[1]) #extract date
            f4.write(",") #set up new field
            f4.write(fields[2]) #extract real time
            f4.write(",,,,,,,,,,,,,") #write blank fields for rest of row
            f4.write('\n') #start next iteration on a new line
            continue
    f3.close() #close file objects
    f4.close()
    print ('Active telemetry data has been extracted.') #when done, print completion statement
	
#resting HR: 
#resting HR: 
def restHR(FILE): #extract lines with activity = 0 after 1 full minute of rest
    f3 = open("filtered_parsed_" + FILE + ".csv") #open filtered data
    f3.readline() #skip header in for_loop
    f5 = open("restHR_" + FILE + ".csv", "w") #open new file for extracted 'resting' data
    f5.write("ElapsedTime,Date,Realtime, , ,I1Num,I1RR-I,I1RR-I(SD),I1HR,I1HR(SD),I2T_Mean,I2T_Mean(SD),I3A_TA,I3A_TA(SD)\r\n") #insert header into new file
    counts = 0 #set up counter; set counter to 0
    for line in f3: #iterate line by line
        fields = line.split(",") #define field delimiter as comma
        try:
            if float(fields[12]) == 0: #if mouse has no activity, add to counts
                counts = counts + 1 
            else: #if there is activity, reset counter to 0
                counts == 0 
            if counts >= 3 and float(fields[12]) == 0: #if activity is 0 after at least one full minute of rest, extract line
                f5.write(line)
            else: #extract time place-holder data and write blank fields
                f5.write(fields[0])
                f5.write(",")
                f5.write(fields[1])
                f5.write(",")
                f5.write(fields[2])
                f5.write(",,,,,,,,,,,,,")
                f5.write('\n')
        except ValueError, e: #when iteration hits blank field from temperature filtering, ignore the error; write time place-holder fields and continue iteration
            f5.write(fields[0])
            f5.write(",")
            f5.write(fields[1])
            f5.write(",")
            f5.write(fields[2])
            f5.write(",,,,,,,,,,,,,")
            f5.write('\n')
            continue
    f3.close() #close files
    f5.close()
    print ('Resting telemetry data has been extracted.') #when done, print completion statement

