import subprocess
import glob
import shutil

try:
    import firebase_admin
    import matplotlib.pyplot as plt
    import numpy as np
    from firebase_admin import credentials
    from firebase_admin import storage
    from firebase_admin import firestore
    

except ImportError as e:
    print(e.msg)
    print('Could not find library, attempting to install via pip')
    try:
        subprocess.call(['pip3', 'install', 'firebase_admin'])
        subprocess.call(['pip3', 'install', 'matplotlib'])
        subprocess.call(['pip3', 'install', 'numpy'])

        import firebase_admin
        import matplotlib.pyplot as plt
        import numpy as np
        from firebase_admin import credentials
        from firebase_admin import storage
        from firebase_admin import firestore

    except FileNotFoundError:
        print("Error: Pip3 path not correctly set up")
        print("Exiting")
        exit(1)

cred = credentials.Certificate('Resources/raspberry-pi-monitoring-firebase-adminsdk-9q3qx-b62c8051b4.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'raspberry-pi-monitoring.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

path = 'csv_storage/'

def main():
    menu()
    return

def list_folders():
    collections = db.collections()

    for collection in collections:
        print(collection.id)

    return

def list_all_files_in_folder():
    user_choice = input('What folder would you like to view the contents of?: ')

    collection = db.collection(user_choice)

    for document in collection.get():
        print(f'{document.id}')

    return

def delete_file():
    collections = db.collections()
    print('Collections: ')
    for collection in collections:
        print(f'\t{collection.id}')

    folder_choice = input('\nFrom which collection do you want to delete?: ')
    folder = db.collection(folder_choice)

    print('Documents:')
    for doc in folder.get():
        print(f'\t{doc.id}')

    file_choice = input('\nWhich file/s do you want to delete?: ')
    file_choice.split(' ')

    folder.document(file_choice).delete()
    blob = bucket.blob(folder_choice + '/' + file_choice)
    blob.delete()

    print('\nDeleted all files')

def download_all_files():
    list_of_folders = list()
    for collection in db.collections():
        list_of_folders.append(collection.id)

    for folder in list_of_folders:
        docs = db.collection(folder).get()
        for doc in docs:
            blob = bucket.blob(folder + '/' + doc.id)
            blob.download_to_filename('file.foo')
            shutil.move('file.foo', path + folder + '/' + doc.id)
        

    return

def get_average():
    while True:
        try:
            user_choice = int(input('\nWhich value would you like to generate the average of?:\n1. Temperature\n2. Barometric Pressure\n3. Humidity\n'))
            
            if user_choice <= 3 and user_choice >= 1:
                generate_average_from_files(user_choice)
                break

        except ValueError:
            print('Please enter a valid integer')

    return

def generate_average_from_files(index):
    recorded_units = ['Temperature', 'Barometric Pressure', 'Humidity']

    print(f'\n{recorded_units[index - 1]} Averages: ')
    overall_value_holder = float()
    overall_number_of_value_track = 0

    list_of_folders = glob.glob(path + '*')

    folder_map = dict()

    for csv_folders in list_of_folders:
        
        value_holder = float()
        number_of_value_track = 0

        list_of_csv_files = glob.glob(csv_folders + '\\*.csv')

        for each_file in list_of_csv_files:

            with open(each_file, 'r') as csv_file:
                data = csv_file.read().split()
                del[data[0]]
                del[data[0]]
                for line in data:
                    values = line.split(',')
                    value_holder += float(values[index])
                    number_of_value_track += 1
                    
        average = value_holder / number_of_value_track
        print('\t' + csv_folders.split('\\')[1] + f': {average}')
        
        folder_map[csv_folders.split('\\')[1]] = average
        
        overall_value_holder += value_holder
        overall_number_of_value_track += number_of_value_track
    
    overall_average = overall_value_holder / overall_number_of_value_track
    folder_map['Overall'] = overall_average
    print(f'\tOverall Average: {overall_average}')
    
    plot_averages(folder_map, recorded_units[index - 1])
    
def plot_averages(map_of_averages, unit):

    y_axis = [0, 100]
    dataNames = tuple(map_of_averages.keys())
    itemsToPlot = map_of_averages.values()

    plt.bar(y_axis, itemsToPlot, align='center', alpha=1)
    plt.xticks(y_axis, dataNames)

    plt.ylabel(unit)
    plt.xlabel("Devices")

    plt.title(f"Average {unit} across all devices")
    plt.show()
    return

def menu():
    while True:
        try:
            user_choice = int(input('\n1. List all Folders\n2. List all files within a folder\n3. Delete a file\n4. Download All Files\n5. Get Average of Values from All Files\n6. Exit\n'))
            
            if user_choice <= 6 and user_choice >= 1:
                if user_choice == 1:
                    list_folders()
                elif user_choice == 2:
                    list_all_files_in_folder()
                elif user_choice == 3:
                    delete_file()
                elif user_choice == 4:
                    download_all_files()
                elif user_choice == 5:
                    get_average()
                elif user_choice == 6:
                    print('Exiting')
                    exit(1)

        except ValueError:
            print('Please enter a valid integer')
        

if __name__ == "__main__":
    main()