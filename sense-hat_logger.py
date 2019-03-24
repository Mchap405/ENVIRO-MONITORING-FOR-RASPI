import os
import csv
import time
import datetime
import socket

from sense_hat import SenseHat
from timeit import default_timer as timer

#Globals
csv_folder_name = "csv_storage"

working_directory = os.getcwd()

folder_path = working_directory + "/" + csv_folder_name

sense = SenseHat()

logging_window_seconds = 60
logging_period_seconds = 10

def main():
    folder_operations()
    log_data()
    
    return

def log_data():
    ts = time.time()
    
    print('Beginning logging')
    
    with open(folder_path + '/' + socket.gethostname() + '_data_log_' + str(time.time()).replace('.', '-') + '.csv', mode = 'w') as csv_file:
        fieldnames = ['TimeStamp', 'Temperature',
                      'Barometric Pressure', 'Humidity']
        
        start_time = timer()
        
        writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
        writer.writeheader()
        
        while (timer() - start_time) < logging_window_seconds:
            writer.writerow({'TimeStamp':time.time(),
            'Temperature':sense.get_temperature(),
            'Barometric Pressure':sense.get_pressure(),
            'Humidity':sense.get_humidity()})
            
            time.sleep(logging_period_seconds)
                         
    print('Logging finished')
    csv_file.close()

    return

#Checks if the csv folder exists
#If not it creates a new one
def folder_operations():
    if check_directories_exist() == False:
        print("Current directory doesn't exist\nCreating a new directory")
        create_folder()

#Checks if the directory exists, returns true if it does
def check_directories_exist():
    return os.path.isdir(working_directory + "/" + csv_folder_name)

#Attempts to create a folder, shuts down if it cant
def create_folder():
    try:
        os.mkdir(folder_path)
        
    except OSError:
        print("Failed to create folder, shutting down")
        exit()

    else:
        print("Folder created")
    
        
if __name__ == "__main__":
    main()
