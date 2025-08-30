"""
Data extraction schema definitions
Contains the fixed schema for Cochrane systematic review data extraction
"""

EXTRACTION_SCHEMA = {
    "Study_Info": [
        {"name": "Study_ID", "description": "Extract unique identifier using first author's surname and publication year.", "example": "Smith, 2020"},
        {"name": "Publication_Type", "description": "Document type (full report, abstract, letter, thesis, etc.).", "example": "Full report"},
        {"name": "Study_Design", "description": "Study design as stated or determined from methods.", "example": "Randomized Controlled Trial"},
        {"name": "Aim", "description": "Explicitly stated objectives or research questions.", "example": "To evaluate the effectiveness of a structured exercise program for reducing pain in adults with chronic lower back pain"},
        {"name": "Unit_of_Allocation", "description": "Whether allocation was by individuals, clusters, or body parts.", "example": "Individuals"},
        {"name": "Country", "description": "Country or region where the study was conducted.", "example": "United States"},
        {"name": "Setting", "description": "Specific environment/location where study was implemented (hospital, community, school, etc.).", "example": "Three urban community health centers"},
        {"name": "Method_of_Recruitment", "description": "How participants were recruited for the study.", "example": "Physician referrals and community advertisements"},
        {"name": "Start_Date", "description": "When study recruitment/intervention began.", "example": "January 2018"},
        {"name": "End_Date", "description": "When study data collection completed.", "example": "December 2019"},
        {"name": "Duration", "description": "Total time participants were in the study.", "example": "8 months (including 2-month follow-up)"},
        {"name": "Ethical_Approval", "description": "Whether ethical approval was obtained, committee name and approval number if reported.", "example": "Yes, university ethics committee approval #ERB2017-234"},
        {"name": "Ethical_Approval_Sentence", "description": "Direct quote from paper regarding ethical approval.", "example": "\"The study protocol was approved by the University Research Ethics Board (approval #ERB2017-234).\""},
        {"name": "Informed_Consent", "description": "Whether informed consent was obtained from participants and how.", "example": "Written informed consent obtained from all participants prior to enrollment"},
        {"name": "Funding_Sources", "description": "All reported funding sources and grant numbers.", "example": "National Institute for Health Research, Grant #NH-2017-45621; Funders had no role in study design or data analysis"},
        {"name": "Conflicts_of_Interest", "description": "All declared conflicts of interest for each author.", "example": "Dr. Smith received speaking fees from PharmaCo; Other authors declare no competing interests"},
        {"name": "Key_Conclusions", "description": "Main conclusions as stated by the authors.", "example": "\"A 12-week structured exercise program significantly reduced pain intensity compared to usual care in adults with chronic lower back pain, with benefits maintained at 6-month follow-up\""},
        {"name": "Adverse_Events", "description": "All reported adverse events, safety outcomes, or harms by intervention group.", "example": "Structured exercise: Muscle soreness: 12 (16%), Joint pain: 5 (7%); Usual care: Medication side effects: 8 (11%)"},
        {"name": "Notes", "description": "Any additional important information not captured elsewhere.", "example": "Study was stopped early due to significant benefit in intervention group at interim analysis"}
    ],

    "Groups": [
        {"name": "Group_Name", "description": "Specific name used to identify this group in the study.", "example": "Structured exercise program"},
        {"name": "Study_ID", "description": "Matching study identifier.", "example": "Smith, 2020"},
        {"name": "Group_Type", "description": "Whether this is an intervention or control/comparison group.", "example": "Intervention"},
        {"name": "Sample_Size", "description": "Number of participants initially allocated to this group.", "example": "75 participants"},
        {"name": "Assessed_for_Eligibility", "description": "Number of participants initially screened for this group.", "example": "98 participants"},
        {"name": "Excluded_Before_Randomization", "description": "Number and reasons for exclusion before randomization.", "example": "23 (10 did not meet inclusion criteria, 8 declined participation, 5 other reasons)"},
        {"name": "Randomized", "description": "Number actually randomized to this group.", "example": "75 participants"},
        {"name": "Lost_to_Followup", "description": "Number lost to follow-up and reasons.", "example": "3 (2 withdrew due to time constraints, 1 moved away)"},
        {"name": "Excluded_from_Analysis", "description": "Number excluded from analysis and reasons.", "example": "2 (protocol violations)"},
        {"name": "Cluster_Unit_and_Size", "description": "For cluster trials, description of cluster unit and size.", "example": "Schools, average 45 students per cluster (range 28-62)"},
        {"name": "Description", "description": "Detailed components of intervention for this group.", "example": "60-minute sessions including aerobic warm-up (10 min), strengthening exercises (30 min), flexibility training (15 min), and cool-down (5 min). Strengthening focused on core and lower limb with progressive resistance."},
        {"name": "Duration", "description": "Total duration of the intervention period for this group.", "example": "12 weeks"},
        {"name": "Timing", "description": "Frequency and duration details of intervention episodes.", "example": "3 sessions per week, 60 minutes per session, total 36 sessions"},
        {"name": "Setting_Delivery_Location", "description": "Specific location/environment where intervention was delivered.", "example": "Hospital outpatient rehabilitation gymnasium"},
        {"name": "Delivery", "description": "How the intervention was delivered (mode, format, setting).", "example": "In-person, supervised by trained physiotherapists in groups of 6-8 participants"},
        {"name": "Providers", "description": "Who delivered the intervention (profession, qualifications).", "example": "Certified physiotherapists with ≥3 years experience in pain management; 8 therapists delivered the program"},
        {"name": "Recruitment_Method", "description": "How participants were recruited for this intervention.", "example": "Referrals from primary care physicians and self-referral through advertisement"},
        {"name": "Co_Interventions", "description": "Additional interventions provided alongside the main intervention.", "example": "Educational booklet on back pain self-management; weekly 15-minute advice session"},
        {"name": "Compliance", "description": "Information about adherence to the intervention.", "example": "Mean attendance: 30.2 of 36 sessions (84%); Full program completion: 68 participants (91%)"}
    ],

    "Participant_Characteristics": [
        {"name": "Group", "description": "Matching group name or 'Overall' if characteristics are reported for entire sample.", "example": "Structured exercise program or Overall"},
        {"name": "Total_Sample_Size", "description": "Total number of participants randomized across all groups.", "example": "225"},
        {"name": "Population_Description", "description": "Brief overall description of the participant population.", "example": "Community-dwelling adults with chronic low back pain of at least moderate intensity"},
        {"name": "Baseline_Reporting", "description": "Whether baseline characteristics are reported overall or by group.", "example": "By group or Overall"},
        {"name": "Baseline_Imbalances", "description": "Any significant imbalances between groups at baseline.", "example": "Significant between-group differences in baseline pain severity (p=0.03) and prior treatments (p=0.04)"},
        {"name": "Inclusion_Criteria", "description": "Key inclusion criteria for participant eligibility.", "example": "Adults aged 18-65 years with chronic lower back pain (>3 months duration), pain intensity ≥4/10 on VAS"},
        {"name": "Exclusion_Criteria", "description": "Key exclusion criteria for participant eligibility.", "example": "Specific pathologies (fracture, tumor, infection), recent surgery (<6 months), pending litigation"},
        {"name": "Subgroups_Measured", "description": "All subgroups planned/measured in study design.", "example": "Age (<50 vs ≥50 years), Sex (male vs female), Pain duration (<5 vs ≥5 years)"},
        {"name": "Subgroups_Reported", "description": "Subgroups for which results were actually reported.", "example": "Age and sex subgroups reported; pain duration subgroup analysis mentioned but results not reported"},
        {"name": "Age", "description": "Age statistics overall and/or by group.", "example": "Mean 48.2 years (SD 10.9), range 22-65 years"},
        {"name": "Sex", "description": "Sex/gender distribution overall and/or by group.", "example": "Female: 121 (54%), Male: 104 (46%)"},
        {"name": "Race_Ethnicity", "description": "All reported racial/ethnic categories overall and/or by group.", "example": "White: 135 (60%), Black: 56 (25%), Asian: 22 (10%), Other: 12 (5%)"},
        {"name": "BMI", "description": "Body mass index statistics overall and/or by group.", "example": "Mean 27.8 kg/m² (SD 4.4); Normal weight: 72 (32%), Overweight: 105 (47%), Obese: 48 (21%)"},
        {"name": "Height_Weight", "description": "Height and weight measurements overall and/or by group.", "example": "Height: mean 172.5 cm (SD 9.8); Weight: mean 82.3 kg (SD 14.7)"},
        {"name": "Smoking", "description": "Smoking status categories overall and/or by group.", "example": "Current smokers: 43 (19%), Former smokers: 69 (31%), Never smokers: 113 (50%)"},
        {"name": "Alcohol", "description": "Alcohol consumption patterns overall and/or by group.", "example": "Non-drinkers: 45 (20%), Moderate consumption (1-7 drinks/week): 135 (60%), Heavy (>7 drinks/week): 45 (20%)"},
        {"name": "Physical_Activity", "description": "Physical activity levels overall and/or by group.", "example": "Sedentary (<30 min/week): 126 (56%), Moderate (30-150 min/week): 68 (30%), Active (>150 min/week): 31 (14%)"},
        {"name": "Education", "description": "Education levels overall and/or by group.", "example": "High school or less: 76 (34%), Some college: 56 (25%), College degree or higher: 93 (41%)"},
        {"name": "Employment", "description": "Employment status overall and/or by group.", "example": "Employed full-time: 146 (65%), Part-time: 34 (15%), Not working: 45 (20%)"},
        {"name": "Income", "description": "Income information overall and/or by group.", "example": "<30,000-60,000: 90 (40%), >$60,000: 79 (35%)"},
        {"name": "Marital_Status", "description": "Marital status overall and/or by group.", "example": "Married/partnered: 148 (66%), Single: 54 (24%), Divorced/widowed: 23 (10%)"},
        {"name": "Duration_of_Condition", "description": "Time with condition/symptoms overall and/or by group.", "example": "Median duration of pain: 4.0 years (IQR 2.0-7.8)"},
        {"name": "Severity_of_Illness", "description": "Baseline disease severity measures overall and/or by group.", "example": "Pain intensity (0-10): mean 6.7 (SD 1.3); Disability (ODI): mean 35.0 (SD 8.6)"},
        {"name": "Comorbidities", "description": "All reported comorbid conditions overall and/or by group.", "example": "Hypertension: 42 (28%); Diabetes: 23 (15%); Depression: 33 (22%); Anxiety disorders: 27 (18%); Osteoarthritis: 31 (21%)"},
        {"name": "Medication_Use", "description": "All reported medication usage overall and/or by group.", "example": "NSAIDs: 110 (73%); Acetaminophen: 98 (65%); Opioids: 40 (27%); Muscle relaxants: 55 (37%)"},
        {"name": "Previous_Treatments", "description": "All reported prior treatments overall and/or by group.", "example": "Physical therapy: 70 (47%); Chiropractic: 45 (30%); Acupuncture: 25 (17%); Surgery: 20 (13%)"}
    ],

    "Outcomes": [
        {"name": "Outcome_Name", "description": "Specific name of this outcome as reported.", "example": "Pain intensity"},
        {"name": "Study_ID", "description": "Matching study identifier.", "example": "Smith, 2020"},
        {"name": "Outcome_Type", "description": "Classification as primary or secondary, if specified.", "example": "Primary"},
        {"name": "Time_Points", "description": "All time points when this outcome was measured.", "example": "Baseline, 6 weeks (mid-intervention), 12 weeks (end of intervention), 24 weeks (12-week follow-up)"},
        {"name": "Definition", "description": "How this outcome was defined, including aspects measured.", "example": "Self-reported pain intensity during the past week at rest and during activity"},
        {"name": "Outcome_Definition", "description": "Detailed definition including diagnostic criteria if applicable.", "example": "Average pain intensity over the past 7 days, rated separately for rest and during typical daily activities, then averaged for total score"},
        {"name": "Measurement_Tool", "description": "Specific measurement instrument, scale, or questionnaire used.", "example": "Visual Analog Scale (VAS)"},
        {"name": "Unit_of_Measurement", "description": "Unit or scale range used to measure this outcome.", "example": "0-10 scale"},
        {"name": "Range_of_Measurement", "description": "Range of possible scores and categories if applicable.", "example": "0-10 scale; categorized as mild (0-3), moderate (4-6), severe (7-10)"},
        {"name": "Scales", "description": "Upper and lower limits of scales, and whether high/low scores are better.", "example": "0 (no pain) to 10 (worst pain imaginable); lower scores indicate better outcomes"},
        {"name": "Validation", "description": "Whether the measurement tool has been validated.", "example": "Yes, validated in chronic pain populations"},
        {"name": "Evaluation_Type", "description": "Whether quantitative or qualitative outcome, with conclusion for qualitative.", "example": "Quantitative; for qualitative component, authors concluded 'participants reported high satisfaction with the program'"},
        {"name": "Power", "description": "Statistical power calculation information with supporting text.", "example": "Sample size calculated to detect 1.5-point difference in pain scores with 90% power and alpha of 0.05; 'We calculated that 65 participants per group would provide 90% power to detect a minimal clinically important difference of 1.5 points'"},
        {"name": "Analysis_Method", "description": "Statistical analysis method used (ITT/PP) with supporting text.", "example": "Intention-to-treat analysis with multiple imputation for missing data; 'All analyses followed the intention-to-treat principle'"}
    ],

    "Results": [
        {"name": "Result_ID", "description": "Unique identifier for this result (e.g., Study1_Outcome1_Group1_Timepoint1).", "example": "Smith2020_Pain_Exercise_12weeks"},
        {"name": "Outcome_Name", "description": "Matching outcome name.", "example": "Pain intensity"},
        {"name": "Group_Name", "description": "Matching group name.", "example": "Structured exercise program"},
        {"name": "Time_Point", "description": "Specific time point for this measurement.", "example": "12 weeks (end of intervention)"},
        {"name": "Sample_Size", "description": "Number of participants analyzed at this time point.", "example": "72"},
        {"name": "Data_Complete", "description": "Number with complete data at this time point.", "example": "72 of 75 randomized (96%)"},
        {"name": "Result_Value", "description": "Results for this group (appropriate to outcome type).", "example": "Mean 3.5 (SD 1.8); Mean change from baseline: -3.3 (SD 1.5)"},
        {"name": "Subgroup_Results", "description": "Results stratified by relevant subgroups.", "example": "Age <50 years: Mean 3.0 (SD 1.6); Age ≥50 years: Mean 4.1 (SD 1.9)"},
        {"name": "Missing_Data", "description": "Number missing from this group and reasons.", "example": "3 (2 withdrew due to time constraints, 1 lost to follow-up)"}
    ],

    "Comparisons": [
        {"name": "Comparison_ID", "description": "Unique identifier for this comparison.", "example": "Smith2020_Pain_Ex_vs_UC_12weeks"},
        {"name": "Outcome_Name", "description": "Matching outcome name.", "example": "Pain intensity"},
        {"name": "Group1_Name", "description": "First group in this comparison.", "example": "Structured exercise program"},
        {"name": "Group2_Name", "description": "Second group in this comparison.", "example": "Usual care"},
        {"name": "Intervention_and_Comparison", "description": "Clear description of what is being compared.", "example": "Structured exercise program vs. usual care"},
        {"name": "Time_Point", "description": "Time point for this comparison.", "example": "12 weeks (end of intervention)"},
        {"name": "Effect_Estimate", "description": "Effect measures comparing groups with confidence intervals and p-values.", "example": "Mean difference: -2.5 (95% CI: -3.1 to -1.9); p<0.001"},
        {"name": "Adjusted_Effect", "description": "Adjusted effect size with covariates used.", "example": "Adjusted mean difference: -2.3 (95% CI: -2.9 to -1.7); p<0.001; adjusted for baseline pain, age, and sex"},
        {"name": "Subgroup_Analyses", "description": "Any subgroup or interaction analyses.", "example": "Age subgroups: Significant treatment effect in patients <50 years (MD: -3.2; 95% CI: -4.1 to -2.3) but not in patients ≥50 years (MD: -1.1; 95% CI: -2.4 to 0.2); p for interaction=0.02"},
        {"name": "Statistical_Methods", "description": "Statistical tests and adjustments used.", "example": "ANCOVA adjusting for baseline pain scores; intention-to-treat analysis with multiple imputation for missing data; SPSS v26"}
    ]
}

