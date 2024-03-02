import pydicom

def modify_DicomTag(specific_dicom, 
                    tags_to_change_dict, 
                    important_info, 
                    live_display):
    
    # Read DICOM
    pydicom_item = pydicom.dcmread(specific_dicom)

    # Iterate over all DICOM tags to change
    for tag_tuple, new_value in tags_to_change_dict.items():
        # Attempt to read the old value for specific tag
        try:
            old_value = pydicom_item[tag_tuple[0],tag_tuple[1]].value
        except: 
            important_info.add_text_line("Tag: "+ str(tag_tuple)+" not present.", live_display)
        else:
            pass
        finally:
            old_value = 'N/A'

        # Change the specific tag's value
        pydicom_item[tag_tuple[0],tag_tuple[1]].value = new_value

        # Output change to UI
        important_info.add_text_line("Tag - " +  str(tag_tuple) + " changed: " + str(old_value) + " --> " + str(new_value))               

    return pydicom_item
