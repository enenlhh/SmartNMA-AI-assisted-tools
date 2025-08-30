import time
import os
import pandas as pd
import numpy as np
import glob
from typing import Dict, List, Tuple, Optional, Union
import re
import sys

class GradeEvaluator:
    """GRADE evaluation system for assessing the certainty of evidence in network meta-analysis"""
    
    def __init__(self, base_dir: str, outcome_name: str, model_type: str = "random", 
             ask_for_mid: bool = False, mid_params: dict = None,
             rob_params: dict = None, inconsistency_params: dict = None):
        """
        Initialize the GRADE evaluator
        
        Parameters:
            base_dir: Base directory containing NMA analysis results
            outcome_name: Name of the outcome
            model_type: Type of model used, 'random' or 'fixed'
            ask_for_mid: Whether to ask for MID values for imprecision assessment
            mid_params: Dictionary containing harmful_mid and benefit_mid
            rob_params: ROB assessment parameter dictionary
            inconsistency_params: Inconsistency assessment parameter dictionary
        """

        # Set default MID parameters
        self.mid_params = {
            'harmful_mid': None,  # Default no harmful threshold
            'benefit_mid': None   # Default no benefit threshold
        }
        
        # Update with user-provided MID parameters
        if mid_params:
            self.mid_params.update(mid_params)
        self.base_dir = base_dir
        self.outcome_name = outcome_name
        self.model_type = model_type
        self.model_dir_name = "Results of Random Effect Model" if model_type == "random" else "Results of Common Effect Model"
        self.outcome_dir = os.path.join(base_dir, outcome_name)
        self.model_dir = os.path.join(self.outcome_dir, self.model_dir_name)
        self.ask_for_mid = ask_for_mid
        
        # Set default ROB parameters
        self.rob_params = {
            'high_risk_count_threshold': 0.5,  # Default high-risk study proportion threshold is 50%
            'high_risk_weight_threshold': 50,  # Default high-risk study weight threshold is 50%
            'very_serious_weight_threshold': 80  # Default very serious bias weight threshold is 80%
        }
        
        # Set default Inconsistency parameters
        self.inconsistency_params = {
            'i2_threshold': 60,  # Default I² threshold is 60%
            'i2_very_serious_threshold': 90,  # Default very serious inconsistency I² threshold is 90%
            'ci_overlap_threshold': 0.5  # Default 95% CI overlap threshold is 50%
        }
        
        # Update with user-provided parameters
        if rob_params:
            self.rob_params.update(rob_params)
        if inconsistency_params:
            self.inconsistency_params.update(inconsistency_params)
        
        # Check if directory exists
        if not os.path.exists(self.model_dir):
            raise FileNotFoundError(f"Directory does not exist: {self.model_dir}")
        
        # Load necessary data files
        self.load_analysis_data()

    
    def load_analysis_data(self):
        """Load NMA analysis generated data files"""
        try:
            # Load network table data
            nettable_file = os.path.join(self.model_dir, f"{self.outcome_name}-nettable.csv")
            self.nettable_data = pd.read_csv(nettable_file)
            
            # Load original data
            original_data_file = os.path.join(self.outcome_dir, f"{self.outcome_name}-original_data.csv") 
            self.original_data = pd.read_csv(original_data_file)
            
            # Load analysis settings
            settings_file = os.path.join(self.outcome_dir, f"{self.outcome_name}-analysis_settings.csv")
            self.analysis_settings = pd.read_csv(settings_file)
            self.settings = dict(zip(self.analysis_settings['setting'], self.analysis_settings['value']))
            
            # Load pairwise comparison data
            pairwise_file = os.path.join(self.model_dir, f"{self.outcome_name}-netpairwise.csv")
            self.pairwise_data = pd.read_csv(pairwise_file)
            
            # If meta-analysis results file exists, load it
            meta_result_file = os.path.join(self.model_dir, f"{self.outcome_name}-meta_result_{self.model_type}.csv")
            if os.path.exists(meta_result_file):
                self.meta_result = pd.read_csv(meta_result_file)
            else:
                self.meta_result = None
                print(f"Warning: Could not find meta-analysis results file {meta_result_file}")
            
            # Get data type
            self.data_type = self.settings.get('data_type', 'unknown')
            self.effect_measure = self.settings.get('effect_measure', '')
            self.ref_treatment = self.settings.get('ref_treatment', '')
            
            print(f"Successfully loaded analysis data for {self.outcome_name}.")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def prepare_grade_framework(self) -> pd.DataFrame:
        """Prepare the GRADE evaluation framework"""
        # Create GRADE table based on nettable data
        grade_results = pd.DataFrame({
            "Arm_1": self.nettable_data.iloc[:, 0],
            "Arm_2": self.nettable_data.iloc[:, 1],
            "No_of_study": self.nettable_data.iloc[:, 2],
            "Sample_size": self.nettable_data.iloc[:, 3],
            "I2": self.nettable_data.iloc[:, 4],
            "Direct_estimate": self.nettable_data.iloc[:, 5],
            "ROB": pd.NA,
            "Reason_for_ROB": pd.NA,
            "Inconsistency": pd.NA,
            "Reason_for_Inconsistency": pd.NA,
            "Indirectness": pd.NA,
            "Reason_for_Indirectness": pd.NA,
            "Publication_bias": pd.NA,
            "Reason_for_Publication_bias": pd.NA,
            "Direct_rating_without_imprecision": pd.NA,
            "Indirect_estimate": self.nettable_data.iloc[:, 6],
            "First_order_loop_of_the_most_contribution": pd.NA,
            "Certainty_of_evidence_for_arm1": pd.NA,
            "Certainty_of_evidence_for_arm2": pd.NA,
            "Intransitivity": pd.NA,
            "Reason_for_Intransitivity": pd.NA,
            "Indirect_rating_without_imprecision": pd.NA,
            "Network_meta_analysis": self.nettable_data.iloc[:, 7],
            "Higher_rating_of_direct_and_indirect_without_imprecision": pd.NA,
            "Incoherence": pd.NA,
            "Reason_for_Incoherence": self.nettable_data.iloc[:, 8],
            "Imprecision": pd.NA,
            "Reason_for_Imprecision": pd.NA,
            "Final_rating": pd.NA,
            "Final_rating_reason": pd.NA
        })
        
        # Convert string type No_of_study column to numeric
        grade_results['No_of_study'] = pd.to_numeric(grade_results['No_of_study'], errors='coerce')
        
        return grade_results
    
    def find_studies_with_treatments(self) -> pd.DataFrame:
        """Organize data of studies and corresponding treatment groups"""
        return self.original_data[['study', 'treatment', 'ROB']].drop_duplicates()
    
    def precompute_sample_sizes_and_ois(self) -> dict:
        """
        Precompute effective sample sizes for direct, indirect, and network evidence
        as well as the Optimal Information Size (OIS) for each comparison of each outcome
        
        Returns:
            Dictionary of precomputed values, formatted as {(arm1, arm2): {
                'direct_sample_size': value,
                'indirect_sample_size': value,
                'network_sample_size': value,
                'ois': value,
                'ois_reason': 'text description'
            }}
        """
        precomputed_data = {}
        
        # Get MID values
        harmful_mid = self.mid_params.get('harmful_mid')
        benefit_mid = self.mid_params.get('benefit_mid')
        
        # Calculate MCID (Minimal Clinical Important Difference)
        if harmful_mid is not None and benefit_mid is not None:
            if abs(1 - harmful_mid) < abs(benefit_mid - 1):
                mcid = abs(1 - harmful_mid)
            else:
                mcid = abs(benefit_mid - 1)
        else:
            mcid = 0.2  # Default MCID value
        
        # Iterate over all comparison groups
        for i in range(len(self.nettable_data)):
            arm1 = self.nettable_data.iloc[i, 0]
            arm2 = self.nettable_data.iloc[i, 1]
            pair_key = (arm1, arm2)
            
            # Initialize data for this comparison group
            precomputed_data[pair_key] = {
                'direct_sample_size': 0,
                'indirect_sample_size': 0,
                'network_sample_size': 0,
                'ois': 800,  # Default OIS value
                'ois_reason': "Using default OIS = 800"
            }
            
            # Calculate direct evidence sample size
            sample_size_str = self.nettable_data.iloc[i, 3]  # 'Sample_size' column
            if pd.notna(sample_size_str):
                direct_sample_size = int(re.sub(r'[^0-9]', '', str(sample_size_str)) or 0)
                precomputed_data[pair_key]['direct_sample_size'] = direct_sample_size
            
            # Calculate indirect evidence sample size
            # Find possible first-order loops (bridge nodes) between this pair of treatments
            indirect_sample_size = self._calculate_indirect_sample_size(arm1, arm2)
            precomputed_data[pair_key]['indirect_sample_size'] = indirect_sample_size
            
            # Calculate effective sample size of network evidence
            network_sample_size = self._calculate_network_sample_size(arm1, arm2)
            precomputed_data[pair_key]['network_sample_size'] = network_sample_size
            
            # Calculate Optimal Information Size (OIS)
            if harmful_mid is not None and benefit_mid is not None:
                ois, ois_reason = self._calculate_ois(arm1, arm2, mcid)
                precomputed_data[pair_key]['ois'] = ois
                precomputed_data[pair_key]['ois_reason'] = ois_reason
        
        return precomputed_data

    def _calculate_indirect_sample_size(self, arm1, arm2) -> float:
        """
        Calculate the effective sample size of indirect evidence for a given pair of treatments
        
        Parameters:
            arm1, arm2: Two treatments to compare
            
        Returns:
            Effective sample size of indirect evidence
        """
        # Get all directly compared intervention pairs
        direct_comparisons = []
        for i in range(len(self.nettable_data)):
            row_arm1 = self.nettable_data.iloc[i, 0]
            row_arm2 = self.nettable_data.iloc[i, 1]
            study_count = self.nettable_data.iloc[i, 2] 
            sample_size_str = self.nettable_data.iloc[i, 3]
            
            if pd.notna(study_count) and study_count > 0 and pd.notna(sample_size_str):
                sample_size = int(re.sub(r'[^0-9]', '', str(sample_size_str)) or 0)
                direct_comparisons.append((row_arm1, row_arm2, sample_size))
        
        # All possible nodes
        all_nodes = set()
        for a1, a2, _ in direct_comparisons:
            all_nodes.add(a1)
            all_nodes.add(a2)
        
        # Remove the two nodes of the current comparison to get potential bridge nodes
        potential_bridges = [node for node in all_nodes if node != arm1 and node != arm2]
        
        max_effective_sample = 0
        
        # Check each potential bridge node
        for bridge in potential_bridges:
            # Find sample sizes for arm1-bridge and bridge-arm2
            sample_size_a_bridge = 0
            sample_size_bridge_b = 0
            
            for a, b, sample in direct_comparisons:
                if (a == arm1 and b == bridge) or (a == bridge and b == arm1):
                    sample_size_a_bridge = sample
                if (a == bridge and b == arm2) or (a == arm2 and b == bridge):
                    sample_size_bridge_b = sample
            
            # If both segments have data, calculate effective sample size of indirect comparison
            if sample_size_a_bridge > 0 and sample_size_bridge_b > 0:
                effective_sample = 1 / ((1/sample_size_a_bridge) + (1/sample_size_bridge_b))
                if effective_sample > max_effective_sample:
                    max_effective_sample = effective_sample
        
        return max_effective_sample

    def _calculate_network_sample_size(self, arm1, arm2) -> float:
        """
        Calculate the effective sample size of network evidence for a given pair of treatments
        
        Parameters:
            arm1, arm2: Two treatments to compare
            
        Returns:
            Effective sample size of network evidence
        """
        # Find network estimate and confidence interval
        estimate_str = None
        for i in range(len(self.nettable_data)):
            if self.nettable_data.iloc[i, 0] == arm1 and self.nettable_data.iloc[i, 1] == arm2:
                estimate_str = self.nettable_data.iloc[i, 7]  # 'Network_meta_analysis' column
                break
        
        if pd.isna(estimate_str) or not re.search(r'[0-9]', str(estimate_str)):
            return 0  # Return 0 if no valid network estimate
        
        # Extract point estimate and confidence interval from string
        estimate_point = None  # Add this line to define the variable
        ci_lower = None
        ci_upper = None
        
        # Extract point estimate
        point_match = re.search(r'^([0-9.-]+)', str(estimate_str))
        if point_match:
            try:
                estimate_point = float(point_match.group(1).strip())
            except ValueError:
                pass
        
        ci_match = re.search(r'\[(.*?);(.*?)\]', str(estimate_str))
        if ci_match:
            try:
                ci_lower = float(ci_match.group(1).strip())
                ci_upper = float(ci_match.group(2).strip())
            except ValueError:
                pass
        
        if ci_lower is None or ci_upper is None or estimate_point is None:
            # If CI or point estimate cannot be extracted, use direct sample size as conservative estimate
            return self._calculate_direct_sample_size(arm1, arm2)
        
        # Calculate standard error (depending on data type)
        if self.data_type == "binary":
            # Binary outcomes use log scale
            senma = (np.log(ci_upper) - np.log(ci_lower)) / 3.92
        else:
            # Continuous outcomes use original scale
            senma = (ci_upper - ci_lower) / 3.92
        
        # For continuous variables (MD/SMD), use the formula
        if self.data_type == "continuous":
            pooled_within_group_sd = self._get_pooled_within_group_sd(arm1, arm2)
            if pooled_within_group_sd is not None:
                # Formula: n = 2 * SD² / (SE_NMA)²
                effective_sample = 2 * (pooled_within_group_sd**2) / (senma**2)
                return effective_sample
        
        # For binary variables, maintain original logic
        control_event_rate = self._get_control_event_rate(arm1, arm2)
        intervention_event_rate = self._get_intervention_event_rate(arm1, arm2)
        
        if self.data_type == "binary":
            if self.effect_measure == "RR" and control_event_rate is not None:
                return (1/control_event_rate + 1/(estimate_point*control_event_rate) - 2) / (senma**2)
            elif self.effect_measure == "OR" and control_event_rate is not None and intervention_event_rate is not None:
                return (1/control_event_rate + 1/(1-control_event_rate) + 1/intervention_event_rate + 1/(1-intervention_event_rate)) / (senma**2)
        
        return 0  # Default case



    def _calculate_direct_sample_size(self, arm1, arm2) -> int:
        """Calculate the sample size of direct comparison"""
        for i in range(len(self.nettable_data)):
            if (self.nettable_data.iloc[i, 0] == arm1 and self.nettable_data.iloc[i, 1] == arm2) or \
            (self.nettable_data.iloc[i, 0] == arm2 and self.nettable_data.iloc[i, 1] == arm1):
                sample_size_str = self.nettable_data.iloc[i, 3]  # 'Sample_size' column
                if pd.notna(sample_size_str):
                    return int(re.sub(r'[^0-9]', '', str(sample_size_str)) or 0)
        return 0

    def _calculate_ois(self, arm1, arm2, mcid) -> tuple:
        """
        Calculate Optimal Information Size (OIS) and calculation rationale
        
        Parameters:
            arm1, arm2: Two treatments to compare
            mcid: Minimal Clinical Important Difference
            
        Returns:
            (ois, ois_reason): OIS value and calculation rationale
        """
        ois = 800  # Default OIS value
        ois_reason = "Using default OIS = 800"
        
        if mcid <= 0:
            return ois, ois_reason
        
        if self.data_type == "binary":
            # Find control group event rate
            control_event_rate = self._get_control_event_rate(arm1, arm2)
            
            if self.effect_measure == "RR":
                # Calculate OIS for RR
                if control_event_rate is not None:
                    ois = 7.85 * control_event_rate * (1 - control_event_rate) * (1 + 1/mcid) / (control_event_rate * (1 - mcid)**2)
                    ois_reason = f"OIS for RR = 7.85 × p₁({control_event_rate:.3f}) × (1-p₁) × (1 + 1/MCID) / (p₁ × (1-MCID)²) = {ois:.0f}"
            elif self.effect_measure == "OR":
                # Calculate OIS for OR
                intervention_event_rate = self._get_intervention_event_rate(arm1, arm2)
                
                if control_event_rate is not None and intervention_event_rate is not None:
                    ois = 7.85 * ((1/(control_event_rate * (1 - control_event_rate))) + 
                                (1/(intervention_event_rate * (1 - intervention_event_rate)))) / (np.log(mcid))**2
                    ois_reason = f"OIS for OR = 7.85 × [(p₁ × (1-p₁))⁻¹ + (p₂ × (1-p₂))⁻¹] / [ln(MCID)]² = {ois:.0f}"
        else:  # continuous outcome
            # Find control group standard deviation
            pooled_within_group_sd = self._get_pooled_within_group_sd(arm1, arm2)
            
            if pooled_within_group_sd is not None:
                ois = 15.7 * (pooled_within_group_sd**2) / (mcid**2)
                ois_reason = f"OIS for continuous = 15.7 × SD²({pooled_within_group_sd:.3f}²) / MCID²({mcid:.3f}²) = {ois:.0f}"
        
        return ois, ois_reason

    def _calculate_direct_sample_size(self, arm1, arm2) -> int:
        """Calculate the sample size of direct comparison"""
        for i in range(len(self.nettable_data)):
            if (self.nettable_data.iloc[i, 0] == arm1 and self.nettable_data.iloc[i, 1] == arm2) or \
            (self.nettable_data.iloc[i, 0] == arm2 and self.nettable_data.iloc[i, 1] == arm1):
                sample_size_str = self.nettable_data.iloc[i, 3]  # 'Sample_size' column
                if pd.notna(sample_size_str):
                    return int(re.sub(r'[^0-9]', '', str(sample_size_str)) or 0)
        return 0

    def _calculate_ois(self, arm1, arm2, mcid) -> tuple:
        """
        Calculate Optimal Information Size (OIS) and calculation rationale
        
        Parameters:
            arm1, arm2: Two treatments to compare
            mcid: Minimal Clinical Important Difference
            
        Returns:
            (ois, ois_reason): OIS value and calculation rationale
        """
        ois = 800  # Default OIS value
        ois_reason = "Using default OIS = 800"
        
        if mcid <= 0:
            return ois, ois_reason
        
        if self.data_type == "binary":
            # Find control group event rate
            control_event_rate = self._get_control_event_rate(arm1, arm2)
            
            if self.effect_measure == "RR":
                # Calculate OIS for RR
                if control_event_rate is not None:
                    ois = 7.85 * control_event_rate * (1 - control_event_rate) * (1 + 1/mcid) / (control_event_rate * (1 - mcid)**2)
                    ois_reason = f"OIS for RR = 7.85 × p₁({control_event_rate:.3f}) × (1-p₁) × (1 + 1/MCID) / (p₁ × (1-MCID)²) = {ois:.0f}"
            elif self.effect_measure == "OR":
                # Calculate OIS for OR
                intervention_event_rate = self._get_intervention_event_rate(arm1, arm2)
                
                if control_event_rate is not None and intervention_event_rate is not None:
                    ois = 7.85 * ((1/(control_event_rate * (1 - control_event_rate))) + 
                                (1/(intervention_event_rate * (1 - intervention_event_rate)))) / (np.log(mcid))**2
                    ois_reason = f"OIS for OR = 7.85 × [(p₁ × (1-p₁))⁻¹ + (p₂ × (1-p₂))⁻¹] / [ln(MCID)]² = {ois:.0f}"
        else:  # continuous outcome
            # Find control group standard deviation
            pooled_within_group_sd = self._get_pooled_within_group_sd(arm1, arm2)
            
            if pooled_within_group_sd is not None:
                ois = 15.7 * (pooled_within_group_sd**2) / (mcid**2)
                ois_reason = f"OIS for continuous = 15.7 × SD²({pooled_within_group_sd:.3f}²) / MCID²({mcid:.3f}²) = {ois:.0f}"
        
        return ois, ois_reason






    def evaluate_rob(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Risk of Bias (ROB)"""
        # Get parameters
        high_risk_count_threshold = self.rob_params['high_risk_count_threshold']
        high_risk_weight_threshold = self.rob_params['high_risk_weight_threshold']
        very_serious_weight_threshold = self.rob_params['very_serious_weight_threshold']

        # Get study and treatment group data
        studies_with_treatments = self.find_studies_with_treatments()
        
        # Prepare for weight calculation
        if self.meta_result is not None:
            weight_column = 'w.random' if self.model_type == 'random' else 'w.common'
            result_table = self.meta_result
        else:
            weight_column = None
            result_table = None
        
    
        
        # Evaluate ROB for each comparison
        for i in range(len(grade_results)):
            arm1 = grade_results.loc[i, 'Arm_1']
            arm2 = grade_results.loc[i, 'Arm_2']
            study_count = grade_results.loc[i, 'No_of_study']
            
            # Process only rows with direct comparison
            if pd.notna(study_count) and study_count > 0:
                # Find studies containing arm1
                studies_with_arm1 = studies_with_treatments[studies_with_treatments['treatment'] == arm1]['study'].unique()
                
                # Find studies containing arm2
                studies_with_arm2 = studies_with_treatments[studies_with_treatments['treatment'] == arm2]['study'].unique()
                
                # Find studies containing both arm1 and arm2
                common_studies = np.intersect1d(studies_with_arm1, studies_with_arm2)
                
                if len(common_studies) > 0:
                    # Get ROB assessments for these studies
                    rob_assessments = studies_with_treatments[
                        studies_with_treatments['study'].isin(common_studies)
                    ][['study', 'ROB']].drop_duplicates()
                    
                    # Count the number of high-risk studies
                    high_risk_count = sum(rob_assessments['ROB'] == "High")
                    total_studies = len(common_studies)
                    high_risk_proportion = high_risk_count / total_studies if total_studies > 0 else 0
                    
                    # Build comparison string
                    comparison_str = f"{arm1}:{arm2}"
                    comparison_str_reverse = f"{arm2}:{arm1}"
                    
                    # Get study weights
                    high_risk_weight_total = 0
                    total_weight = 0
                    
                    if result_table is not None and weight_column in result_table.columns:
                        # Filter studies for relevant comparison
                        relevant_studies = result_table[
                            (result_table['subgroup'] == comparison_str) | 
                            (result_table['subgroup'] == comparison_str_reverse)
                        ]
                        
                        if len(relevant_studies) > 0:
                            for _, row in relevant_studies.iterrows():
                                study_name = row['studlab']
                                study_weight = row[weight_column]
                                
                                if pd.notna(study_weight):
                                    total_weight += study_weight
                                    
                                    # Check if this study is high risk
                                    is_high_risk = False
                                    for _, rob_row in rob_assessments.iterrows():
                                        if rob_row['study'] == study_name and rob_row['ROB'] == "High":
                                            is_high_risk = True
                                            break
                                    
                                    if is_high_risk:
                                        high_risk_weight_total += study_weight
                    
                    # Calculate high-risk study weight proportion
                    high_risk_weight_percentage = 0
                    if total_weight > 0:
                        high_risk_weight_percentage = (high_risk_weight_total / total_weight) * 100
                        print(f"High risk studies weight percentage: {high_risk_weight_percentage}%")
                    else:
                        print("Warning: Could not calculate weight percentage, total weight is 0 or not available.")
                        # If no weight data, use study count as substitute
                        if high_risk_count > 0:
                            high_risk_weight_percentage = (high_risk_count / total_studies) * 100
                    
                    # Determine ROB rating based on rules (using custom thresholds)
                    if high_risk_weight_percentage >= very_serious_weight_threshold:
                        # Rule 1: High-risk study weight >= very_serious_weight_threshold
                        grade_results.loc[i, 'ROB'] = "Very serious"
                        grade_results.loc[i, 'Reason_for_ROB'] = (
                            f"{high_risk_count} of {total_studies} studies were assessed as having a high "
                            f"risk-of-bias, with their total weight exceeding {very_serious_weight_threshold}%. Therefore, risk-of-bias "
                            f"significantly impacted the certainty of evidence."
                        )
                    elif high_risk_proportion >= high_risk_count_threshold and high_risk_weight_percentage >= high_risk_weight_threshold:
                        # Rule 2: High-risk study proportion >= high_risk_count_threshold and weight >= high_risk_weight_threshold
                        grade_results.loc[i, 'ROB'] = "Serious"
                        grade_results.loc[i, 'Reason_for_ROB'] = (
                            f"{high_risk_count} of {total_studies} studies were assessed as having a high "
                            f"risk-of-bias, with their total weight exceeding {high_risk_weight_threshold}%. Therefore, risk-of-bias "
                            f"may have significantly impacted the certainty of evidence."
                        )
                    elif high_risk_proportion >= high_risk_count_threshold and high_risk_weight_percentage < high_risk_weight_threshold:
                        # Rule 3: High-risk study proportion >= high_risk_count_threshold but weight < high_risk_weight_threshold
                        grade_results.loc[i, 'ROB'] = "Not serious"
                        grade_results.loc[i, 'Reason_for_ROB'] = (
                            f"{high_risk_count} of {total_studies} studies were assessed as having a high "
                            f"risk-of-bias, with their total weight not exceeding {high_risk_weight_threshold}%. Therefore, risk-of-bias "
                            f"may not have significantly impacted the certainty of evidence."
                        )
                    elif high_risk_proportion < high_risk_count_threshold and high_risk_weight_percentage >= high_risk_weight_threshold:
                        # Rule 4: High-risk study proportion < high_risk_count_threshold but weight >= high_risk_weight_threshold
                        grade_results.loc[i, 'ROB'] = "Serious"
                        grade_results.loc[i, 'Reason_for_ROB'] = (
                            f"{high_risk_count} of {total_studies} studies were assessed as having a high "
                            f"risk-of-bias, but their total weight exceeding {high_risk_weight_threshold}%. Therefore, risk-of-bias "
                            f"may have significantly impacted the certainty of evidence."
                        )
                    else:
                        # Rule 5: High-risk study proportion < high_risk_count_threshold and weight < high_risk_weight_threshold
                        grade_results.loc[i, 'ROB'] = "Not serious"
                        grade_results.loc[i, 'Reason_for_ROB'] = (
                            f"{high_risk_count} of {total_studies} studies were assessed as having a high "
                            f"risk-of-bias, with their total weight not exceeding {high_risk_weight_threshold}%. Therefore, risk-of-bias "
                            f"may not have significantly impacted the certainty of evidence."
                        )
                else:
                    grade_results.loc[i, 'ROB'] = "Not applicable"
                    grade_results.loc[i, 'Reason_for_ROB'] = "No direct comparison available."
        
        return grade_results

    
    def evaluate_inconsistency(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Inconsistency"""
        # Get parameters
        i2_threshold = self.inconsistency_params['i2_threshold']
        i2_very_serious_threshold = self.inconsistency_params['i2_very_serious_threshold']
        ci_overlap_threshold = self.inconsistency_params['ci_overlap_threshold']
        
        for i in range(len(grade_results)):
            study_count = grade_results.loc[i, 'No_of_study']
            arm1 = grade_results.loc[i, 'Arm_1']
            arm2 = grade_results.loc[i, 'Arm_2']
            
            # Process only rows with direct comparison
            if pd.notna(study_count) and study_count > 0:
                # Get I2 value from nettable
                i2_value = grade_results.loc[i, 'I2']
                
                # Extract numeric part of I2
                i2_numeric = np.nan
                if pd.notna(i2_value):
                    # If it's a string, try to extract the numeric part
                    if isinstance(i2_value, str):
                        # Extract numeric part (remove percentage sign and other non-numeric characters)
                        i2_extracted = re.sub(r'[^0-9\.]', '', i2_value)
                        print(f"Row {i} - Original I2: {i2_value} - Extracted: {i2_extracted}")
                        
                        # Ensure the extracted string is in valid numeric format
                        if i2_extracted and not pd.isna(i2_extracted):
                            try:
                                i2_numeric = float(i2_extracted)
                            except ValueError:
                                print(f"Warning: Could not convert I2 value to numeric: {i2_value}")
                                i2_numeric = np.nan
                    elif isinstance(i2_value, (int, float)):
                        # If already numeric, use directly
                        i2_numeric = float(i2_value)
                
                # If I2 value is NA or number of studies <=1, set to Not serious
                if pd.isna(i2_numeric) or study_count <= 1:
                    grade_results.loc[i, 'Inconsistency'] = "Not serious"
                    grade_results.loc[i, 'Reason_for_Inconsistency'] = "Insufficient studies for heterogeneity assessment."
                elif i2_numeric > i2_very_serious_threshold:
                    # If I2 > i2_very_serious_threshold, directly determine as Very serious
                    grade_results.loc[i, 'Inconsistency'] = "Very serious"
                    grade_results.loc[i, 'Reason_for_Inconsistency'] = f"I² = {i2_numeric}%, exceeding {i2_very_serious_threshold}%, indicating obversely heterogeneity."
                elif i2_numeric <= i2_threshold:
                    # If I2 <= i2_threshold, determine as Not serious
                    grade_results.loc[i, 'Inconsistency'] = "Not serious"
                    grade_results.loc[i, 'Reason_for_Inconsistency'] = f"I² = {i2_numeric}%, below {i2_threshold}%, indicating no significant heterogeneity."
                else:
                    # If i2_threshold < I2 <= i2_very_serious_threshold, further analysis needed
                    # Build comparison string
                    comparison_str = f"{arm1}:{arm2}"
                    comparison_str_reverse = f"{arm2}:{arm1}"
                    
                    # Filter relevant direct comparisons
                    relevant_comparisons = self.pairwise_data[
                        (self.pairwise_data['subgroup'] == comparison_str) | 
                        (self.pairwise_data['subgroup'] == comparison_str_reverse)
                    ]
                    
                    if len(relevant_comparisons) > 0:
                        # Check if all point estimates are on the same side of the null effect line
                        null_effect_line = 1 if self.data_type == "binary" else 0
                        all_same_side = all(relevant_comparisons['TE'] >= null_effect_line) or all(relevant_comparisons['TE'] <= null_effect_line)
                        
                        # Check 95% CI overlap
                        has_sufficient_overlap = False
                        if len(relevant_comparisons) > 1:
                            # Calculate CI overlap for each pair of studies
                            overlap_count = 0
                            total_pairs = 0
                            
                            for j in range(len(relevant_comparisons)-1):
                                for k in range(j+1, len(relevant_comparisons)):
                                    study1_lower = relevant_comparisons.iloc[j]['lower']
                                    study1_upper = relevant_comparisons.iloc[j]['upper']
                                    study2_lower = relevant_comparisons.iloc[k]['lower']
                                    study2_upper = relevant_comparisons.iloc[k]['upper']
                                    
                                    # Calculate overlap interval length
                                    overlap_length = min(study1_upper, study2_upper) - max(study1_lower, study2_lower)
                                    if overlap_length > 0:
                                        # Calculate total length of both CIs
                                        study1_length = study1_upper - study1_lower
                                        study2_length = study2_upper - study2_lower
                                        
                                        # Calculate overlap ratio (relative to the shorter CI)
                                        overlap_ratio = overlap_length / min(study1_length, study2_length)
                                        
                                        if overlap_ratio >= ci_overlap_threshold:
                                            overlap_count += 1
                                    total_pairs += 1
                            
                            # If all pairs have overlap >= ci_overlap_threshold, consider sufficient overlap
                            has_sufficient_overlap = (overlap_count == total_pairs)
                        else:
                            # Only one study, no overlap issue
                            has_sufficient_overlap = True
                        
                        # Determine Inconsistency based on conditions
                        if all_same_side or has_sufficient_overlap:
                            grade_results.loc[i, 'Inconsistency'] = "Not serious"
                            reason = f"I² = {i2_numeric}% (between {i2_threshold}% and {i2_very_serious_threshold}%), but "
                            if all_same_side:
                                reason += "all point estimates are on the same side of the line of no effect"
                            if has_sufficient_overlap:
                                if all_same_side:
                                    reason += " and "
                                reason += f"there is sufficient overlap (>={ci_overlap_threshold*100}%) between confidence intervals"
                            reason += "."
                            grade_results.loc[i, 'Reason_for_Inconsistency'] = reason
                        else:
                            grade_results.loc[i, 'Inconsistency'] = "Serious"
                            grade_results.loc[i, 'Reason_for_Inconsistency'] = (
                                f"I² = {i2_numeric}% (between {i2_threshold}% and {i2_very_serious_threshold}%), indicating significant heterogeneity. "
                                f"Additionally, point estimates vary in direction and confidence intervals have insufficient overlap (<{ci_overlap_threshold*100}%)."
                            )
                    else:
                        # No relevant direct comparisons found
                        grade_results.loc[i, 'Inconsistency'] = "Not serious"
                        grade_results.loc[i, 'Reason_for_Inconsistency'] = "No direct comparisons found in the network."
        
        return grade_results

    
    def evaluate_indirectness(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Indirectness"""
        for i in range(len(grade_results)):
            study_count = grade_results.loc[i, 'No_of_study']
            
            # Process only rows with direct comparison
            if pd.notna(study_count) and study_count > 0:
                grade_results.loc[i, 'Indirectness'] = "Not serious"
                grade_results.loc[i, 'Reason_for_Indirectness'] = "By default, INDIRECTNESS is not serious and needs to be checked manually"
        
        return grade_results
    
    def evaluate_publication_bias(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Publication Bias"""
        
        # Attempt to load Egger test results file
        egger_file = os.path.join(self.model_dir, f"{self.outcome_name}-egger_test_results.csv")
        egger_data = None
        
        if os.path.exists(egger_file):
            try:
                egger_data = pd.read_csv(egger_file)
                print(f"Successfully loaded Egger test results file: {egger_file}")
            except Exception as e:
                print(f"Error loading Egger test results file: {e}")
                egger_data = None
        else:
            print(f"Egger test results file not found: {egger_file}")
        
        for i in range(len(grade_results)):
            study_count = grade_results.loc[i, 'No_of_study']
            arm1 = grade_results.loc[i, 'Arm_1']
            arm2 = grade_results.loc[i, 'Arm_2']
            
            # Process only rows with direct comparison
            if pd.notna(study_count) and study_count > 0:
                if study_count < 10:
                    grade_results.loc[i, 'Publication_bias'] = "Undetected"
                    grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                        "Less than 10 studies were included and were not tested for publication bias."
                    )
                else:
                    # For direct comparisons with >=10 studies, find Egger test results
                    comparison_found = False
                    egger_p_value = None
                    
                    if egger_data is not None:
                        # Build comparison string (both possible orders)
                        comparison_str1 = f"{arm1}:{arm2}"
                        comparison_str2 = f"{arm2}:{arm1}"
                        
                        # Find corresponding comparison in Egger test results
                        matching_rows = egger_data[
                            (egger_data['comparison'] == comparison_str1) | 
                            (egger_data['comparison'] == comparison_str2)
                        ]
                        
                        if len(matching_rows) > 0:
                            comparison_found = True
                            egger_p_value = matching_rows.iloc[0]['p_egger']
                            
                            # Check if p-value is a valid numeric
                            if pd.notna(egger_p_value):
                                try:
                                    egger_p_value = float(egger_p_value)
                                    
                                    # Determine publication bias based on Egger test p-value
                                    if egger_p_value < 0.05:
                                        grade_results.loc[i, 'Publication_bias'] = "Serious"
                                        grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                            f"Egger's test showed significant asymmetry (p = {egger_p_value:.4f}), "
                                            f"suggesting possible publication bias."
                                        )
                                    else:
                                        grade_results.loc[i, 'Publication_bias'] = "Not serious"
                                        grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                            f"Egger's test showed no significant asymmetry (p = {egger_p_value:.4f}), "
                                            f"suggesting no evidence of publication bias."
                                        )
                                except (ValueError, TypeError):
                                    # p-value cannot be converted to numeric
                                    grade_results.loc[i, 'Publication_bias'] = "Undetected"
                                    grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                        f"Egger's test could not be performed or p-value is invalid "
                                        f"(p = {egger_p_value}). Publication bias assessment inconclusive."
                                    )
                            else:
                                # p-value is NA
                                reason = matching_rows.iloc[0]['reason'] if 'reason' in matching_rows.columns else "Unknown reason"
                                grade_results.loc[i, 'Publication_bias'] = "Undetected"
                                grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                    f"Egger's test could not be performed: {reason}. "
                                    f"Publication bias assessment inconclusive."
                                )
                    
                    # If corresponding comparison not found in Egger test results, use original logic
                    if not comparison_found:
                        # Build comparison string
                        comparison_str = f"{arm1}:{arm2}"
                        comparison_str_reverse = f"{arm2}:{arm1}"
                        
                        # Filter relevant direct comparisons
                        relevant_comparisons = self.pairwise_data[
                            (self.pairwise_data['subgroup'] == comparison_str) | 
                            (self.pairwise_data['subgroup'] == comparison_str_reverse)
                        ]
                        
                        if len(relevant_comparisons) > 0:
                            if len(relevant_comparisons) >= 10:
                                # In 10 or more studies, uneven distribution of results may indicate publication bias
                                positive_results = sum(relevant_comparisons['TE'] > 0)
                                negative_results = sum(relevant_comparisons['TE'] < 0)
                                ratio = max(positive_results, negative_results) / len(relevant_comparisons)
                                
                                if ratio > 0.8:  # If >80% of studies have results in the same direction
                                    grade_results.loc[i, 'Publication_bias'] = "Serious"
                                    grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                        f"Distribution of study results is uneven ({ratio:.2f}), with "
                                        f"{max(positive_results, negative_results)} of {len(relevant_comparisons)} "
                                        f"studies showing the same direction, suggesting possible publication bias."
                                    )
                                else:
                                    grade_results.loc[i, 'Publication_bias'] = "Not serious"
                                    grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                        f"Distribution of study results is relatively even, with "
                                        f"{positive_results} positive and {negative_results} negative results."
                                    )
                            else:
                                grade_results.loc[i, 'Publication_bias'] = "Undetected"
                                grade_results.loc[i, 'Reason_for_Publication_bias'] = (
                                    f"Only {len(relevant_comparisons)} studies available for publication bias assessment, "
                                    f"which is insufficient for a reliable test."
                                )
                        else:
                            grade_results.loc[i, 'Publication_bias'] = "Undetected"
                            grade_results.loc[i, 'Reason_for_Publication_bias'] = "No direct comparisons found for publication bias assessment."
        
        return grade_results

        


    def calculate_direct_rating(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Calculate Direct_rating_without_imprecision"""
        for i in range(len(grade_results)):
            study_count = grade_results.loc[i, 'No_of_study']
            
            # Process only rows with direct comparison
            if pd.notna(study_count) and study_count > 0:
                # Starting rating is High
                rating_level = "High"
                downgrade_count = 0
                
                # Check ROB
                if pd.notna(grade_results.loc[i, 'ROB']):
                    if grade_results.loc[i, 'ROB'] == "Serious":
                        downgrade_count += 1
                    elif grade_results.loc[i, 'ROB'] == "Very serious":
                        downgrade_count += 2
                
                # Check Inconsistency
                if pd.notna(grade_results.loc[i, 'Inconsistency']):
                    if grade_results.loc[i, 'Inconsistency'] == "Serious":
                        downgrade_count += 1
                    elif grade_results.loc[i, 'Inconsistency'] == "Very serious":
                        downgrade_count += 2
                
                # Check Indirectness
                if pd.notna(grade_results.loc[i, 'Indirectness']):
                    if grade_results.loc[i, 'Indirectness'] == "Serious":
                        downgrade_count += 1
                    elif grade_results.loc[i, 'Indirectness'] == "Very serious":
                        downgrade_count += 2
                
                # Check Publication_bias
                if pd.notna(grade_results.loc[i, 'Publication_bias']):
                    if grade_results.loc[i, 'Publication_bias'] == "Serious":
                        downgrade_count += 1
                    elif grade_results.loc[i, 'Publication_bias'] == "Very serious":
                        downgrade_count += 2
                
                # Determine final rating based on number of downgrades
                if downgrade_count == 0:
                    rating_level = "High"
                elif downgrade_count == 1:
                    rating_level = "Moderate"
                elif downgrade_count == 2:
                    rating_level = "Low"
                elif downgrade_count >= 3:
                    rating_level = "Very low"
                
                # Set final rating
                grade_results.loc[i, 'Direct_rating_without_imprecision'] = rating_level
        
        return grade_results
    
    def find_most_contributing_loop(self, arm1: str, arm2: str, grade_results: pd.DataFrame) -> dict:
        """Find the most contributing first-order loop (supports triangles and quadrilaterals)"""
        # Get all directly compared intervention pairs
        direct_comparisons = grade_results[pd.notna(grade_results['No_of_study']) & (grade_results['No_of_study'] > 0)]
        direct_comparisons = direct_comparisons[['Arm_1', 'Arm_2', 'Sample_size']]
        
        # All possible nodes
        all_nodes = pd.unique(pd.concat([direct_comparisons['Arm_1'], direct_comparisons['Arm_2']]))
        
        # Remove the two nodes of the current comparison to get potential bridge nodes
        potential_bridges = [node for node in all_nodes if node != arm1 and node != arm2]
        
        max_sample_size = 0
        best_path = None
        best_bridge = None
        best_path_type = None  # Record if it's a triangle or quadrilateral
        
        # First try triangular paths (original logic)
        for bridge in potential_bridges:
            # Check arm1-bridge connection
            arm1_bridge_rows = direct_comparisons[
                ((direct_comparisons['Arm_1'] == arm1) & (direct_comparisons['Arm_2'] == bridge)) |
                ((direct_comparisons['Arm_1'] == bridge) & (direct_comparisons['Arm_2'] == arm1))
            ]
            
            # Check bridge-arm2 connection
            bridge_arm2_rows = direct_comparisons[
                ((direct_comparisons['Arm_1'] == bridge) & (direct_comparisons['Arm_2'] == arm2)) |
                ((direct_comparisons['Arm_1'] == arm2) & (direct_comparisons['Arm_2'] == bridge))
            ]
            
            if len(arm1_bridge_rows) > 0 and len(bridge_arm2_rows) > 0:
                # Extract and convert sample size to numeric
                arm1_bridge_sample_str = arm1_bridge_rows.iloc[0]['Sample_size']
                bridge_arm2_sample_str = bridge_arm2_rows.iloc[0]['Sample_size']
                
                # Extract numeric part
                arm1_bridge_sample = int(re.sub(r'[^0-9]', '', str(arm1_bridge_sample_str)) or 0)
                bridge_arm2_sample = int(re.sub(r'[^0-9]', '', str(bridge_arm2_sample_str)) or 0)
                
                # Calculate total sample size
                total_sample_size = arm1_bridge_sample + bridge_arm2_sample
                
                # Update best path
                if total_sample_size > max_sample_size:
                    max_sample_size = total_sample_size
                    best_bridge = bridge
                    
                    # Format path
                    path1 = f"{arm1} - {bridge}"
                    path2 = f"{bridge} - {arm2}"
                    best_path = f"{path1}; {path2}"
                    best_path_type = "triangle"
        
        # If no triangular path found, try quadrilateral path
        if best_path is None:
            # Look for quadrilateral path: arm1 - bridge1 - bridge2 - arm2
            for bridge1 in potential_bridges:
                for bridge2 in potential_bridges:
                    if bridge1 == bridge2:
                        continue
                    
                    # Check arm1-bridge1 connection
                    arm1_bridge1_rows = direct_comparisons[
                        ((direct_comparisons['Arm_1'] == arm1) & (direct_comparisons['Arm_2'] == bridge1)) |
                        ((direct_comparisons['Arm_1'] == bridge1) & (direct_comparisons['Arm_2'] == arm1))
                    ]
                    
                    # Check bridge1-bridge2 connection
                    bridge1_bridge2_rows = direct_comparisons[
                        ((direct_comparisons['Arm_1'] == bridge1) & (direct_comparisons['Arm_2'] == bridge2)) |
                        ((direct_comparisons['Arm_1'] == bridge2) & (direct_comparisons['Arm_2'] == bridge1))
                    ]
                    
                    # Check bridge2-arm2 connection
                    bridge2_arm2_rows = direct_comparisons[
                        ((direct_comparisons['Arm_1'] == bridge2) & (direct_comparisons['Arm_2'] == arm2)) |
                        ((direct_comparisons['Arm_1'] == arm2) & (direct_comparisons['Arm_2'] == bridge2))
                    ]
                    
                    if len(arm1_bridge1_rows) > 0 and len(bridge1_bridge2_rows) > 0 and len(bridge2_arm2_rows) > 0:
                        # Extract and convert sample size to numeric
                        arm1_bridge1_sample_str = arm1_bridge1_rows.iloc[0]['Sample_size']
                        bridge1_bridge2_sample_str = bridge1_bridge2_rows.iloc[0]['Sample_size']
                        bridge2_arm2_sample_str = bridge2_arm2_rows.iloc[0]['Sample_size']
                        
                        # Extract numeric part
                        arm1_bridge1_sample = int(re.sub(r'[^0-9]', '', str(arm1_bridge1_sample_str)) or 0)
                        bridge1_bridge2_sample = int(re.sub(r'[^0-9]', '', str(bridge1_bridge2_sample_str)) or 0)
                        bridge2_arm2_sample = int(re.sub(r'[^0-9]', '', str(bridge2_arm2_sample_str)) or 0)
                        
                        # Calculate total sample size
                        total_sample_size = arm1_bridge1_sample + bridge1_bridge2_sample + bridge2_arm2_sample
                        
                        # Update best path
                        if total_sample_size > max_sample_size:
                            max_sample_size = total_sample_size
                            best_bridge = [bridge1, bridge2]  # Store two bridge nodes
                            
                            # Format path
                            path1 = f"{arm1} - {bridge1}"
                            path2 = f"{bridge1} - {bridge2}"
                            path3 = f"{bridge2} - {arm2}"
                            best_path = f"{path1}; {path2}; {path3}"
                            best_path_type = "quadrilateral"
        
        return {
            "path": best_path,
            "total_sample": max_sample_size,
            "bridge": best_bridge,
            "path_type": best_path_type
        }

    def evaluate_indirect_evidence(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate indirect evidence (supports triangular and quadrilateral paths)"""
        # First add new columns, but with initial empty values
        if 'Certainty_of_evidence_for_arm3' not in grade_results.columns:
            grade_results.insert(
                grade_results.columns.get_loc('Certainty_of_evidence_for_arm2') + 1,
                'Certainty_of_evidence_for_arm3',
                pd.NA  # Initial value is empty
            )
        
        for i in range(len(grade_results)):
            arm1 = grade_results.loc[i, 'Arm_1']
            arm2 = grade_results.loc[i, 'Arm_2']
            
            # Check if Indirect_estimate has content (contains numbers)
            indirect_estimate = grade_results.loc[i, 'Indirect_estimate']
            has_indirect_estimate = False
            
            # Safely check if indirect_estimate is valid
            if pd.notna(indirect_estimate) and str(indirect_estimate) != "." and str(indirect_estimate) != "" and re.search(r'[0-9]', str(indirect_estimate)):
                has_indirect_estimate = True
            
            # Perform evaluation as long as there is indirect comparison result
            if has_indirect_estimate:
                print(f"Processing indirect evidence for row {i}: {arm1} vs {arm2}")
                print(f"Indirect estimate: {indirect_estimate}")
                
                try:
                    # Find the most contributing first-order loop
                    loop_info = self.find_most_contributing_loop(arm1, arm2, grade_results)
                    
                    # Fill in the most contributing first-order loop
                    grade_results.loc[i, 'First_order_loop_of_the_most_contribution'] = loop_info.get("path")
                    
                    # Get path type and bridge nodes
                    path_type = loop_info.get("path_type")
                    bridge_treatment = loop_info.get("bridge")
                    
                    # Initialize evidence ratings
                    arm1_evidence = None
                    arm2_evidence = None
                    arm3_evidence = None
                    
                    if path_type == "triangle" and bridge_treatment:
                        # Triangular path: arm1 - bridge - arm2
                        # Find evidence rating for arm1 vs bridge
                        arm1_rows = grade_results[
                            ((grade_results['Arm_1'] == arm1) & (grade_results['Arm_2'] == bridge_treatment)) |
                            ((grade_results['Arm_1'] == bridge_treatment) & (grade_results['Arm_2'] == arm1))
                        ]
                        
                        if len(arm1_rows) > 0:
                            arm1_evidence = arm1_rows.iloc[0]['Direct_rating_without_imprecision']
                        
                        # Find evidence rating for arm2 vs bridge
                        arm2_rows = grade_results[
                            ((grade_results['Arm_1'] == arm2) & (grade_results['Arm_2'] == bridge_treatment)) |
                            ((grade_results['Arm_1'] == bridge_treatment) & (grade_results['Arm_2'] == arm2))
                        ]
                        
                        if len(arm2_rows) > 0:
                            arm2_evidence = arm2_rows.iloc[0]['Direct_rating_without_imprecision']
                        
                        # Triangular path does not require a third arm
                        arm3_evidence = "Not available"
                    
                    elif path_type == "quadrilateral" and isinstance(bridge_treatment, list) and len(bridge_treatment) == 2:
                        # Quadrilateral path: arm1 - bridge1 - bridge2 - arm2
                        bridge1, bridge2 = bridge_treatment
                        
                        # Find evidence rating for arm1 vs bridge1
                        arm1_rows = grade_results[
                            ((grade_results['Arm_1'] == arm1) & (grade_results['Arm_2'] == bridge1)) |
                            ((grade_results['Arm_1'] == bridge1) & (grade_results['Arm_2'] == arm1))
                        ]
                        
                        if len(arm1_rows) > 0:
                            arm1_evidence = arm1_rows.iloc[0]['Direct_rating_without_imprecision']
                        
                        # Find evidence rating for bridge1 vs bridge2
                        arm2_rows = grade_results[
                            ((grade_results['Arm_1'] == bridge1) & (grade_results['Arm_2'] == bridge2)) |
                            ((grade_results['Arm_1'] == bridge2) & (grade_results['Arm_2'] == bridge1))
                        ]
                        
                        if len(arm2_rows) > 0:
                            arm2_evidence = arm2_rows.iloc[0]['Direct_rating_without_imprecision']
                        
                        # Find evidence rating for bridge2 vs arm2
                        arm3_rows = grade_results[
                            ((grade_results['Arm_1'] == bridge2) & (grade_results['Arm_2'] == arm2)) |
                            ((grade_results['Arm_1'] == arm2) & (grade_results['Arm_2'] == bridge2))
                        ]
                        
                        if len(arm3_rows) > 0:
                            arm3_evidence = arm3_rows.iloc[0]['Direct_rating_without_imprecision']
                    
                    else:
                        # If no suitable path found, fall back to using reference treatment
                        if self.ref_treatment:
                            # Find comparison between arm1 and reference treatment
                            arm1_ref_rows = grade_results[
                                ((grade_results['Arm_1'] == arm1) & (grade_results['Arm_2'] == self.ref_treatment)) |
                                ((grade_results['Arm_1'] == self.ref_treatment) & (grade_results['Arm_2'] == arm1))
                            ]
                            
                            if len(arm1_ref_rows) > 0:
                                arm1_evidence = arm1_ref_rows.iloc[0]['Direct_rating_without_imprecision']
                            
                            # Find comparison between arm2 and reference treatment
                            arm2_ref_rows = grade_results[
                                ((grade_results['Arm_1'] == arm2) & (grade_results['Arm_2'] == self.ref_treatment)) |
                                ((grade_results['Arm_1'] == self.ref_treatment) & (grade_results['Arm_2'] == arm2))
                            ]
                            
                            if len(arm2_ref_rows) > 0:
                                arm2_evidence = arm2_ref_rows.iloc[0]['Direct_rating_without_imprecision']
                            
                            arm3_evidence = "Not available"
                    
                    # Fill in results, ensuring they are not None
                    grade_results.loc[i, 'Certainty_of_evidence_for_arm1'] = "Unrated" if arm1_evidence is None or pd.isna(arm1_evidence) else arm1_evidence
                    grade_results.loc[i, 'Certainty_of_evidence_for_arm2'] = "Unrated" if arm2_evidence is None or pd.isna(arm2_evidence) else arm2_evidence
                    grade_results.loc[i, 'Certainty_of_evidence_for_arm3'] = "Not available" if arm3_evidence is None or pd.isna(arm3_evidence) else arm3_evidence
                    
                    # Fill in Intransitivity
                    grade_results.loc[i, 'Intransitivity'] = "Not serious"
                    grade_results.loc[i, 'Reason_for_Intransitivity'] = "By default, INTRANSITIVITY is not severe. Please manually check for differences in basic characteristics between studies."
                    
                    # Fill in Indirect_rating_without_imprecision
                    # Collect all valid evidence ratings
                    valid_evidences = []
                    for evidence in [arm1_evidence, arm2_evidence, arm3_evidence]:
                        if evidence is not None and pd.notna(evidence) and evidence not in ["Unrated", "Not available"]:
                            valid_evidences.append(evidence)
                    
                    if valid_evidences:
                        evidence_levels = ["High", "Moderate", "Low", "Very low"]
                        
                        try:
                            # Find the lowest evidence rating (highest index value)
                            evidence_indices = [evidence_levels.index(evidence) for evidence in valid_evidences]
                            lowest_rating_index = max(evidence_indices)
                            lower_rating = evidence_levels[lowest_rating_index]
                            
                            # Check Intransitivity, if "Serious", downgrade by one more level
                            if grade_results.loc[i, 'Intransitivity'] == "Serious":
                                if lowest_rating_index < len(evidence_levels) - 1:
                                    lower_rating = evidence_levels[lowest_rating_index + 1]
                            
                            grade_results.loc[i, 'Indirect_rating_without_imprecision'] = lower_rating
                        except ValueError:
                            # Handle case where rating not found in list
                            grade_results.loc[i, 'Indirect_rating_without_imprecision'] = None
                    else:
                        grade_results.loc[i, 'Indirect_rating_without_imprecision'] = None
                
                except Exception as e:
                    print(f"Error in processing indirect evidence for row {i}: {e}")
                    grade_results.loc[i, 'First_order_loop_of_the_most_contribution'] = f"Error: {str(e)}"
                    grade_results.loc[i, 'Certainty_of_evidence_for_arm1'] = "Error"
                    grade_results.loc[i, 'Certainty_of_evidence_for_arm2'] = "Error"
                    grade_results.loc[i, 'Certainty_of_evidence_for_arm3'] = "Error"
            
            # Note: If no indirect evidence, do not set Certainty_of_evidence_for_arm3, keep it empty (pd.NA)
        
        return grade_results

    
    def calculate_higher_rating(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Calculate Higher_rating_of_direct_and_indirect_without_imprecision"""
        for i in range(len(grade_results)):
            direct_rating = grade_results.loc[i, 'Direct_rating_without_imprecision']
            indirect_rating = grade_results.loc[i, 'Indirect_rating_without_imprecision']
            
            if pd.notna(direct_rating) and pd.notna(indirect_rating):
                evidence_levels = ["High", "Moderate", "Low", "Very low"]
                
                try:
                    direct_level = evidence_levels.index(direct_rating)
                    indirect_level = evidence_levels.index(indirect_rating)
                    
                    # Choose the higher rating (lower index value)
                    if direct_level <= indirect_level:  # When indices are the same, prefer direct_rating
                        grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision'] = direct_rating
                    else:
                        grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision'] = indirect_rating
                except ValueError:
                    # Handle case where one or both ratings not in predefined list
                    if pd.notna(direct_rating):
                        grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision'] = direct_rating
                    elif pd.notna(indirect_rating):
                        grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision'] = indirect_rating
            elif pd.notna(direct_rating):
                grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision'] = direct_rating
            elif pd.notna(indirect_rating):
                grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision'] = indirect_rating
        
        return grade_results

    def evaluate_incoherence(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Incoherence"""
        for i in range(len(grade_results)):
            # Get Incoherence p-value string
            incoherence_str = grade_results.loc[i, 'Reason_for_Incoherence']
            incoherence_value = np.nan
            is_small_p = False
            
            # If not "." and not NA, try to parse p-value
            if pd.notna(incoherence_str) and incoherence_str != ".":
                # Check for small p-value notation like "<0.0001"
                if isinstance(incoherence_str, str) and '<' in incoherence_str:
                    is_small_p = True
                    print(f"Row {i} - Detected small p-value notation: {incoherence_str}")
                else:
                    try:
                        incoherence_value = float(incoherence_str)
                    except (ValueError, TypeError):
                        incoherence_value = np.nan
            
            # Output debug info
            print(f"Row {i} - Incoherence string: {incoherence_str} - Converted value: {incoherence_value}, Is small p: {is_small_p}")
            
            # Set Incoherence based on p-value
            if is_small_p:
                # If expressed as less than a value, consider p-value significant
                grade_results.loc[i, 'Incoherence'] = "Serious"
                print("  Setting to Serious (p is very small)")
            elif pd.isna(incoherence_value):
                # If cannot convert to numeric, default to Not serious
                grade_results.loc[i, 'Incoherence'] = "Not serious"
                print("  Setting to Not serious (NA value)")
            elif incoherence_value < 0.05:
                # p < 0.05 indicates significant incoherence
                grade_results.loc[i, 'Incoherence'] = "Serious"
                print("  Setting to Serious (p < 0.05)")
            else:
                # p >= 0.05 indicates no significant incoherence
                grade_results.loc[i, 'Incoherence'] = "Not serious"
                print("  Setting to Not serious (p >= 0.05)")
        
        return grade_results
    
    def evaluate_incoherence(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Incoherence"""
        for i in range(len(grade_results)):
            # Get Incoherence p-value string
            incoherence_str = grade_results.loc[i, 'Reason_for_Incoherence']
            incoherence_value = np.nan
            is_small_p = False
            
            # If not "." and not NA, try to parse p-value
            if pd.notna(incoherence_str) and incoherence_str != ".":
                # Check for small p-value notation like "<0.0001"
                if isinstance(incoherence_str, str) and '<' in incoherence_str:
                    is_small_p = True
                    print(f"Row {i} - Detected small p-value notation: {incoherence_str}")
                else:
                    try:
                        incoherence_value = float(incoherence_str)
                    except (ValueError, TypeError):
                        incoherence_value = np.nan
            
            # Output debug info
            print(f"Row {i} - Incoherence string: {incoherence_str} - Converted value: {incoherence_value}, Is small p: {is_small_p}")
            
            # Set Incoherence based on p-value
            if is_small_p:
                # If expressed as less than a value, consider p-value significant
                grade_results.loc[i, 'Incoherence'] = "Serious"
                print("  Setting to Serious (p is very small)")
            elif pd.isna(incoherence_value):
                # If cannot convert to numeric, default to Not serious
                grade_results.loc[i, 'Incoherence'] = "Not serious"
                print("  Setting to Not serious (NA value)")
            elif incoherence_value < 0.05:
                # p < 0.05 indicates significant incoherence
                grade_results.loc[i, 'Incoherence'] = "Serious"
                print("  Setting to Serious (p < 0.05)")
            else:
                # p >= 0.05 indicates no significant incoherence
                grade_results.loc[i, 'Incoherence'] = "Not serious"
                print("  Setting to Not serious (p >= 0.05)")
        
        return grade_results

    
    def evaluate_imprecision(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Evaluate Imprecision"""
        # Precompute sample sizes and OIS for all comparisons
        precomputed_data = self.precompute_sample_sizes_and_ois()
        
        for i in range(len(grade_results)):
            arm1 = grade_results.loc[i, 'Arm_1']
            arm2 = grade_results.loc[i, 'Arm_2']
            pair_key = (arm1, arm2)
            
            # Get starting rating
            start_rating = grade_results.loc[i, 'Higher_rating_of_direct_and_indirect_without_imprecision']
            if pd.isna(start_rating):
                continue
            
            # Determine which type of evidence to use
            # If only direct evidence, use direct evidence
            direct_rating = grade_results.loc[i, 'Direct_rating_without_imprecision']
            indirect_rating = grade_results.loc[i, 'Indirect_rating_without_imprecision']
            
            if pd.notna(direct_rating) and pd.isna(indirect_rating):
                evidence_type = "direct"
            # If only indirect evidence, use indirect evidence
            elif pd.isna(direct_rating) and pd.notna(indirect_rating):
                evidence_type = "indirect"
            # If there is incoherence, compare the quality of direct and indirect evidence
            elif pd.notna(grade_results.loc[i, 'Incoherence']) and grade_results.loc[i, 'Incoherence'] == "Serious":
                if pd.notna(direct_rating) and pd.notna(indirect_rating):
                    evidence_levels = ["High", "Moderate", "Low", "Very low"]
                    try:
                        direct_level = evidence_levels.index(direct_rating)
                        indirect_level = evidence_levels.index(indirect_rating)
                        
                        if direct_level <= indirect_level:  # Direct evidence is better or equal
                            evidence_type = "direct"
                        else:  # Indirect evidence is better
                            evidence_type = "indirect"
                    except ValueError:
                        evidence_type = "network"  # Default to network evidence
                else:
                    evidence_type = "network"
            else:
                evidence_type = "network"  # Default to network evidence
            
            # Store the evidence type used for final rating
            grade_results.loc[i, 'Evidence_type_for_final_rating'] = evidence_type
            
            # Get corresponding sample size and OIS
            if pair_key in precomputed_data:
                data = precomputed_data[pair_key]
                
                if evidence_type == "direct":
                    sample_size = data['direct_sample_size']
                elif evidence_type == "indirect":
                    sample_size = data['indirect_sample_size']
                else:  # network
                    sample_size = data['network_sample_size']
                
                ois = data['ois']
                ois_reason = data['ois_reason']
            else:
                # Use default values if precomputed data not found
                sample_size = 0
                ois = 800
                ois_reason = "Using default OIS = 800"
            
            # Extract estimate and CI
            if evidence_type == "direct":
                estimate_str = grade_results.loc[i, 'Direct_estimate']
            elif evidence_type == "indirect":
                estimate_str = grade_results.loc[i, 'Indirect_estimate']
            else:
                estimate_str = grade_results.loc[i, 'Network_meta_analysis']
            
            # Extract point estimate and CI from estimate string
            point_estimate = None
            ci_lower = None
            ci_upper = None
            
            if pd.notna(estimate_str):
                # Extract point estimate
                point_match = re.search(r'^([0-9.-]+)', str(estimate_str))
                if point_match:
                    try:
                        point_estimate = float(point_match.group(1).strip())
                    except ValueError:
                        pass
                
                # Extract CI
                ci_match = re.search(r'\[(.*?);(.*?)\]', str(estimate_str))
                if ci_match:
                    try:
                        ci_lower = float(ci_match.group(1).strip())
                        ci_upper = float(ci_match.group(2).strip())
                    except ValueError:
                        pass
            
            # Get MID values
            harmful_mid = self.mid_params.get('harmful_mid')
            benefit_mid = self.mid_params.get('benefit_mid')
            
            # Evaluate imprecision
            imprecision_rating = "Not serious"  # Default no downgrade
            imprecision_downgrade = 0
            reasons = []
            
            # Check CI in relation to thresholds
            ci_issue = False
            
            if pd.notna(ci_lower) and pd.notna(ci_upper) and harmful_mid is not None and benefit_mid is not None:
                # Handle different data types
                if self.data_type == "binary":
                    # Binary outcomes (OR/RR)
                    null_value = 1
                    
                    # Determine threshold directions
                    harmful_dir = ">" if harmful_mid > 1 else "<"
                    benefit_dir = ">" if benefit_mid > 1 else "<"
                    
                    # Calculate 1.5x thresholds (maintaining direction)
                    harmful_threshold_1_5 = harmful_mid * 1.5 if harmful_dir == ">" else harmful_mid / 1.5
                    benefit_threshold_1_5 = benefit_mid * 1.5 if benefit_dir == ">" else benefit_mid / 1.5
                    
                    # Check threshold crossing (direction-aware)
                    def crosses_threshold(ci_l, ci_u, threshold, direction):
                        if direction == ">":
                            return ci_l < threshold < ci_u
                        return ci_u < threshold < ci_l
                    
                else:
                    # Continuous outcomes (MD/SMD)
                    null_value = 0
                    
                    # Determine threshold directions (assuming absolute values)
                    harmful_sign = 1 if harmful_mid > 0 else -1
                    benefit_sign = 1 if benefit_mid > 0 else -1
                    
                    # Calculate 1.5x thresholds
                    harmful_threshold_1_5 = harmful_mid * 1.5
                    benefit_threshold_1_5 = benefit_mid * 1.5
                    
                    # Check threshold crossing
                    def crosses_threshold(ci_l, ci_u, threshold):
                        return (ci_l < threshold < ci_u) if threshold > 0 else (ci_u < threshold < ci_l)
                
                # Apply the appropriate crossing check
                crosses_harmful_1_5 = crosses_threshold(ci_lower, ci_upper, harmful_threshold_1_5, harmful_dir) if self.data_type == "binary" else crosses_threshold(ci_lower, ci_upper, harmful_threshold_1_5)
                crosses_benefit_1_5 = crosses_threshold(ci_lower, ci_upper, benefit_threshold_1_5, benefit_dir) if self.data_type == "binary" else crosses_threshold(ci_lower, ci_upper, benefit_threshold_1_5)
                crosses_harmful = crosses_threshold(ci_lower, ci_upper, harmful_mid, harmful_dir) if self.data_type == "binary" else crosses_threshold(ci_lower, ci_upper, harmful_mid * harmful_sign)
                crosses_benefit = crosses_threshold(ci_lower, ci_upper, benefit_mid, benefit_dir) if self.data_type == "binary" else crosses_threshold(ci_lower, ci_upper, benefit_mid * benefit_sign)
                
                # Evaluate crossing scenarios
                if crosses_harmful_1_5 and crosses_benefit_1_5:
                    reasons.append(f"95% CI [{ci_lower:.3f}; {ci_upper:.3f}] crosses both 1.5x harmful threshold ({harmful_threshold_1_5:.3f}) and 1.5x benefit threshold ({benefit_threshold_1_5:.3f})")
                    imprecision_rating = "Extremely serious"
                    imprecision_downgrade += 3
                    ci_issue = True
                elif crosses_harmful and crosses_benefit:
                    reasons.append(f"95% CI [{ci_lower:.3f}; {ci_upper:.3f}] crosses both harmful threshold ({harmful_mid:.3f}) and benefit threshold ({benefit_mid:.3f})")
                    imprecision_rating = "Very serious"
                    imprecision_downgrade += 2
                    ci_issue = True
                elif crosses_harmful or crosses_benefit:
                    threshold_type = "harmful" if crosses_harmful else "benefit"
                    threshold_val = harmful_mid if crosses_harmful else benefit_mid
                    reasons.append(f"95% CI [{ci_lower:.3f}; {ci_upper:.3f}] crosses the {threshold_type} threshold ({threshold_val:.3f})")
                    imprecision_rating = "Serious"
                    imprecision_downgrade += 1
                    ci_issue = True
                else:
                    reasons.append(f"95% CI [{ci_lower:.3f}; {ci_upper:.3f}] does not cross any decision thresholds")
            
            elif pd.notna(ci_lower) and pd.notna(ci_upper):
                # No MID values provided - check null line crossing
                null_value = 1 if self.data_type == "binary" else 0
                crosses_null = (ci_lower < null_value < ci_upper) if null_value != 0 else (
                    (ci_lower < 0 < ci_upper) if self.data_type == "continuous" else False
                )
                
                if crosses_null:
                    reasons.append(f"95% CI [{ci_lower:.3f}; {ci_upper:.3f}] crosses the line of no effect ({null_value})")
                    imprecision_rating = "Serious"
                    imprecision_downgrade += 1
                    ci_issue = True
                else:
                    reasons.append(f"95% CI [{ci_lower:.3f}; {ci_upper:.3f}] does not cross the line of no effect ({null_value})")

            
            # Check CI width in relation to point estimate (for categorical variables not crossing null/MID)
            if not ci_issue and pd.notna(ci_lower) and pd.notna(ci_upper) and pd.notna(point_estimate) and self.data_type == "binary":
                # Check if OR or RR effect measure
                if self.effect_measure == "OR" or self.effect_measure == "RR":
                    # Calculate ratio of CI upper to lower limit, then divide by point estimate
                    ci_ratio = ci_upper / ci_lower
                    ci_width_ratio = ci_ratio / point_estimate
                    
                    if self.effect_measure == "RR" and ci_width_ratio >= 3:
                        reasons.append(f"The ratio of the upper to lower limits of the 95% CI is more than 3 times the point estimate, indicating that the sample size is almost certainly insufficient to meet the optimal information size")
                        imprecision_rating = "Serious"
                        imprecision_downgrade += 1
                        ci_issue = True
                    elif self.effect_measure == "OR" and ci_width_ratio >= 2.5:
                        reasons.append(f"The ratio of the upper to lower limits of the 95% CI is more than 2.5 times the point estimate, indicating that the sample size is almost certainly insufficient to meet the optimal information size")
                        imprecision_rating = "Serious"
                        imprecision_downgrade += 1
                        ci_issue = True

            
            # If CI did not cause downgrade, add OIS and sample size comparison
            if not ci_issue:
                reasons.append(f"{ois_reason}")
                
                if sample_size < ois:
                    reasons.append(f"{evidence_type.capitalize()} effective sample size is {sample_size:.0f}, which is below the optimal information size ({ois:.0f})")
                    # Downgrade due to insufficient sample size if CI did not cause downgrade
                    imprecision_rating = "Serious"
                    imprecision_downgrade += 1
                else:
                    reasons.append(f"{evidence_type.capitalize()} effective sample size is {sample_size:.0f}, which meets or exceeds the optimal information size ({ois:.0f})")
            
            # Set results
            grade_results.loc[i, 'Reason_for_Imprecision'] = ". ".join(reasons)
            grade_results.loc[i, 'Imprecision'] = imprecision_rating
            
            # Calculate final rating
            final_rating_level = start_rating
            evidence_levels = ["High", "Moderate", "Low", "Very low"]
            
            if pd.notna(start_rating) and start_rating in evidence_levels:
                start_index = evidence_levels.index(start_rating)
                
                # Check if need to downgrade due to incoherence
                if evidence_type == "network" and pd.notna(grade_results.loc[i, 'Incoherence']) and grade_results.loc[i, 'Incoherence'] == "Serious":
                    # Network evidence with incoherence, downgrade by one more level
                    downgrade_count = imprecision_downgrade + 1
                else:
                    downgrade_count = imprecision_downgrade
                
                # Calculate final index
                final_index = min(start_index + downgrade_count, len(evidence_levels) - 1)
                final_rating_level = evidence_levels[final_index]
            
            grade_results.loc[i, 'Final_rating'] = final_rating_level
        
        return grade_results






    def _get_control_event_rate(self, arm1, arm2):
        """Get control group event rate"""
        # For A vs B comparison, B is the control group
        control_arm = arm2
        
        # Get event rate for the treatment corresponding to the control group from original data
        if hasattr(self, 'original_data'):
            control_data = self.original_data[self.original_data['treatment'] == control_arm]
            if not control_data.empty:
                # Calculate event rate
                total_events = control_data['event'].sum() if 'event' in control_data.columns else 0
                total_sample = control_data['n'].sum() if 'n' in control_data.columns else 0
                
                if total_sample > 0:
                    return total_events / total_sample
        
        # Return None if cannot be obtained
        return None

    def _get_intervention_event_rate(self, arm1, arm2):
        """Get intervention group event rate"""
        # For A vs B comparison, A is the intervention group
        intervention_arm = arm1
        
        # Get event rate for the treatment corresponding to the intervention group from original data
        if hasattr(self, 'original_data'):
            intervention_data = self.original_data[self.original_data['treatment'] == intervention_arm]
            if not intervention_data.empty:
                # Calculate event rate
                total_events = intervention_data['event'].sum() if 'event' in intervention_data.columns else 0
                total_sample = intervention_data['n'].sum() if 'n' in intervention_data.columns else 0
                
                if total_sample > 0:
                    return total_events / total_sample
        
        # Return None if cannot be obtained
        return None

    def _get_pooled_within_group_sd(self, arm1, arm2):
        """
        Calculate the pooled within-group standard deviation (SD) for all groups in the direct comparison (Arm1 vs Arm2)
        Meets GRADE-NMA requirements for continuous variables
        """
        # 1. Get study data for direct comparison (all groups including Arm1 and Arm2)
        direct_studies = self._get_direct_studies_for_pair(arm1, arm2)
        if direct_studies.empty or 'sd' not in direct_studies.columns or 'n' not in direct_studies.columns:
            return None
        # 2. Extract SD and sample size for all groups (including Arm1 and Arm2)
        sd_list = direct_studies['sd'].astype(float)
        n_list = direct_studies['n'].astype(int)
        # 3. Calculate pooled standard deviation (formula: sqrt[Σ(SD_i² × (n_i-1)) / (Σn_i - k)])
        sum_of_squares = (sd_list ** 2 * (n_list - 1)).sum()
        total_n = n_list.sum()
        k = len(n_list)  # Total number of groups (all groups in Arm1 and Arm2)
        pooled_sd = np.sqrt(sum_of_squares / (total_n - k))
        return pooled_sd
    
    def _get_direct_studies_for_pair(self, arm1, arm2):
        """Get all study data for direct comparison of Arm1 vs Arm2 (including raw data for both groups)"""
        studies_with_both = set(
            self.original_data[self.original_data['treatment'] == arm1]['study']
        ) & set(
            self.original_data[self.original_data['treatment'] == arm2]['study']
        )
        return self.original_data[
            self.original_data['study'].isin(studies_with_both) & 
            self.original_data['treatment'].isin([arm1, arm2])
        ]



    
    def calculate_final_rating(self, grade_results: pd.DataFrame) -> pd.DataFrame:
        """Calculate final rating and rationale"""
        print("Starting calculate_final_rating function...")
        
        for i in range(len(grade_results)):
            # Get used evidence type
            evidence_type = grade_results.loc[i, 'Evidence_type_for_final_rating']
            
            # If evidence_type does not exist, determine appropriate evidence type
            if pd.isna(evidence_type):
                direct_rating = grade_results.loc[i, 'Direct_rating_without_imprecision']
                indirect_rating = grade_results.loc[i, 'Indirect_rating_without_imprecision']
                
                if pd.notna(direct_rating) and pd.isna(indirect_rating):
                    evidence_type = "direct"
                elif pd.isna(direct_rating) and pd.notna(indirect_rating):
                    evidence_type = "indirect"
                else:
                    evidence_type = "network"
                
                grade_results.loc[i, 'Evidence_type_for_final_rating'] = evidence_type
            
            # Print debug info
            print(f"Row {i}: Evidence type = {evidence_type}")
            
            # Set final rationale based on evidence type
            if evidence_type == "network":
                # When using network evidence, consider Incoherence
                incoherence = grade_results.loc[i, 'Incoherence']
                incoherence_downgrade = ""
                
                if pd.notna(incoherence) and incoherence == "Serious":
                    incoherence_downgrade = " The rating was further downgraded due to significant incoherence between direct and indirect estimates."
                
                grade_results.loc[i, 'Final_rating_reason'] = (
                    f"NMA estimate was used because direct and indirect evidence were consistent. "
                    f"Imprecision was rated as {grade_results.loc[i, 'Imprecision']}.{incoherence_downgrade}"
                )
            elif evidence_type == "direct":
                # When using direct evidence, no further downgrade for Incoherence
                grade_results.loc[i, 'Final_rating_reason'] = (
                    f"Direct estimate was used because {
                        'no indirect evidence was available' if pd.isna(grade_results.loc[i, 'Indirect_rating_without_imprecision']) else 
                        'incoherence was significant and direct evidence had higher or equal certainty'
                    }. "
                    f"Imprecision was rated as {grade_results.loc[i, 'Imprecision']}."
                )
            elif evidence_type == "indirect":
                # When using indirect evidence, no further downgrade for Incoherence
                grade_results.loc[i, 'Final_rating_reason'] = (
                    f"Indirect estimate was used because {
                        'no direct evidence was available' if pd.isna(grade_results.loc[i, 'Direct_rating_without_imprecision']) else 
                        'incoherence was significant and indirect evidence had higher certainty'
                    }. "
                    f"Imprecision was rated as {grade_results.loc[i, 'Imprecision']}."
                )
            else:
                # If no evidence type specified, use default explanation
                grade_results.loc[i, 'Final_rating_reason'] = (
                    f"Final rating was determined based on available evidence. "
                    f"Imprecision was rated as {grade_results.loc[i, 'Imprecision']}."
                )
        
        print("Finished calculate_final_rating function")
        return grade_results



    
    def evaluate_grade(self) -> pd.DataFrame:
        """Execute the complete GRADE evaluation process"""
        # Prepare GRADE framework
        grade_results = self.prepare_grade_framework()
        
        # First round: Evaluate direct comparisons
        grade_results = self.evaluate_rob(grade_results)
        grade_results = self.evaluate_inconsistency(grade_results)
        grade_results = self.evaluate_indirectness(grade_results)
        grade_results = self.evaluate_publication_bias(grade_results)
        grade_results = self.calculate_direct_rating(grade_results)
        
        # Second round: Evaluate indirect comparisons
        grade_results = self.evaluate_indirect_evidence(grade_results)
        
        # Third round: Comprehensive evaluation
        grade_results = self.evaluate_incoherence(grade_results)
        grade_results = self.calculate_higher_rating(grade_results)
        grade_results = self.evaluate_imprecision(grade_results)
        grade_results = self.calculate_final_rating(grade_results)  # Ensure this line exists
        
        return grade_results

    
    def save_grade_results(self, grade_results: pd.DataFrame) -> str:
        """Save GRADE evaluation results"""
        output_file = os.path.join(self.model_dir, f"{self.outcome_name}-GRADE Evaluation Results.xlsx")
        grade_results.to_excel(output_file, index=False)
        print(f"GRADE evaluation results saved to: {output_file}")
        return output_file


def run_grade_evaluation(base_dir, outcome_name, model_type="random", ask_for_mid=False, 
                         rob_params=None, inconsistency_params=None):
    """
    Convenient function to run GRADE evaluation in a notebook
    """
    # Simplify output
    print(f"Starting GRADE evaluation for {outcome_name} (using {model_type} model)")
    
    try:
        # Create evaluator
        evaluator = GradeEvaluator(
            base_dir=base_dir,
            outcome_name=outcome_name,
            model_type=model_type,
            ask_for_mid=ask_for_mid,
            rob_params=rob_params,
            inconsistency_params=inconsistency_params
        )
        
        # Perform evaluation
        grade_results = evaluator.evaluate_grade()
        
        # Save results
        output_file = evaluator.save_grade_results(grade_results)
        
        print(f"GRADE evaluation completed, results saved")
        
        return grade_results, output_file
        
    except Exception as e:
        print(f"GRADE evaluation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def list_available_outcomes(base_dir):
    """
    List all available outcomes for evaluation
    
    Parameters:
        base_dir: Base directory containing NMA analysis results
    
    Returns:
        available_outcomes: List of available outcomes
    """
    available_outcomes = []
    
    if os.path.exists(base_dir):
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                # Check if there are random and fixed effect subdirectories
                has_random = os.path.exists(os.path.join(item_path, "Results of Random Effect Model"))
                has_fixed = os.path.exists(os.path.join(item_path, "Results of Common Effect Model"))
                
                models = []
                if has_random:
                    models.append("random")
                if has_fixed:
                    models.append("fixed")
                
                if models:
                    available_outcomes.append({"outcome": item, "models": models})
    
    return available_outcomes