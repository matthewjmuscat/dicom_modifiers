### IMPORT PACKAGES (START)

# Generic
import time
import sys
import pathlib
from datetime import date, datetime
from stopwatch import Stopwatch
import warnings

# UI packages
import rich_preambles
from rich.live import Live

# Custom
import misc_tools
import dicom_modifer_functions

### IMPORT PACKAGES (END)



########### main() (START)

def main():
    ### Define variables

    ### Define the dictionary that defines the dicom tags to change and what the new values should be
    ## IMPORTANT: For this below dict, make sure these are all tags that are part of the standard dicom library!
    ## IMPORTANT: Make sure that the new value to be set is of the correct datatype! - Example: SeriesDescription has value representation LO, therefore new value must be string!
    # Can use either tuple of literal hexidecimals or tag keyword as string - Example: 'SeriesDescription' or  
    standard_tags_to_change_dict = {(0x0008,0x103E): 'PELVIS',
                                }

    ### Timing vars
    algo_global_start = time.time()
    stopwatch = Stopwatch(1)

    ### Directory names
    data_folder_name = 'Data'
    input_data_folder_name = "Input data"
    output_folder_name = "Output data"
    unused_folder_name = "Unused data"


    ### Textual parameters/options
    spinner_type = 'point' # other decent ones are 'point' and 'line' or 'line2'


    ### Initialize textual output
    progress_group_info_list = rich_preambles.get_progress_all(spinner_type)
    completed_progress, patients_progress, structures_progress, biopsies_progress, MC_trial_progress, indeterminate_progress_main, indeterminate_progress_sub, progress_group = progress_group_info_list

    rich_layout = rich_preambles.make_layout()

    important_info = rich_preambles.info_output()
    app_header = rich_preambles.Header()
    app_footer = rich_preambles.Footer(algo_global_start, stopwatch)

    layout_groups = (app_header,progress_group_info_list,important_info,app_footer)
    
    warnings.simplefilter('ignore')
            
    with Live(rich_layout, refresh_per_second = 8, screen = True) as live_display:
        rich_layout["header"].update(app_header)
        rich_layout["main-left"].update(progress_group)
        #rich_layout["box2"].update(Panel(make_syntax(), border_style="green"))
        rich_layout["main-right"].update(important_info)
        rich_layout["footer"].update(app_footer)
        
        ###### Indeterminate task preliminaries (START)
        task_main_indeterminate = indeterminate_progress_main.add_task('[red]Performing preliminaries...', total=None)
        task_main_indeterminate_completed = completed_progress.add_task('[green]Performing preliminaries...', total=None, visible = False)
        ######


        ### Create directories if not already present
        data_dir = pathlib.Path(__file__).parents[0].joinpath(data_folder_name)
        input_dir = data_dir.joinpath(input_data_folder_name)
        output_dir = data_dir.joinpath(output_folder_name)
        unused_dir = data_dir.joinpath(unused_folder_name)
        misc_tools.checkdirs(live_display, 
                             important_info, 
                             data_dir,
                             input_dir,
                             output_dir,
                             unused_dir)

        ### Create specific output directory for this particular session
        date_time_now = datetime.now()
        date_time_now_file_name_format = date_time_now.strftime(" Date-%b-%d-%Y Time-%H,%M,%S")
        session_output_dir_name = 'Session - '+date_time_now_file_name_format
        session_output_dir = output_dir.joinpath(session_output_dir_name)
        session_output_dir.mkdir(parents=False, exist_ok=True)

        ### Get all dicom file paths
        # Tell user where the data is being read from
        important_info.add_text_line("Reading dicom data from: "+ str(input_dir), live_display)
        # Get paths
        dicom_paths_list = list(pathlib.Path(input_dir).glob("**/*.dcm")) # list all file paths found in the data folder that have the .dcm extension
        num_dicoms = len(dicom_paths_list)
        important_info.add_text_line("Found "+str(num_dicoms)+" dicom files.", live_display)

        ###### Indeterminate task preliminaries (END)
        indeterminate_progress_main.update(task_main_indeterminate, visible = False)
        completed_progress.update(task_main_indeterminate_completed, visible = True)
        #live_display.refresh()
        ######



        ###
        ### MODIFY DICOMS (START) ###
        ###

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
            modified_dicom = dicom_modifer_functions.modify_standard_DicomTag(dicom_path, 
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


        ###    
        ### MODIFY DICOMS (END) ###
        ###

    # Exit programme
    sys.exit('>Programme has ended.')


########### main() (END)
    


if __name__ == '__main__':    
    main()