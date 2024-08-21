import dicom_modifier_functions
import pydicom
from collections import defaultdict
import misc_tools

def modify_dicoms(num_dicoms,
                  patients_progress,
                  completed_progress,
                  dicom_paths_list,
                  session_output_dir,
                  standard_tags_to_change_dict,
                  important_info,
                  live_display
                  ):
    ### For loading bar (START)
    # Define descriptions
    patientUID_default = "Initializing"
    processing_patients_main_description = "[red]Modifying DICOMs [{}]...".format(patientUID_default)
    processing_patients_completed_main_description = "[green]Modifying DICOMs"
    # Initialize tasks
    processing_patients_task = patients_progress.add_task(processing_patients_main_description, total=num_dicoms)
    processing_patients_task_completed = completed_progress.add_task(processing_patients_completed_main_description, total=num_dicoms, visible=False)
    ### For loading bar (END)

    for dicom_path in dicom_paths_list:
        # Get DICOM file name
        dicom_filename = dicom_path.name

        ### For loading bar (START)
        processing_patients_main_description = "[red]Modifying DICOMs [{}]...".format(dicom_filename)
        patients_progress.update(processing_patients_task, description=processing_patients_main_description)
        ### For loading bar (END)

        # Modify the DICOM
        modified_dicom = dicom_modifier_functions.modify_standard_DicomTag(dicom_path, 
                standard_tags_to_change_dict, 
                important_info, 
                live_display)
        
        # Get patient ID
        patient_ID = modified_dicom[0x0010,0x0020].value
        
        # Save the DICOM to file
        sp_session_sp_patient_output_dir = session_output_dir.joinpath(str(patient_ID))
        sp_session_sp_patient_output_dir.mkdir(parents=False, exist_ok=True)
        output_file_path = sp_session_sp_patient_output_dir.joinpath(dicom_filename)
        modified_dicom.save_as(output_file_path)

        del modified_dicom

        # Advance loading bar
        patients_progress.update(processing_patients_task, advance=1)
        completed_progress.update(processing_patients_task_completed, advance=1)

    # Show/hide complete/incomplete loading bars
    patients_progress.update(processing_patients_task, visible=False)
    completed_progress.update(processing_patients_task_completed, visible=True)



def combine_structure_sets(num_dicoms,
                  patients_progress,
                  completed_progress,
                  dicom_paths_list,
                  session_output_dir,
                  structure_names_list,
                  transfer_structure_if_already_exists_in_target_bool,
                  important_info,
                  live_display
                  ):
    ### For loading bar (START)
    # Define descriptions
    patientUID_default = "Initializing"
    processing_patients_main_description = "[red]Determining RTSTRUCTS DICOMs [{}]...".format(patientUID_default)
    processing_patients_completed_main_description = "[green]Determining RTSTRUCTS DICOMs"
    # Initialize tasks
    processing_patients_task = patients_progress.add_task(processing_patients_main_description, total=num_dicoms)
    processing_patients_task_completed = completed_progress.add_task(processing_patients_completed_main_description, total=num_dicoms, visible=False)
    ### For loading bar (END)
    
    rtstruct_groups = defaultdict(list)

    for dicom_path in dicom_paths_list:

        ### For loading bar (START)
        processing_patients_main_description = "[red]Determining RTSTRUCTS DICOMs [{}]...".format(dicom_path.name)
        patients_progress.update(processing_patients_task, description=processing_patients_main_description)
        ### For loading bar (END)

        try:
            dicom_file = pydicom.dcmread(dicom_path, stop_before_pixels=True)
            if dicom_file.Modality == "RTSTRUCT":
                rtstruct_groups[dicom_file.PatientID].append(dicom_path)
        except Exception as e:
            print(f"Failed to read {dicom_path}: {e}")
    
        # Advance loading bar
        patients_progress.update(processing_patients_task, advance=1)
        completed_progress.update(processing_patients_task_completed, advance=1)

    # Show/hide complete/incomplete loading bars
    patients_progress.update(processing_patients_task, visible=False)
    completed_progress.update(processing_patients_task_completed, visible=True)



    ### For loading bar (START)
    # Define descriptions
    patientUID_default = "Initializing"
    processing_patients_main_description = "[red]Combining RTSTRUCTS DICOMs [{}]...".format(patientUID_default)
    processing_patients_completed_main_description = "[green]Combining RTSTRUCTS DICOMs"
    # Initialize tasks
    processing_patients_task = patients_progress.add_task(processing_patients_main_description, total=len(rtstruct_groups))
    processing_patients_task_completed = completed_progress.add_task(processing_patients_completed_main_description, total=len(rtstruct_groups), visible=False)
    ### For loading bar (END)

    for patient_id, sp_patient_rt_struct_paths in rtstruct_groups.items():

        ### For loading bar (START)
        processing_patients_main_description = "[red]Combining RTSTRUCTS DICOMs [{}]...".format(patient_id)
        patients_progress.update(processing_patients_task, description=processing_patients_main_description)
        ### For loading bar (END)


        list_of_dictionaries_of_source_target_combinations = misc_tools.create_combinations(sp_patient_rt_struct_paths)

        for source_target_dictionary in list_of_dictionaries_of_source_target_combinations:
            list_of_sources_paths = source_target_dictionary['Sources']
            target_path = source_target_dictionary['Target']
        
            combined_dicom = dicom_modifier_functions.combine_multiple_rtstructs_with_full_update(list_of_sources_paths, 
                                                                                                  target_path, 
                                                                                                  structure_names_list,
                                                                                                  transfer_structure_if_already_exists_in_target = transfer_structure_if_already_exists_in_target_bool)


            # Get DICOM file name
            target_dicom_filename = target_path.stem

            combined_dicom_filename = target_dicom_filename + '_combined.dcm'

        
        
            # Get patient ID
            patient_ID = combined_dicom[0x0010,0x0020].value
        
            # Save the DICOM to file
            sp_session_sp_patient_output_dir = session_output_dir.joinpath(str(patient_ID))
            sp_session_sp_patient_output_dir.mkdir(parents=False, exist_ok=True)
            output_file_path = sp_session_sp_patient_output_dir.joinpath(combined_dicom_filename)
            combined_dicom.save_as(output_file_path)

            del combined_dicom

        # Advance loading bar
        patients_progress.update(processing_patients_task, advance=1)
        completed_progress.update(processing_patients_task_completed, advance=1)

    # Show/hide complete/incomplete loading bars
    patients_progress.update(processing_patients_task, visible=False)
    completed_progress.update(processing_patients_task_completed, visible=True)