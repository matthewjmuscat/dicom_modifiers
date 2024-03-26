import ques_funcs
import sys

def checkdirs(live_display, important_info, *paths):
    created_a_dir = False
    for path in paths:
        if path.exists():
            important_info.add_text_line(str(path)+ " already exists.", live_display)
        else:
            path.mkdir(parents=True, exist_ok=True)
            important_info.add_text_line("Path "+ str(path)+ " created.", live_display)
            created_a_dir = True
    if created_a_dir == True:
        live_display.stop()
        print('Directories have been created, please ensure the input folder is non-empty, then continue.')
        continue_programme = ques_funcs.ask_ok('> Continue?' )
        if continue_programme == False:
            sys.exit('> Programme exited.')
        else:
            live_display.start()


def find_single_true_key(d):
    # Using list comprehension to filter keys with True values
    keys_with_true_value = [key for key, value in d.items() if value is True]
    
    # Check if the list contains more than one element
    if len(keys_with_true_value) > 1:
        raise ValueError("More than one value is True.")
    elif len(keys_with_true_value) == 0:
        return None  # Or raise an error if a True value is mandatory
    else:
        return keys_with_true_value[0]
    


def create_sublists(original_list):
    result_dict = {}
    for i in original_list:
        # Create a sublist excluding the current element
        sublist = [x for x in original_list if x != i]
        # Store the sublist and the excluded element as a pair
        result_dict[str(i)] = [sublist, i]
    return result_dict

def create_combinations(original_list):
    result_list = []
    for i in original_list:
        # Create a sublist excluding the current element
        sublist = [x for x in original_list if x != i]
        # Create a dictionary for the current combination
        combination_dict = {"Sources": sublist, "Target": i}
        # Add the dictionary to the result list
        result_list.append(combination_dict)
    return result_list