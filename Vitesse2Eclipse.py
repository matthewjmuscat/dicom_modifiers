
import os
import argparse
import time
import pydicom
import sys


def change_isotope(dicom_dir, sourceisotopename):
    for folder_entry in os.scandir(dicom_dir):
    
        if folder_entry.is_dir():
            print("Patient: ", folder_entry.name)
            # Iterate over subfolders in each folder
            for subfolder_entry in os.scandir(folder_entry.path):
                print("Plan: ", subfolder_entry.name)
                for subsubfolder_entry in os.scandir(subfolder_entry.path):
                    if subsubfolder_entry.is_dir() and subsubfolder_entry.name.lower() == 'default':
                        print("Defult folder found.")
                        default_folder_path = subsubfolder_entry.path
                        edited_folder_path = os.path.join(subfolder_entry.path, 'Edited for Eclipse Import')

                        # Create the "Edited for Eclipse Import" folder if it doesn't exist
                        if not os.path.exists(edited_folder_path):
                            os.mkdir(edited_folder_path)
                            print("New folder made at: ", edited_folder_path)
                        # Iterate over files in 'default' folder
                        print("Attempting DICOM Edits")
                        for file_name in os.listdir(default_folder_path):
                            if file_name.endswith(".dcm"):
                                file_path = os.path.join(default_folder_path, file_name)

                                try:
                                    ds = pydicom.dcmread(file_path)
                                except:
                                    print(f"Error reading {file_path}: {e}")
                                    continue
                                try:
                                    oldname = ds.SourceSequence[0].SourceIsotopeName
                                    ds.SourceSequence[0].SourceIsotopeName = sourceisotopename
                                    
                                    print("SourceIsotopeName changed from ", oldname, " to ", sourceisotopename, " in ", file_name)
                                except:
                                    pass
                                edited_file_path = os.path.join(edited_folder_path, file_name)
                                ds.save_as(edited_file_path)

    return


def main():
    # dicom_dir = input("Enter the path to the DICOM images folders directory: ") 
    dicom_dir = '@\\spvaimapsi\\SIHDR\\Vitesse DICOM Archive1\\'
    dicom_dir = '\\spvaimapsi\SIHDR\Vitesse DICOM Archive1'
    dicom_dir = "H:\CCSI\PlanningModule\Physics Patient QA\VitesseBackup\Vitesse DICOM Archive1"

    # dicom_dir = '\\spvaimapsi\SIHDR\Vitesse DICOM Archive1\Brash, Brian'
    # dicom_dir = 'H:\\CCSI\PlanningModule\\Brachy Projects\\3D Printed custom applicators\\Experiments'

    new_source = "GammaMed Plus HDR source 0.9 mm"
    change_isotope(dicom_dir, new_source)
    return

try:
    main()
    input()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    input("Press enter to exit.")

