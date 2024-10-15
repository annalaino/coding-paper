# Simple template for controlling GPS-X from a Python interpreter
# This script is launched from GPS-X
# GPS-X copyright 2022 Hatch

import random
import os
import pandas as pd
import pickle
#from queue import Queue
from datetime import datetime as dt
from datetime import timedelta as time_delta

global output_df, rain_events, base_concentrations, start_dt
global monte_carlo_sim, base_report_path, RainInflow

# simulation information
number_of_monte_carlo = 1000
CommInt = 0.05
StopTime = 60.0
RainInflow = [0, 10]


def profile_variables():
    """
    Returns a dictionary containing the variables that profiles will be obtained for
    """
    profile_variables = {
        'bod1': 'BOD influent',
        'cod1': 'COD influent',
        'bod31': 'BOD effluent',
        'cod31': 'COD effluent',
        'rainfall72': 'Rain'
    }    
    print("profile variables")
    return profile_variables
    
#def single_observation_variables():
    """
    Returns a dictionary of variables to be collected only once at the end of the simulation
    """
#    single_variables = {
#        'codconclimitfinaleff': 'Effluent COD Constraint',
#        'codtimeviolatedfinaleff': 'Total Time Violating COD Constraint',
#        'codptimeviolatedfinaleff': 'Percent of Time Violating COD Constraint',
#        'bodconclimitfinaleff': 'Effluent BOD Constraint',
#        'bodtimeviolatedfinaleff': 'Total Time Violating BOD Constraint',
#        'bodptimeviolatedfinaleff': 'Percent of Time Violating BOD Constraint',
#        'rainEvents': 'Number of rain events experienced'
#        }
#    print("single_variables")
#    return single_variables

# Randomly assign rain fall values
def rain_fall():
    """
    Function returns a random value indicating rainfall occurring in the WWTP catchment
    """
    global RainInflow
    if round(gpsx.getValue("t"), 2) < 23:
            gpsx.setValue("rainfall72", RainInflow[0])
    elif round(gpsx.getValue("t"), 2) > 28:
            gpsx.setValue("rainfall72", RainInflow[0])
    else:
            gpsx.setValue("rainfall72", RainInflow[1])
    
    print("rain")

def build_profile_df():
    """
    Builds an empty dataframe where results of the GPS-X simulation are stored
    """
    df = pd.DataFrame()
    for var in profile_variables():
        df[var] = None
        print("build_profile")
    return df


def build_single_observation_df():
    """
    Builds an empty dataframe where end of simulation results of the GPS-X simulation are stored
    """
    df = pd.DataFrame()
    for var in single_observation_variables():
        df[var] = None
        print("single_obs")
    return df


def collect_outputs(df, index_type):
    """
    Gets the value of simulation outputs to be observed in the GPS-X simulation
    
    df (dataframe): Dataframe where observed values will be stored
    index_type (str): datetime -> use a datetime index
                      monte_carlo -> use current monte carlo iteration as an index
    """
    results = []

    for variable in df.columns:
        results.append(get_simulation_value(variable))
    
    if index_type == 'datetime':
        df.loc[get_sim_dt(), :] = results
    elif index_type == 'monte_carlo':
        df.loc[monte_carlo_sim, :] = results
    else:  # if not one of the specified index types, have an incrementing index
        df.loc[len(df.index), :] = results
    print("collect_outputs")

def get_simulation_value(variable):
    """
    Gets the current value of a parameter in the GPS-X simulation
    """
    if '(' in variable:
        cryptic, index = variable.split('(')
        index = int(index[:-1])
        value = gpsx.getValueAtIndex(cryptic, index)
    else:
        value = gpsx.getValue(variable)
    print("get_sim_Value")
    return value


def set_default_sim_parameters():
    """
    Sets the default GPS-X simulation parameters
    """
    gpsx.resetSim()
    gpsx.resetAllValues()
    gpsx.setCint(CommInt)
    gpsx.setTstop(StopTime)
    gpsx.setSteady(True)
    #gpsx.setValue('truckNumber', 0)
    #gpsx.setValue('rainEvents', 0)


