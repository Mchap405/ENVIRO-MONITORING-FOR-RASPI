import subprocess
import glob
import os
import time

from shutil import copyfile
from multiprocessing import Process

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import storage
    from firebase_admin import firestore

except ImportError as e:
    print(e.msg)
    print('Could not find library, attempting to install via pip')
    try:
        subprocess.call(['pip3', 'install', 'firebase_admin'])

    except FileNotFoundError:
        print("Error: Pip3 path not correctly set up")
        print("Exiting")
        exit(1)

    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import storage

cred = credentials.Certificate('Resources/raspberry-pi-monitoring-firebase-adminsdk-9q3qx-b62c8051b4.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'raspberry-pi-monitoring.appspot.com'
})

bucket = storage.bucket()
db = firestore.client()

#GLOBALS----------------------------
csv_storage_path = "csv_storage/"
#-----------------------------------

def upload_blob(source_file_name, destination_blob_name):
    
    doc_ref = db.collection(destination_blob_name).document(source_file_name)
    blob = bucket.blob(destination_blob_name + '/' + source_file_name)

    blob.upload_from_filename(source_file_name)
    doc_ref.set({})

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

def get_list_of_file_names(folder_path):
    
    list_of_files = list()
    for items in glob.glob(csv_storage_path + '*.csv'):
        list_of_files.append(items.split('/')[1])

    return list_of_files

def remove_file(filename):
    os.remove(filename)
    os.remove(csv_storage_path + filename)

def main():
    
    list_of_file_names = get_list_of_file_names(csv_storage_path)

    for filename in list_of_file_names:
        copyfile(csv_storage_path + filename, filename)
        folder = filename.split('_')[0]
        upload_blob(filename, folder)
        remove_file(filename)

    return

if __name__ == "__main__":
    main()
