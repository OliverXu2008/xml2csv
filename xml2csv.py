import time
import os
import datetime
import glob
import re
from xml.etree import ElementTree as et

# define the variables for the name/value pair list
name_list = []
value_list = []
name_value_dict = {}

# define the indicator on whether set "Action Date" as the current timestamp
set_action_date_as_current = 1

#  Prompt the end-user that this tool is going to be run:
print '---------------------- Welcome to use xml2csv ---------------------------'
print 'Author:      Oliver Xu'
print 'Version:     2.0'
print 'Last Update: 2016.07.05\n'
print 'This tool would generate the CSV for DP Portal based on XML file.\n'
print 'In version 2, it is enhanced to support UpdateData-Reschedule.\n'

closeInput = raw_input("Press ENTER to Start")

#  Obtain the input from keyboard for PWO, CWO
print '-------------------------------------------------------------------------'
print 'Please input the PWO and CWO for the DP Portal'
print 'Press \"ENTER\" to use the PWO and CWO in the xml file'

user_PWO = raw_input("Parent Work Order: (e.g. WOR100000183111) ")
user_CWO = raw_input("Child Work Order:  (e.g. WOR100000183223) ")

'''
print 'User_PWO: ' + user_PWO
print 'User_CWO: ' + user_CWO

if user_PWO == '':
    print 'Use the PWO from the xml.'

if user_CWO == '':
    print 'Use the CWO from the xml.'
'''
    
# defeine the pattern to match the work order WOR100000183111
pattern = re.compile('WOR\d{12}$') 

if re.match(pattern,user_PWO) != None:
    print 'Use the PWO from user input: ' + user_PWO
else:
    user_PWO = ''

if re.match(pattern,user_CWO) != None:
    print 'Use the CWO from user input: ' + user_CWO
else:
    user_CWO = ''
    

    
# Using system time to set the Action_Date
current_Time = datetime.datetime.now()
year = current_Time.year
mon  = current_Time.month
day  = current_Time.day
hour = current_Time.hour
min  = current_Time.minute

def Local2UTC(LocalTime):
    EpochSecond = time.mktime(LocalTime.timetuple())
    utcTime = datetime.datetime.utcfromtimestamp(EpochSecond)
    return utcTime

LocalTime = current_Time
UTCTime= Local2UTC(LocalTime)

TZ = LocalTime.hour - UTCTime.hour
if TZ < 0:
    TZ = TZ + 24
TZ = str(TZ)

if mon < 10:
    mon = '0' + str(mon)
    
if day < 10:
    day = '0' + str(day)

if hour <10:
    hour = '0' + str(hour)

if min <10:
    min = '0' + str(min)

# set the Action_Date to the format: "2016-03-22T09:15:00+11:00"
Action_Date = str(year) + '-' + str(mon) + '-' + str(day) + 'T' + str(hour) + ':' + str(min) + ':00+' + TZ + ':00'