def set_start_dt(start_dt):
    """
    Sets the simulation start time values in GPS-X
    """
    gpsx.setValueAtIndex('ztime', 1, start_dt.year)
    gpsx.setValueAtIndex('ztime', 2, start_dt.month)
    gpsx.setValueAtIndex('ztime', 3, start_dt.day)
    gpsx.setValueAtIndex('ztime', 4, start_dt.hour)
    gpsx.setValueAtIndex('ztime', 5, start_dt.minute)
    gpsx.setValueAtIndex('ztime', 6, start_dt.second)


def get_sim_dt():
    """
    Returns the current datetime for the simulation
    """
    if gpsx.getValue('t') != 0:
        year = int(gpsx.getValue('iyear'))
        month = int(gpsx.getValue('imonth'))
        day = int(gpsx.getValue('iday'))
        hour = int(gpsx.getValue('ihour'))
        minute = int(gpsx.getValue('iminute'))
        second = int(gpsx.getValue('isec'))

        current_time = dt(year, month, day, hour, minute, second)
    else:
        current_time = start_dt

    return current_time


def get_elapsed_time():
    """
    Returns the elapsed simulation time in seconds
    """
    elapsed_seconds = gpsx.getValue('t')

    return elapsed_seconds


def start():
    try:
        global RainInflow
        # choose random number between 0 and 20 with uniform distribution
        RainInflow[1] = random.uniform(0, 10)
        print("start")
    except Exception as e:
        print(e)


# cint() function executed at every communication interval
def cint():
    try:
        collect_outputs(output_df, 'datetime')
        rain_fall()
    except Exception as e:
        print(e)

# eor() function executed once at end of simulation
# finished set True is required to terminate the runSim() function
def eor():
    global finished
    #finished = True
    #try:
    #    pass
    #except Exception as e:
    #    print(e)

# runSim() call starts simulation in GPS-X
#try:
    #reset all the values to the base value
    #gpsx.resetAllValues()
    #run the simulation
    #runSim()
    
 
    #global finished
    #print("eor")
    #single_observation_df = build_single_observation_df()
    #collect_outputs(single_observation_df, 'monte_carlo')
    
    # Serialize simulation results for use later
    with open(os.path.join(report_path, 'profile_run_{}.pkl'.format(monte_carlo_sim)), 'wb') as f:
        f.write(pickle.dumps(output_df))
    
#    with open(os.path.join(report_path, 'single_observation_run_{}.pkl'.format(monte_carlo_sim)), 'wb') as f:
        #f.write(pickle.dumps(single_observation_df))

    finished = True

    try:
        pass
    except Exception as e:
        print(e)
        base_path = os.getcwd()


# Base simulations
#clarifier_surface_area = 25  # assume plant clarifiers have a 25 m2 surface area
#aeration_volume = 900  # Assume aeration of 900 m3
report_path = os.path.join(os.getcwd(), 'base_results')  # path where pickled files will be stored

for monte_carlo_sim in range(1, number_of_monte_carlo + 1):
    print("Sim: ", monte_carlo_sim)
    output_df = build_profile_df()  # Start a fresh collection of profiles
    #sludge_trucks = Queue() # Create a new sludge truck queue
    rain_events = {}  # Create a new rain event tracking dictionary
    
    set_default_sim_parameters()
    start_dt = dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    set_start_dt(start_dt)
    runSim()


# Large plant simulations
#aeration_volume = 1200  # Assume aeration of 1200 m3
#clarifier_surface_area = 35  # assume plant clarifiers have a 35 m2 surface area
#report_path = os.path.join(os.getcwd(), 'updated_results')  # path where pickled files will be stored

#for monte_carlo_sim in range(1, number_of_monte_carlo + 1):#
 #   output_df = build_profile_df()  # Start a fresh collection of profiles
  #  sludge_trucks = Queue() # Create a new sludge truck queue
  #  rain_events = {}  # Create a new rain event tracking dictionary
  #  
  #  set_default_sim_parameters()
  #  start_dt = dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
  #  set_start_dt(start_dt)
  #  runSim()
