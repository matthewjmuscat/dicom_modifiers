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
import dicom_modifier_functions
import processes_funcs

### IMPORT PACKAGES (END)



########### main() (START)

def main():
    ### Define variables

    ### What would you like to do?
    ### Only one key can have a True value!
    mod_dicoms_str = 'Modify dicoms'
    combine_RTStructs_str = 'Combine RT structs'
    process_to_run_dict = {mod_dicoms_str: False,
                           combine_RTStructs_str: True}

    ### IF mod_dicoms_str == True
    ### Define the dictionary that defines the dicom tags to change and what the new values should be
    ## IMPORTANT: For this below dict, make sure these are all tags that are part of the standard dicom library!
    ## IMPORTANT: Make sure that the new value to be set is of the correct datatype! - Example: SeriesDescription has value representation LO, therefore new value must be string!
    # Can use either tuple of literal hexidecimals or tag keyword as string - Example: 'SeriesDescription' or  
    standard_tags_to_change_dict = {(0x0008,0x103E): 'PELVIS',
                                }

    ### IF combine_RTStructs_str == True
    ### Provide a list of strings of the structures (or an empty list for ALL structures) you wish to be transferred
    # Note that the list is NOT case sensitive, when the programme makes the comparison it converts all characters to lower case 
    # for both vars being compared.
    structures_to_be_transferred_list = ['bladder']

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

        ### Check what you want to accomplish:
        try:
            process_to_run = misc_tools.find_single_true_key(process_to_run_dict)
            print(f"You indicated you want to: {process_to_run}")
        except ValueError as e:
            print(e)


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

        if process_to_run == mod_dicoms_str:
            processes_funcs.modify_dicoms(num_dicoms,
                  patients_progress,
                  completed_progress,
                  dicom_paths_list,
                  session_output_dir,
                  standard_tags_to_change_dict,
                  important_info,
                  live_display
                  )


        ###    
        ### MODIFY DICOMS (END) ###
        ###
            

        ###
        ### COMBINE DICOMS (START) ###
        ###
        if process_to_run == combine_RTStructs_str:  
            processes_funcs.combine_structure_sets(num_dicoms,
                  patients_progress,
                  completed_progress,
                  dicom_paths_list,
                  session_output_dir,
                  structures_to_be_transferred_list,
                  important_info,
                  live_display
                  )


        ###        
        ### COMBINE DICOMS (END) ### 
        ###

    # Exit programme
    sys.exit('>Programme has ended.')


########### main() (END)
    


if __name__ == '__main__':    
    main()