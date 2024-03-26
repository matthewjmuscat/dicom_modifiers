import pydicom
from pydicom.datadict import dictionary_VR
from pydicom.sequence import Sequence
from copy import deepcopy
from pydicom.uid import generate_uid


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





### COMBINING RT STRUCTS

def check_referenced_frame_of_reference_match(source_ds, target_ds):
    """
    Check if the DICOM datasets can be combined based on matching FrameOfReferenceUID,
    ReferencedSOPInstanceUID in RTReferencedStudySequence, and SeriesInstanceUID in
    RTReferencedSeriesSequence. Returns True and a matching message, or False with mismatch details.
    """
    # Check if ReferencedFrameOfReferenceSequence exists and extract FrameOfReferenceUID
    try:
        source_frame_uid = source_ds.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID
        target_frame_uid = target_ds.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID
        if source_frame_uid != target_frame_uid:
            return False, "Mismatched FrameOfReferenceUID"
    except AttributeError:
        return False, "Missing FrameOfReferenceUID in one or both DICOMs"
    
    # Assuming matching FrameOfReferenceUID, check RTReferencedStudySequence for matching ReferencedSOPInstanceUID
    try:
        source_study_uid = source_ds.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].ReferencedSOPInstanceUID
        target_study_uid = target_ds.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].ReferencedSOPInstanceUID
        if source_study_uid != target_study_uid:
            return False, "Mismatched ReferencedSOPInstanceUID in RTReferencedStudySequence"
    except AttributeError:
        return False, "Missing RTReferencedStudySequence in one or both DICOMs"
    
    # Check RTReferencedSeriesSequence for matching SeriesInstanceUID
    try:
        source_series_uid = source_ds.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID
        target_series_uid = target_ds.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID
        if source_series_uid != target_series_uid:
            return False, "Mismatched SeriesInstanceUID in RTReferencedSeriesSequence"
    except AttributeError:
        return False, "Missing RTReferencedSeriesSequence in one or both DICOMs"
    
    return True, "All relevant fields match"


def check_sequence_match(source_ds, target_ds, sequence_tag):
    """Check if the specified sequence matches between two DICOM datasets."""
    return getattr(source_ds, sequence_tag, None) == getattr(target_ds, sequence_tag, None)

def get_unique_roinumber(target_ds):
    """Generate a unique ROINumber for the target dataset."""
    existing_numbers = {roi.ROINumber for roi in target_ds.StructureSetROISequence}
    return max(existing_numbers, default=0) + 1


def get_max_roinumber(ds):
    """Get the maximum ROINumber used in the dataset."""
    if "StructureSetROISequence" in ds:
        return max((roi.ROINumber for roi in ds.StructureSetROISequence), default=0)
    return 0

def combine_rtstructs_with_checks(source_path, target_path):
    source_ds = pydicom.dcmread(source_path)
    target_ds = pydicom.dcmread(target_path)
    
    # Check for matching sequences
    check_referenced_frame_of_reference_match(source_ds, target_ds)
    for seq_tag in ['ReferencedFrameOfReferenceSequence', 'RTReferencedStudySequence', 'RTReferencedSeriesSequence']:
        assert check_sequence_match(source_ds, target_ds, seq_tag), f"{seq_tag} does not match"
    
    # Ensure ROIContourSequence and StructureSetROISequence exist in the target
    if "ROIContourSequence" not in target_ds:
        target_ds.ROIContourSequence = Sequence()
    if "StructureSetROISequence" not in target_ds:
        target_ds.StructureSetROISequence = Sequence()
    if "RTROIObservationsSequence" not in target_ds:
        target_ds.RTROIObservationsSequence = Sequence()

    max_roinumber = get_max_roinumber(target_ds)
    
    for source_structure in source_ds.StructureSetROISequence:
        new_roi_number = max_roinumber + 1
        max_roinumber += 1
        
        # Copy and update the ROI in StructureSetROISequence
        new_structure = deepcopy(source_structure)
        new_structure.ROINumber = new_roi_number
        target_ds.StructureSetROISequence.append(new_structure)
        
        # Find and copy the corresponding contour in ROIContourSequence
        for source_roi in source_ds.ROIContourSequence:
            if source_roi.ReferencedROINumber == source_structure.ROINumber:
                new_roi = deepcopy(source_roi)
                new_roi.ReferencedROINumber = new_roi_number
                if "ROIContourSequence" not in target_ds:
                    target_ds.ROIContourSequence = Sequence()
                target_ds.ROIContourSequence.append(new_roi)
                break
        
        # Find and copy the corresponding observation in RTROIObservationsSequence
        for source_observation in source_ds.RTROIObservationsSequence:
            if source_observation.ReferencedROINumber == source_structure.ROINumber:
                new_observation = deepcopy(source_observation)
                new_observation.ObservationNumber = new_roi_number
                new_observation.ReferencedROINumber = new_roi_number
                if "RTROIObservationsSequence" not in target_ds:
                    target_ds.RTROIObservationsSequence = Sequence()
                target_ds.RTROIObservationsSequence.append(new_observation)
                break
    
    
    return target_ds



def combine_multiple_rtstructs_with_full_update(source_paths, target_path):
    target_ds = deepcopy(pydicom.dcmread(target_path))
    max_roinumber = get_max_roinumber(target_ds)
    
    for source_path in source_paths:
        source_ds = pydicom.dcmread(source_path)

        # Check for matching sequences
        match, message = check_referenced_frame_of_reference_match(source_ds, target_ds)
        if not match:
            raise ValueError(f"The DICOM files cannot be combined due to the following mismatches: {message}")
        
        for source_structure in source_ds.StructureSetROISequence:
            new_roi_number = max_roinumber + 1
            max_roinumber += 1
            
            # Copy and update the ROI in StructureSetROISequence
            new_structure = deepcopy(source_structure)
            new_structure.ROINumber = new_roi_number
            target_ds.StructureSetROISequence.append(new_structure)
            
            # Process the corresponding contour in ROIContourSequence
            for source_roi in source_ds.ROIContourSequence:
                if source_roi.ReferencedROINumber == source_structure.ROINumber:
                    new_roi = deepcopy(source_roi)
                    new_roi.ReferencedROINumber = new_roi_number
                    if "ROIContourSequence" not in target_ds:
                        target_ds.ROIContourSequence = Sequence()
                    target_ds.ROIContourSequence.append(new_roi)
                    break
            
            # Process the corresponding observation in RTROIObservationsSequence
            for source_observation in source_ds.RTROIObservationsSequence:
                if source_observation.ReferencedROINumber == source_structure.ROINumber:
                    new_observation = deepcopy(source_observation)
                    new_observation.ObservationNumber = new_roi_number
                    new_observation.ReferencedROINumber = new_roi_number
                    if "RTROIObservationsSequence" not in target_ds:
                        target_ds.RTROIObservationsSequence = Sequence()
                    target_ds.RTROIObservationsSequence.append(new_observation)
                    break

    # generate a unique id for the new dicom 
    target_ds.SOPInstanceUID = generate_uid()
    # include/modify the series description 
    combined_description = 'Target: '+str(target_path.name) +'. Sources: '+', '.join([str(source.name) for source in source_paths])
    if "SeriesDescription" in target_ds:
        target_ds.SeriesDescription += combined_description
    else:
        target_ds.SeriesDescription = combined_description

    return target_ds