# Simple template for controlling GPS-X from a Python interpreter
# This script is launched from GPS-X
# GPS-X copyright 2020 Hydromantis
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import csv
############################USER INPUTS############################
CommInt = 0.05
StopTime = 60.0
Bodlt = 25
Bodut = 50 
Bodp = 0.7
Codut = 250
Codlt = 125
Codp = 0.75

bodi = ["BOD1"]
codi = ["COD1"] 
bod = ["BOD31"]
cod = ["COD31"]
c_bod = ["c_bod"]
c_cod = ["c_cod"]
compliance_bod = ["Compliance BOD"]
compliance_cod = ["Compliance COD"]
ts = ["TIME"]
#c = ["c"]
###################################################################

#############################FUNCTIONS#############################

# start() function executed once at simulation start
#
def start():
    global CommInt, StopTime
    try:
        gpsx.setTstop(StopTime)
        gpsx.setCint(CommInt)
    except Exception as e:
        print(e)

# cint() function executed at every communication interval
#
def cint():
    global bod,cod,c_bod,c_cod,ts,bodi,codi,compliance
    try:
        #store the time
        a = round(gpsx.getValue("t"),2)
        ts.append(a)
        #store bod and cod
        bod.append(gpsx.getValue("bod31"))
        cod.append(gpsx.getValue("cod31"))
        bodi.append(gpsx.getValue("bod1"))
        codi.append(gpsx.getValue("cod1"))

        #calculate c value for bod and cod
        c_bod.append(min(Bodut-gpsx.getValue("bod31"), max(Bodlt - gpsx.getValue("bod31"), Bodp*gpsx.getValue("bod1")-gpsx.getValue("bod1")+gpsx.getValue("bod31"))))
        c_cod.append(min(Codut-gpsx.getValue("cod31"), max(Codlt - gpsx.getValue("cod31"), Codp*gpsx.getValue("cod1")-gpsx.getValue("cod1")+gpsx.getValue("cod31"))))
        #MCL failure or LUT failure
        if (Bodlt - gpsx.getValue("bod31")<0) and (Bodut - gpsx.getValue("bod31")>0) and (((gpsx.getValue("bod1")-gpsx.getValue("bod31"))/gpsx.getValue("bod1"))<0.7):
          return compliance_bod.append("LUT failure")
        elif (Bodut - gpsx.getValue("bod31")<0) and (((gpsx.getValue("bod1")-gpsx.getValue("bod31"))/gpsx.getValue("bod1"))<0.7):
          return compliance_bod.append ("MCL failure")
        else:
          return compliance_bod.append ("Compliant")
          
        if (Codlt - gpsx.getValue("cod31")<0) and (Codut - gpsx.getValue("cod31")>0) and (((gpsx.getValue("cod1")-gpsx.getValue("cod31"))/gpsx.getValue("cod1"))<0.7):
          return compliance_cod.append("LUT failure")
        elif (Codut - gpsx.getValue("cod31")<0) and (((gpsx.getValue("cod1")-gpsx.getValue("cod31"))/gpsx.getValue("cod1"))<0.7):
          return compliance_cod.append ("MCL failure")
        else:
          return compliance_cod.append ("Compliant")
        
    except Exception as e:
        print(e)

# eor() function executed once at end of simulation
# finished set True is required to terminate the runSim() function
#
def eor():
    global finished
    finished = True
    try:
        pass
    except Exception as e:
        print(e)

# runSim() call starts simulation in GPS-X
try:
    #reset all the values to the base value
    gpsx.resetAllValues()
    #run the simulation
    runSim()
    #print values of bod and cod
    print(bodi)
    print(codi)
    print(ts)
    print(bod)
    print(cod)
    #print(c)

    fields=["TIME","BOD31","COD31","BOD1","COD1","c_bod","c_cod"]
    rows= [ts,bod,cod,bodi,codi,bod_c,cod_c]
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        #writer.writerow(fields)
        writer.writerows(rows)
    
  

except Exception as e:
 print(e)
###################################################################

