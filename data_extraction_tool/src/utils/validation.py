"""
Data validation utilities
"""

def validate_data_consistency(all_data):
    """Validate data consistency across tables"""
    print("\nValidating data consistency...")
  
    # Collect all Study_IDs
    study_ids = set()
    if "Study_Info" in all_data and all_data["Study_Info"]:
        for study in all_data["Study_Info"]:
            if "Study_ID" in study and study["Study_ID"]:
                study_ids.add(study["Study_ID"])
  
    # Collect all Group_Names
    group_names = set()
    if "Groups" in all_data and all_data["Groups"]:
        for group in all_data["Groups"]:
            if "Group_Name" in group and group["Group_Name"]:
                group_names.add(group["Group_Name"])
  
    # Collect all Outcome_Names
    outcome_names = set()
    if "Outcomes" in all_data and all_data["Outcomes"]:
        for outcome in all_data["Outcomes"]:
            if "Outcome_Name" in outcome and outcome["Outcome_Name"]:
                outcome_names.add(outcome["Outcome_Name"])
  
    # Validate Study_ID references in Groups
    if "Groups" in all_data and all_data["Groups"]:
        missing_study_ids = 0
        for group in all_data["Groups"]:
            if "Study_ID" in group and group["Study_ID"] and group["Study_ID"] not in study_ids:
                missing_study_ids += 1
        if missing_study_ids > 0:
            print(f"  Warning: Groups table has {missing_study_ids} records referencing non-existent Study_ID")
  
    # Validate Group_Name references in Participant_Characteristics
    if "Participant_Characteristics" in all_data and all_data["Participant_Characteristics"]:
        missing_group_names = 0
        for char in all_data["Participant_Characteristics"]:
            if "Group" in char and char["Group"] and char["Group"] != "Overall" and char["Group"] not in group_names:
                missing_group_names += 1
        if missing_group_names > 0:
            print(f"  Warning: Participant_Characteristics table has {missing_group_names} records referencing non-existent Group")
  
    # Validate Outcome_Name and Group_Name references in Results
    if "Results" in all_data and all_data["Results"]:
        missing_outcome_names = 0
        missing_group_names = 0
        for result in all_data["Results"]:
            if "Outcome_Name" in result and result["Outcome_Name"] and result["Outcome_Name"] not in outcome_names:
                missing_outcome_names += 1
            if "Group_Name" in result and result["Group_Name"] and result["Group_Name"] not in group_names:
                missing_group_names += 1
        if missing_outcome_names > 0:
            print(f"  Warning: Results table has {missing_outcome_names} records referencing non-existent Outcome_Name")
        if missing_group_names > 0:
            print(f"  Warning: Results table has {missing_group_names} records referencing non-existent Group_Name")
  
    # Validate Outcome_Name and Group_Name references in Comparisons
    if "Comparisons" in all_data and all_data["Comparisons"]:
        missing_outcome_names = 0
        missing_group1_names = 0
        missing_group2_names = 0
        for comparison in all_data["Comparisons"]:
            if "Outcome_Name" in comparison and comparison["Outcome_Name"] and comparison["Outcome_Name"] not in outcome_names:
                missing_outcome_names += 1
            if "Group1_Name" in comparison and comparison["Group1_Name"] and comparison["Group1_Name"] not in group_names:
                missing_group1_names += 1
            if "Group2_Name" in comparison and comparison["Group2_Name"] and comparison["Group2_Name"] not in group_names:
                missing_group2_names += 1
        if missing_outcome_names > 0:
            print(f"  Warning: Comparisons table has {missing_outcome_names} records referencing non-existent Outcome_Name")
        if missing_group1_names > 0:
            print(f"  Warning: Comparisons table has {missing_group1_names} records referencing non-existent Group1_Name")
        if missing_group2_names > 0:
            print(f"  Warning: Comparisons table has {missing_group2_names} records referencing non-existent Group2_Name")
  
    print("  Data consistency validation completed")