def create_structured_schemas():
    """为每个表格创建JSON Schema"""
    schemas = {}
    
    # Study_Info表的schema
    schemas["Study_Info"] = {
        "type": "object",
        "properties": {
            "studies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Study_ID": {"type": "string"},
                        "Publication_Type": {"type": "string"},
                        "Study_Design": {"type": "string"},
                        "Aim": {"type": "string"},
                        "Unit_of_Allocation": {"type": "string"},
                        "Country": {"type": "string"},
                        "Setting": {"type": "string"},
                        "Method_of_Recruitment": {"type": "string"},
                        "Start_Date": {"type": "string"},
                        "End_Date": {"type": "string"},
                        "Duration": {"type": "string"},
                        "Ethical_Approval": {"type": "string"},
                        "Ethical_Approval_Sentence": {"type": "string"},
                        "Informed_Consent": {"type": "string"},
                        "Funding_Sources": {"type": "string"},
                        "Conflicts_of_Interest": {"type": "string"},
                        "Key_Conclusions": {"type": "string"},
                        "Adverse_Events": {"type": "string"},
                        "Notes": {"type": "string"}
                    },
                    "required": [
                        "Study_ID", "Publication_Type", "Study_Design", "Aim", 
                        "Unit_of_Allocation", "Country", "Setting", "Method_of_Recruitment",
                        "Start_Date", "End_Date", "Duration", "Ethical_Approval",
                        "Ethical_Approval_Sentence", "Informed_Consent", "Funding_Sources",
                        "Conflicts_of_Interest", "Key_Conclusions", "Adverse_Events", "Notes"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["studies"],
        "additionalProperties": False
    }
    
    # Groups表的schema
    schemas["Groups"] = {
        "type": "object",
        "properties": {
            "groups": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Group_Name": {"type": "string"},
                        "Study_ID": {"type": "string"},
                        "Group_Type": {"type": "string"},
                        "Sample_Size": {"type": "string"},
                        "Assessed_for_Eligibility": {"type": "string"},
                        "Excluded_Before_Randomization": {"type": "string"},
                        "Randomized": {"type": "string"},
                        "Lost_to_Followup": {"type": "string"},
                        "Excluded_from_Analysis": {"type": "string"},
                        "Cluster_Unit_and_Size": {"type": "string"},
                        "Description": {"type": "string"},
                        "Duration": {"type": "string"},
                        "Timing": {"type": "string"},
                        "Setting_Delivery_Location": {"type": "string"},
                        "Delivery": {"type": "string"},
                        "Providers": {"type": "string"},
                        "Recruitment_Method": {"type": "string"},
                        "Co_Interventions": {"type": "string"},
                        "Compliance": {"type": "string"}
                    },
                    "required": [
                        "Group_Name", "Study_ID", "Group_Type", "Sample_Size",
                        "Assessed_for_Eligibility", "Excluded_Before_Randomization",
                        "Randomized", "Lost_to_Followup", "Excluded_from_Analysis",
                        "Cluster_Unit_and_Size", "Description", "Duration", "Timing",
                        "Setting_Delivery_Location", "Delivery", "Providers",
                        "Recruitment_Method", "Co_Interventions", "Compliance"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["groups"],
        "additionalProperties": False
    }
    
    # Participant_Characteristics表的schema
    schemas["Participant_Characteristics"] = {
        "type": "object",
        "properties": {
            "characteristics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Group_Name": {"type": "string"},
                        "Total_Sample_Size": {"type": "string"},
                        "Population_Description": {"type": "string"},
                        "Baseline_Reporting": {"type": "string"},
                        "Baseline_Imbalances": {"type": "string"},
                        "Inclusion_Criteria": {"type": "string"},
                        "Exclusion_Criteria": {"type": "string"},
                        "Subgroups_Measured": {"type": "string"},
                        "Subgroups_Reported": {"type": "string"},
                        "Age": {"type": "string"},
                        "Sex": {"type": "string"},
                        "Race_Ethnicity": {"type": "string"},
                        "BMI": {"type": "string"},
                        "Height_Weight": {"type": "string"},
                        "Smoking": {"type": "string"},
                        "Alcohol": {"type": "string"},
                        "Physical_Activity": {"type": "string"},
                        "Education": {"type": "string"},
                        "Employment": {"type": "string"},
                        "Income": {"type": "string"},
                        "Marital_Status": {"type": "string"},
                        "Duration_of_Condition": {"type": "string"},
                        "Severity_of_Illness": {"type": "string"},
                        "Comorbidities": {"type": "string"},
                        "Medication_Use": {"type": "string"},
                        "Previous_Treatments": {"type": "string"}
                    },
                    "required": [
                        "Group_Name", "Total_Sample_Size", "Population_Description",
                        "Baseline_Reporting", "Baseline_Imbalances", "Inclusion_Criteria",
                        "Exclusion_Criteria", "Subgroups_Measured", "Subgroups_Reported",
                        "Age", "Sex", "Race_Ethnicity", "BMI", "Height_Weight",
                        "Smoking", "Alcohol", "Physical_Activity", "Education",
                        "Employment", "Income", "Marital_Status", "Duration_of_Condition",
                        "Severity_of_Illness", "Comorbidities", "Medication_Use",
                        "Previous_Treatments"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["characteristics"],
        "additionalProperties": False
    }
    
    # Outcomes表的schema
    schemas["Outcomes"] = {
        "type": "object",
        "properties": {
            "outcomes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Outcome_Name": {"type": "string"},
                        "Study_ID": {"type": "string"},
                        "Outcome_Type": {"type": "string"},
                        "Time_Points": {"type": "string"},
                        "Definition": {"type": "string"},
                        "Outcome_Definition": {"type": "string"},
                        "Measurement_Tool": {"type": "string"},
                        "Unit_of_Measurement": {"type": "string"},
                        "Range_of_Measurement": {"type": "string"},
                        "Scales": {"type": "string"},
                        "Validation": {"type": "string"},
                        "Evaluation_Type": {"type": "string"},
                        "Power": {"type": "string"},
                        "Analysis_Method": {"type": "string"}
                    },
                    "required": [
                        "Outcome_Name", "Study_ID", "Outcome_Type", "Time_Points",
                        "Definition", "Outcome_Definition", "Measurement_Tool",
                        "Unit_of_Measurement", "Range_of_Measurement", "Scales",
                        "Validation", "Evaluation_Type", "Power", "Analysis_Method"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["outcomes"],
        "additionalProperties": False
    }
    
    # Results表的schema
    schemas["Results"] = {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Result_ID": {"type": "string"},
                        "Outcome_Name": {"type": "string"},
                        "Group_Name": {"type": "string"},
                        "Time_Point": {"type": "string"},
                        "Sample_Size": {"type": "string"},
                        "Data_Complete": {"type": "string"},
                        "Result_Value": {"type": "string"},
                        "Subgroup_Results": {"type": "string"},
                        "Missing_Data": {"type": "string"}
                    },
                    "required": [
                        "Result_ID", "Outcome_Name", "Group_Name", "Time_Point",
                        "Sample_Size", "Data_Complete", "Result_Value",
                        "Subgroup_Results", "Missing_Data"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["results"],
        "additionalProperties": False
    }
    
    # Comparisons表的schema
    schemas["Comparisons"] = {
        "type": "object",
        "properties": {
            "comparisons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Comparison_ID": {"type": "string"},
                        "Outcome_Name": {"type": "string"},
                        "Group1_Name": {"type": "string"},
                        "Group2_Name": {"type": "string"},
                        "Intervention_and_Comparison": {"type": "string"},
                        "Time_Point": {"type": "string"},
                        "Effect_Estimate": {"type": "string"},
                        "Adjusted_Effect": {"type": "string"},
                        "Subgroup_Analyses": {"type": "string"},
                        "Statistical_Methods": {"type": "string"}
                    },
                    "required": [
                        "Comparison_ID", "Outcome_Name", "Group1_Name", "Group2_Name",
                        "Intervention_and_Comparison", "Time_Point", "Effect_Estimate",
                        "Adjusted_Effect", "Subgroup_Analyses", "Statistical_Methods"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": ["comparisons"],
        "additionalProperties": False
    }
    
    return schemas