print '------------------------ Processing -------------------------------------'
print ''
xml_file_list = glob.glob("./*.xml")
for xml_file in xml_file_list:
    # initialize the name_list and value_list
    name_list = []
    value_list = []
    name_value_dict = {}
    
    #print xml_file, 
    # e.g.  ".\03.xml", to remove the leading ".\"
    # so that the file name is changed to "03.xml"
    input_file = xml_file.replace(".\\" , "")
    if input_file.endswith('.xml'):
        input_file = input_file[:-4]
    
    # define output_File  "~03.csv"
    csv_file = "~" + input_file + '.csv'
    
    # parse the xml file
    tree = et.parse(xml_file)

    # get the spec
    if tree.find('FieldWork/FieldWorkSpecifiedBy/ID') != None:
        spec = tree.find('FieldWork/FieldWorkSpecifiedBy/ID').text
    else:
        spec = ''
        
    # get the spec_Version
    if tree.find('FieldWork/FieldWorkSpecifiedBy/version') != None:
        spec_Version = tree.find('FieldWork/FieldWorkSpecifiedBy/version').text
    else:
        spec_Version = ''
        
    # get the activity_Type
    if tree.find('FieldWork/HasStatusSnapshot/SnapshotOfCurrentStatus/ActivityStatusInfo/ActivityInstantiatedBy/ID') != None:
        activity_Type = tree.find('FieldWork/HasStatusSnapshot/SnapshotOfCurrentStatus/ActivityStatusInfo/ActivityInstantiatedBy/ID').text
    else:
        activity_Type = ''
        
    # Set the Parent Word Order, if user_PWO is provided with valid format, PWO is set as user_PWO. otherwise use the PWO from xml.
    if user_PWO != '':
        PWO = user_PWO
    elif tree.find('FieldWork/ID') != None:
            PWO = tree.find('FieldWork/ID').text
    else:
        PWO = ''

    # Set the Child Work Order 
    # if xml file doesn't include CWO, then no need to set it
    # if xml file does include CWO, then
    #     if user_CWO is provided correctly, use the user_CWO as child work order
    #     otherwise, use the CWO from the xml file.
    if tree.find('FieldWork/HasStatusSnapshot/SnapshotOfCurrentStatus/ActivityStatusInfo/ID') == None:
        CWO = ''        
    elif user_CWO != '':
        CWO = user_CWO
    else:
        CWO = tree.find('FieldWork/HasStatusSnapshot/SnapshotOfCurrentStatus/ActivityStatusInfo/ID').text

    # get the StateID
    if tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/stateId') != None:
        StateID = tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/stateId').text                              
    else:
        StateID = ''
    
    # get the StepID
    if tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/stepId') != None:
        StepID = tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/stepId').text
    else:
        StepID = ''

    # get the ActionID
    if tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/actionId') != None:
        ActionID = tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/actionId').text
    else:
        ActionID = ''
    
    # get all the name/value pair list from InputData
    #  or
    # get all the name/value pair list from UpdateData (this is only for DataUpdate e.g. TCD update)

    if tree.find('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/InputData/DescribedBy/Characteristic/ID') !=None:
        # get the name
        for elem in tree.iterfind('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/InputData/DescribedBy/Characteristic/ID'):
            name_list.append(elem.text)
        # get the value
        for elem in tree.iterfind('FieldWork/FieldWorkHasChanges/ActivityChangeEntry/InputData/DescribedBy/value'):
            value_list.append(elem.text)

    elif tree.find('FieldWork/FieldWorkHasChanges/UpdateData/DescribedBy/Characteristic/ID') !=None:
        # get the name
        for elem in tree.iterfind('FieldWork/FieldWorkHasChanges/UpdateData/DescribedBy/Characteristic/ID'):
            name_list.append(elem.text)
        # get the value
        for elem in tree.iterfind('FieldWork/FieldWorkHasChanges/UpdateData/DescribedBy/value'):
            value_list.append(elem.text)

    
    
    # Map two lists into a dictionary
    name_value_dict = dict(zip(name_list, value_list))

    # set the Action Date to current timestamp according to the indicator
    if set_action_date_as_current == 1:
        name_value_dict['Action Date'] = Action_Date  

    #                          
    line1 = 'WorkOrderID,WorkOrderSpecificationType,WorkOrderSpecificationVersion,ActivityID,ActivityType,StateID,StepID,ActionID'

    #
    line2 = PWO + ',' + spec + ',' + spec_Version + ',' + CWO + ',' + activity_Type + ',' + StateID + ',' + StepID + ',' + ActionID 
    
    #o = open(csv_file,"w")
    #o.write(line1)
    #o.write('\n')
    #o.write(line2)
    #o.close()   
    print csv_file
    #print name_value_dict

    # get the number of the name_value pair 
    num_name_value = len(name_value_dict)
    #print num_name_value

    n = 1
    FieldName = 'FieldName'
    FieldValue = 'FieldValue'
    for key in name_value_dict:
        line1 = line1 + ',' +  FieldName+str(n) + ',' + FieldValue+str(n)
        line2 = line2 + ',' + key + ',' + name_value_dict[key]
        n = n + 1
    
    o = open(csv_file,"w")
    o.write(line1)
    o.write('\n')
    o.write(line2)
    o.close() 
    
    # Below print are only for debugging!
    #print 'Parent Work Order updated to: ' + PWO
    #print 'Child  Work Order updated to: ' + CWO
    #print 'Action Date updated to:' + Action_Date
    #print ''  

print ''
print '-------------------------------------------------------------------------'
print 'Parent Work Order updated to: ' + PWO
print 'Child  Work Order updated to: ' + CWO
print 'Action Date updated to:' + Action_Date
closeInput = raw_input("Press ENTER to exit")
print "Closing...\n"
