import pydicom
from pydicom.datadict import dictionary_VR

def modify_standard_DicomTag(specific_dicom, 
                    tags_to_change_dict, 
                    important_info, 
                    live_display):
    
    # Read DICOM
    pydicom_item = pydicom.dcmread(specific_dicom)

    # Iterate over all DICOM tags to change
    for tag_key, new_value in tags_to_change_dict.items():
        # Attempt to read the old value for specific tag
        if tag_key in pydicom_item:
            old_value = pydicom_item[tag_key].value
        else: 
            #important_info.add_text_line("Tag: "+ str(tag_key)+" not present in this DICOM.", live_display)
            old_value = None

        # Change the specific tag's value
        if tag_key in pydicom_item:
            pydicom_item[tag_key].value = new_value
        else:
            try:
                value_representation = dictionary_VR(tag_key)
            except KeyError:
                raise Exception(str(tag_key)+": is a non-standard tag!")
            else:
                pydicom_item.add_new(tag_key, value_representation, new_value)

        # Output change to UI
        #important_info.add_text_line("Tag - " +  str(tag_key) + " changed: " + str(old_value) + " --> " + str(new_value), live_display)               

    return pydicom_item
