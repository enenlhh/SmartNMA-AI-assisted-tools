# =========================
# Data Validation Module
# =========================
# This module provides data quality checking functions for NMA data
# Supports both binary and continuous outcome data validation

# Load required libraries
if (!require(dplyr)) {
  install.packages("dplyr")
  library(dplyr)
}

# =========================
# Core Validation Function
# =========================

#' Validate Data Quality
#' 
#' Main function to validate data quality for both binary and continuous data
#' 
#' @param data Data frame containing the study data
#' @param filename Character string of the filename being validated
#' @param data_type Character string: "binary" or "continuous"
#' @return List containing validation results
validate_data_quality <- function(data, filename, data_type) {
  # Initialize results structure
  issues <- data.frame(
    file = character(0),
    issue_type = character(0),
    row_number = integer(0),
    study = character(0),
    treatment = character(0),
    description = character(0),
    severity = character(0),
    stringsAsFactors = FALSE
  )
  
  # Validate input parameters
  if (missing(data) || is.null(data) || nrow(data) == 0) {
    return(list(
      is_valid = FALSE,
      issues = data.frame(
        file = filename,
        issue_type = "empty_data",
        row_number = NA,
        study = NA,
        treatment = NA,
        description = "Data is empty or missing",
        severity = "error",
        stringsAsFactors = FALSE
      ),
      summary = list(
        total_issues = 1,
        error_count = 1,
        warning_count = 0
      )
    ))
  }
  
  if (!data_type %in% c("binary", "continuous")) {
    stop("data_type must be either 'binary' or 'continuous'")
  }
  
  # Check required columns exist
  required_cols_common <- c("study", "treatment")
  required_cols_binary <- c("event", "n")
  required_cols_continuous <- c("n", "mean", "sd")
  
  if (data_type == "binary") {
    required_cols <- c(required_cols_common, required_cols_binary)
  } else {
    required_cols <- c(required_cols_common, required_cols_continuous)
  }
  
  missing_cols <- setdiff(required_cols, names(data))
  if (length(missing_cols) > 0) {
    return(list(
      is_valid = FALSE,
      issues = data.frame(
        file = filename,
        issue_type = "missing_columns",
        row_number = NA,
        study = NA,
        treatment = NA,
        description = paste("Missing required columns:", paste(missing_cols, collapse = ", ")),
        severity = "error",
        stringsAsFactors = FALSE
      ),
      summary = list(
        total_issues = 1,
        error_count = 1,
        warning_count = 0
      )
    ))
  }
  
  # Run specific validation checks based on data type
  if (data_type == "binary") {
    # Check event vs n
    event_issues <- check_event_vs_n(data, filename)
    if (nrow(event_issues) > 0) {
      issues <- rbind(issues, event_issues)
    }
  } else if (data_type == "continuous") {
    # Check zero standard deviation
    sd_issues <- check_zero_sd(data, filename)
    if (nrow(sd_issues) > 0) {
      issues <- rbind(issues, sd_issues)
    }
  }
  
  # Check for duplicate treatments within studies (common for both types)
  duplicate_issues <- check_duplicate_treatments(data, filename)
  if (nrow(duplicate_issues) > 0) {
    issues <- rbind(issues, duplicate_issues)
  }
  
  # Calculate summary statistics
  error_count <- sum(issues$severity == "error")
  warning_count <- sum(issues$severity == "warning")
  total_issues <- nrow(issues)
  
  # Determine overall validation status
  is_valid <- error_count == 0
  
  return(list(
    is_valid = is_valid,
    issues = issues,
    summary = list(
      total_issues = total_issues,
      error_count = error_count,
      warning_count = warning_count
    )
  ))
}

# =========================
# Specific Check Functions
# =========================

#' Check Event vs N for Binary Data
#' 
#' Checks if event count exceeds total sample size in binary data
#' 
#' @param data Data frame containing binary outcome data
#' @param filename Character string of the filename being validated
#' @return Data frame of issues found
check_event_vs_n <- function(data, filename) {
  issues <- data.frame(
    file = character(0),
    issue_type = character(0),
    row_number = integer(0),
    study = character(0),
    treatment = character(0),
    description = character(0),
    severity = character(0),
    stringsAsFactors = FALSE
  )
  
  # Check if required columns exist
  if (!all(c("event", "n") %in% names(data))) {
    return(issues)
  }
  
  # Find rows where event > n
  problematic_rows <- which(data$event > data$n)
  
  if (length(problematic_rows) > 0) {
    for (row_idx in problematic_rows) {
      issues <- rbind(issues, data.frame(
        file = filename,
        issue_type = "event_exceeds_n",
        row_number = row_idx,
        study = as.character(data$study[row_idx]),
        treatment = as.character(data$treatment[row_idx]),
        description = sprintf("Event count (%d) exceeds sample size (%d)", 
                              data$event[row_idx], data$n[row_idx]),
        severity = "error",
        stringsAsFactors = FALSE
      ))
    }
  }
  
  return(issues)
}

#' Check Zero Standard Deviation for Continuous Data
#' 
#' Checks if standard deviation is zero in continuous data
#' 
#' @param data Data frame containing continuous outcome data
#' @param filename Character string of the filename being validated
#' @return Data frame of issues found
check_zero_sd <- function(data, filename) {
  issues <- data.frame(
    file = character(0),
    issue_type = character(0),
    row_number = integer(0),
    study = character(0),
    treatment = character(0),
    description = character(0),
    severity = character(0),
    stringsAsFactors = FALSE
  )
  
  # Check if required column exists
  if (!"sd" %in% names(data)) {
    return(issues)
  }
  
  # Find rows where sd = 0
  problematic_rows <- which(data$sd == 0)
  
  if (length(problematic_rows) > 0) {
    for (row_idx in problematic_rows) {
      issues <- rbind(issues, data.frame(
        file = filename,
        issue_type = "zero_sd",
        row_number = row_idx,
        study = as.character(data$study[row_idx]),
        treatment = as.character(data$treatment[row_idx]),
        description = "Standard deviation is zero, which may cause analysis issues",
        severity = "warning",
        stringsAsFactors = FALSE
      ))
    }
  }
  
  return(issues)
}

#' Check Duplicate Treatments within Studies
#' 
#' Checks if the same treatment appears multiple times within a single study
#' 
#' @param data Data frame containing study data
#' @param filename Character string of the filename being validated
#' @return Data frame of issues found
check_duplicate_treatments <- function(data, filename) {
  issues <- data.frame(
    file = character(0),
    issue_type = character(0),
    row_number = integer(0),
    study = character(0),
    treatment = character(0),
    description = character(0),
    severity = character(0),
    stringsAsFactors = FALSE
  )
  
  # Check if required columns exist
  if (!all(c("study", "treatment") %in% names(data))) {
    return(issues)
  }
  
  # Find duplicate study-treatment combinations
  data$row_id <- seq_len(nrow(data))
  duplicates <- data %>%
    group_by(study, treatment) %>%
    filter(n() > 1) %>%
    ungroup()
  
  if (nrow(duplicates) > 0) {
    for (i in seq_len(nrow(duplicates))) {
      issues <- rbind(issues, data.frame(
        file = filename,
        issue_type = "duplicate_treatment",
        row_number = duplicates$row_id[i],
        study = as.character(duplicates$study[i]),
        treatment = as.character(duplicates$treatment[i]),
        description = sprintf("Treatment '%s' appears multiple times in study '%s'", 
                              duplicates$treatment[i], duplicates$study[i]),
        severity = "error",
        stringsAsFactors = FALSE
      ))
    }
  }
  
  return(issues)
}

# =========================
# Data Characteristics Analysis Module
# =========================

#' Analyze Data Characteristics
#' 
#' Main function to analyze data characteristics for both binary and continuous data
#' Calculates study count, treatment count, network density, connectivity, and type-specific metrics
#' 
#' @param data Data frame containing the study data
#' @param data_type Character string: "binary" or "continuous"
#' @return List containing comprehensive data characteristics
analyze_data_characteristics <- function(data, data_type) {
  # Validate input parameters
  if (missing(data) || is.null(data) || nrow(data) == 0) {
    stop("Data is empty or missing")
  }
  
  if (!data_type %in% c("binary", "continuous")) {
    stop("data_type must be either 'binary' or 'continuous'")
  }
  
  # Check required columns exist
  required_cols_common <- c("study", "treatment", "n")
  if (!all(required_cols_common %in% names(data))) {
    missing_cols <- setdiff(required_cols_common, names(data))
    stop(paste("Missing required columns:", paste(missing_cols, collapse = ", ")))
  }
  
  # Calculate basic statistics
  basic_stats <- calculate_basic_stats(data)
  
  # Calculate network statistics
  network_stats <- calculate_network_stats(data)
  
  # Calculate type-specific statistics
  if (data_type == "binary") {
    type_specific_stats <- calculate_binary_specific_stats(data)
  } else {
    type_specific_stats <- calculate_continuous_specific_stats(data)
  }
  
  # Calculate overall complexity score
  complexity_score <- calculate_complexity_score(basic_stats, network_stats, type_specific_stats, data_type)
  
  return(list(
    data_type = data_type,
    basic_stats = basic_stats,
    network_stats = network_stats,
    type_specific_stats = type_specific_stats,
    complexity_score = complexity_score
  ))
}

#' Calculate Basic Statistics
#' 
#' Calculates fundamental statistics about the dataset
#' 
#' @param data Data frame containing the study data
#' @return List containing basic statistics
calculate_basic_stats <- function(data) {
  study_count <- length(unique(data$study))
  treatment_count <- length(unique(data$treatment))
  total_sample_size <- sum(data$n, na.rm = TRUE)
  avg_study_size <- mean(aggregate(n ~ study, data, sum)$n, na.rm = TRUE)
  
  return(list(
    study_count = study_count,
    treatment_count = treatment_count,
    total_sample_size = total_sample_size,
    avg_study_size = round(avg_study_size, 2)
  ))
}

#' Calculate Network Statistics
#' 
#' Calculates network-related statistics including density and connectivity
#' 
#' @param data Data frame containing the study data
#' @return List containing network statistics
calculate_network_stats <- function(data) {
  # Create treatment pairs from the data
  all_pairs <- data.frame(treatment1 = character(0), treatment2 = character(0), stringsAsFactors = FALSE)
  
  # For each study, create all possible treatment pairs
  for (study in unique(data$study)) {
    study_treatments <- unique(data$treatment[data$study == study])
    
    if (length(study_treatments) > 1) {
      # Generate all combinations of treatments in this study
      pairs <- combn(study_treatments, 2, simplify = FALSE)
      study_pairs <- data.frame(
        treatment1 = sapply(pairs, function(x) x[1]),
        treatment2 = sapply(pairs, function(x) x[2]),
        stringsAsFactors = FALSE
      )
      all_pairs <- rbind(all_pairs, study_pairs)
    }
  }
  
  # Remove duplicate pairs (same comparison from different studies)
  if (nrow(all_pairs) > 0) {
    # Standardize pair order (alphabetical)
    all_pairs$pair_key <- paste(
      pmin(all_pairs$treatment1, all_pairs$treatment2),
      pmax(all_pairs$treatment1, all_pairs$treatment2),
      sep = "-"
    )
    unique_pairs <- unique(all_pairs$pair_key)
    actual_comparisons <- length(unique_pairs)
  } else {
    actual_comparisons <- 0
  }
  
  # Calculate network density
  unique_treatments <- unique(data$treatment)
  n_treatments <- length(unique_treatments)
  possible_comparisons <- n_treatments * (n_treatments - 1) / 2
  
  density <- if (possible_comparisons > 0) actual_comparisons / possible_comparisons else 0
  
  # Check network connectivity
  connectivity_result <- check_network_connectivity(data)
  
  # Calculate network diameter (longest shortest path)
  diameter <- calculate_network_diameter(data)
  
  return(list(
    density = round(density, 3),
    connectivity = connectivity_result$is_connected,
    actual_comparisons = actual_comparisons,
    possible_comparisons = possible_comparisons,
    diameter = diameter,
    disconnected_components = connectivity_result$components
  ))
}

#' Check Network Connectivity
#' 
#' Checks if the treatment network is fully connected using graph theory
#' 
#' @param data Data frame containing the study data
#' @return List containing connectivity information
check_network_connectivity <- function(data) {
  # Create adjacency list representation
  treatments <- unique(data$treatment)
  
  if (length(treatments) <= 1) {
    return(list(
      is_connected = FALSE,  # Single treatment or no treatments can't be "connected"
      component_count = length(treatments),
      components = if (length(treatments) == 1) list(treatments) else list()
    ))
  }
  
  adj_list <- setNames(vector("list", length(treatments)), treatments)
  
  # Build adjacency list from studies
  for (study in unique(data$study)) {
    study_treatments <- data$treatment[data$study == study]
    study_treatments <- unique(study_treatments)
    
    # Add edges between all treatments in the same study
    for (i in seq_along(study_treatments)) {
      for (j in seq_along(study_treatments)) {
        if (i != j) {
          treatment_i <- study_treatments[i]
          treatment_j <- study_treatments[j]
          if (!treatment_j %in% adj_list[[treatment_i]]) {
            adj_list[[treatment_i]] <- c(adj_list[[treatment_i]], treatment_j)
          }
        }
      }
    }
  }
  
  # Perform DFS to check connectivity
  visited <- setNames(rep(FALSE, length(treatments)), treatments)
  components <- list()
  component_count <- 0
  
  for (treatment in treatments) {
    if (!visited[treatment]) {
      component_count <- component_count + 1
      component_result <- dfs_component(treatment, adj_list, visited)
      components[[component_count]] <- component_result$component
      visited <- component_result$visited
    }
  }
  
  is_connected <- component_count == 1
  
  return(list(
    is_connected = is_connected,
    component_count = component_count,
    components = components
  ))
}

#' Depth-First Search for Connected Components
#' 
#' Helper function for connectivity analysis
#' 
#' @param start Starting treatment node
#' @param adj_list Adjacency list representation of the network
#' @param visited Named logical vector tracking visited nodes
#' @return List containing component and updated visited vector
dfs_component <- function(start, adj_list, visited) {
  stack <- c(start)
  component <- c()
  
  while (length(stack) > 0) {
    current <- stack[length(stack)]
    stack <- stack[-length(stack)]
    
    if (!visited[current]) {
      visited[current] <- TRUE
      component <- c(component, current)
      
      # Add unvisited neighbors to stack
      neighbors <- adj_list[[current]]
      if (!is.null(neighbors) && length(neighbors) > 0) {
        for (neighbor in neighbors) {
          if (!visited[neighbor]) {
            stack <- c(stack, neighbor)
          }
        }
      }
    }
  }
  
  return(list(
    component = component,
    visited = visited
  ))
}

#' Calculate Network Diameter
#' 
#' Calculates the longest shortest path in the network
#' 
#' @param data Data frame containing the study data
#' @return Integer representing the network diameter
calculate_network_diameter <- function(data) {
  treatments <- unique(data$treatment)
  n_treatments <- length(treatments)
  
  if (n_treatments <= 1) return(0)
  
  # Create distance matrix
  dist_matrix <- matrix(Inf, nrow = n_treatments, ncol = n_treatments)
  rownames(dist_matrix) <- treatments
  colnames(dist_matrix) <- treatments
  
  # Initialize diagonal to 0
  diag(dist_matrix) <- 0
  
  # Set direct connections to distance 1
  for (study in unique(data$study)) {
    study_treatments <- unique(data$treatment[data$study == study])
    for (i in seq_along(study_treatments)) {
      for (j in seq_along(study_treatments)) {
        if (i != j) {
          dist_matrix[study_treatments[i], study_treatments[j]] <- 1
        }
      }
    }
  }
  
  # Floyd-Warshall algorithm for shortest paths
  for (k in treatments) {
    for (i in treatments) {
      for (j in treatments) {
        if (dist_matrix[i, k] + dist_matrix[k, j] < dist_matrix[i, j]) {
          dist_matrix[i, j] <- dist_matrix[i, k] + dist_matrix[k, j]
        }
      }
    }
  }
  
  # Find maximum finite distance
  finite_distances <- dist_matrix[is.finite(dist_matrix) & dist_matrix > 0]
  diameter <- if (length(finite_distances) > 0) max(finite_distances) else 0
  
  return(diameter)
}

#' Calculate Binary-Specific Statistics
#' 
#' Calculates statistics specific to binary outcome data
#' 
#' @param data Data frame containing binary outcome data
#' @return List containing binary-specific statistics
calculate_binary_specific_stats <- function(data) {
  # Check if required columns exist
  if (!all(c("event", "n") %in% names(data))) {
    return(list(
      zero_event_studies = NA,
      zero_event_proportion = NA,
      average_event_rate = NA,
      event_rate_range = c(NA, NA),
      total_events = NA,
      total_participants = NA
    ))
  }
  
  # Calculate event rates for each row
  data$event_rate <- data$event / data$n
  
  # Count zero event studies
  zero_event_studies <- sum(data$event == 0, na.rm = TRUE)
  zero_event_proportion <- zero_event_studies / nrow(data)
  
  # Calculate average event rate
  average_event_rate <- mean(data$event_rate, na.rm = TRUE)
  
  # Calculate event rate range
  event_rate_range <- c(min(data$event_rate, na.rm = TRUE), max(data$event_rate, na.rm = TRUE))
  
  # Calculate totals
  total_events <- sum(data$event, na.rm = TRUE)
  total_participants <- sum(data$n, na.rm = TRUE)
  
  return(list(
    zero_event_studies = zero_event_studies,
    zero_event_proportion = round(zero_event_proportion, 3),
    average_event_rate = round(average_event_rate, 3),
    event_rate_range = round(event_rate_range, 3),
    total_events = total_events,
    total_participants = total_participants
  ))
}

#' Calculate Continuous-Specific Statistics
#' 
#' Calculates statistics specific to continuous outcome data
#' 
#' @param data Data frame containing continuous outcome data
#' @return List containing continuous-specific statistics
calculate_continuous_specific_stats <- function(data) {
  # Check if required columns exist
  if (!all(c("mean", "sd") %in% names(data))) {
    return(list(
      zero_sd_count = NA,
      zero_sd_proportion = NA,
      mean_range = c(NA, NA),
      sd_range = c(NA, NA),
      cv_range = c(NA, NA),
      pooled_mean = NA,
      pooled_sd = NA
    ))
  }
  
  # Count zero standard deviations
  zero_sd_count <- sum(data$sd == 0, na.rm = TRUE)
  zero_sd_proportion <- zero_sd_count / nrow(data)
  
  # Calculate ranges
  mean_range <- c(min(data$mean, na.rm = TRUE), max(data$mean, na.rm = TRUE))
  sd_range <- c(min(data$sd, na.rm = TRUE), max(data$sd, na.rm = TRUE))
  
  # Calculate coefficient of variation (CV) for each row
  data$cv <- data$sd / abs(data$mean)
  data$cv[is.infinite(data$cv) | is.nan(data$cv)] <- NA
  cv_range <- c(min(data$cv, na.rm = TRUE), max(data$cv, na.rm = TRUE))
  
  # Calculate pooled statistics (weighted by sample size)
  total_n <- sum(data$n, na.rm = TRUE)
  pooled_mean <- sum(data$mean * data$n, na.rm = TRUE) / total_n
  
  # Pooled standard deviation calculation
  pooled_variance <- sum((data$n - 1) * data$sd^2, na.rm = TRUE) / (total_n - length(data$n))
  pooled_sd <- sqrt(pooled_variance)
  
  return(list(
    zero_sd_count = zero_sd_count,
    zero_sd_proportion = round(zero_sd_proportion, 3),
    mean_range = round(mean_range, 3),
    sd_range = round(sd_range, 3),
    cv_range = round(cv_range, 3),
    pooled_mean = round(pooled_mean, 3),
    pooled_sd = round(pooled_sd, 3)
  ))
}

#' Calculate Complexity Score
#' 
#' Calculates an overall complexity score for the dataset
#' 
#' @param basic_stats List of basic statistics
#' @param network_stats List of network statistics
#' @param type_specific_stats List of type-specific statistics
#' @param data_type Character string indicating data type
#' @return Numeric complexity score (0-100)
calculate_complexity_score <- function(basic_stats, network_stats, type_specific_stats, data_type) {
  score <- 0
  
  # Study count contribution (0-25 points)
  study_score <- min(basic_stats$study_count / 20 * 25, 25)
  score <- score + study_score
  
  # Treatment count contribution (0-25 points)
  treatment_score <- min(basic_stats$treatment_count / 10 * 25, 25)
  score <- score + treatment_score
  
  # Network density contribution (0-20 points)
  density_score <- network_stats$density * 20
  score <- score + density_score
  
  # Connectivity penalty (-10 points if not connected)
  if (!network_stats$connectivity) {
    score <- score - 10
  }
  
  # Type-specific contributions (0-30 points)
  if (data_type == "binary") {
    # Penalize high zero event proportion
    zero_event_penalty <- type_specific_stats$zero_event_proportion * 15
    score <- score - zero_event_penalty
    
    # Reward balanced event rates
    if (!is.na(type_specific_stats$average_event_rate)) {
      balance_score <- 15 * (1 - abs(type_specific_stats$average_event_rate - 0.5) * 2)
      score <- score + balance_score
    }
  } else {
    # Penalize zero standard deviations
    zero_sd_penalty <- type_specific_stats$zero_sd_proportion * 15
    score <- score - zero_sd_penalty
    
    # Reward reasonable coefficient of variation
    if (!is.na(type_specific_stats$cv_range[1]) && !is.infinite(type_specific_stats$cv_range[2])) {
      cv_score <- 15 * (1 - min(mean(type_specific_stats$cv_range, na.rm = TRUE) / 2, 1))
      score <- score + cv_score
    }
  }
  
  # Ensure score is between 0 and 100
  score <- max(0, min(100, score))
  
  return(round(score, 1))
}

# =========================
# Methodology Recommendation Engine
# =========================

#' Generate Methodology Recommendations
#' 
#' Main function to generate methodology recommendations based on data characteristics
#' 
#' @param characteristics List returned by analyze_data_characteristics()
#' @param data_type Character string: "binary" or "continuous"
#' @return List containing comprehensive methodology recommendations
generate_methodology_recommendations <- function(characteristics, data_type) {
  # Validate input parameters
  if (missing(characteristics) || is.null(characteristics)) {
    stop("Data characteristics are required for generating recommendations")
  }
  
  if (!data_type %in% c("binary", "continuous")) {
    stop("data_type must be either 'binary' or 'continuous'")
  }
  
  # Extract key metrics for recommendations
  study_count <- characteristics$basic_stats$study_count
  treatment_count <- characteristics$basic_stats$treatment_count
  network_connected <- characteristics$network_stats$connectivity
  
  # Generate tau method recommendation
  tau_recommendation <- recommend_tau_method(study_count, treatment_count)
  
  # Generate effect measure recommendation
  if (data_type == "binary") {
    avg_event_rate <- characteristics$type_specific_stats$average_event_rate
    effect_recommendation <- recommend_effect_measure(data_type, avg_event_rate)
    
    # Generate continuity correction recommendation
    zero_event_proportion <- characteristics$type_specific_stats$zero_event_proportion
    continuity_recommendation <- recommend_continuity_correction(zero_event_proportion)
  } else {
    effect_recommendation <- recommend_effect_measure(data_type)
    continuity_recommendation <- list(
      recommended = FALSE,
      value = 0,
      reason = "连续性校正不适用于连续数据",
      rule_applied = "continuous_data_rule",
      confidence = 1.0
    )
  }
  
  # Generate model type recommendation
  model_recommendation <- recommend_model_type(study_count, characteristics$complexity_score)
  
  # Calculate overall confidence
  overall_confidence <- calculate_overall_confidence(
    tau_recommendation$confidence,
    effect_recommendation$confidence,
    continuity_recommendation$confidence,
    model_recommendation$confidence,
    network_connected
  )
  
  # Determine complexity level
  complexity_level <- determine_complexity_level(characteristics$complexity_score)
  
  # Generate special considerations
  special_considerations <- generate_special_considerations(characteristics, data_type)
  
  return(list(
    data_type = data_type,
    data_characteristics = characteristics,
    recommendations = list(
      tau_method = tau_recommendation,
      effect_measure = effect_recommendation,
      continuity_correction = continuity_recommendation,
      model_type = model_recommendation
    ),
    recommendation_summary = list(
      overall_confidence = overall_confidence,
      complexity_level = complexity_level,
      special_considerations = special_considerations,
      network_connected = network_connected
    )
  ))
}

#' Recommend Tau Estimation Method
#' 
#' Recommends tau estimation method based on study count and treatment count
#' 
#' @param study_count Integer number of studies
#' @param treatment_count Integer number of treatments
#' @return List containing tau method recommendation
recommend_tau_method <- function(study_count, treatment_count) {
  if (study_count < 5) {
    return(list(
      primary = "DL",
      alternatives = character(0),
      reason = "研究数量少于5个，DerSimonian-Laird(DL)方法计算稳定且适用于小样本",
      confidence = 0.9,
      rule_applied = "small_study_rule"
    ))
  } else if (study_count >= 5 && study_count < 10) {
    alternatives <- if (treatment_count >= 8) c("EB") else character(0)
    reason <- "中等研究数量时REML提供无偏估计"
    if (treatment_count >= 8) {
      reason <- paste(reason, "；复杂网络(≥8个治疗)可考虑Empirical Bayes(EB)方法")
    }
    
    return(list(
      primary = "REML",
      alternatives = alternatives,
      reason = reason,
      confidence = 0.95,
      rule_applied = "medium_study_rule"
    ))
  } else {
    alternatives <- if (treatment_count >= 8) c("EB") else character(0)
    reason <- "大样本时REML是金标准方法"
    if (treatment_count >= 8) {
      reason <- paste(reason, "；复杂网络(≥8个治疗)可考虑Empirical Bayes(EB)方法借用更多信息")
    }
    
    return(list(
      primary = "REML",
      alternatives = alternatives,
      reason = reason,
      confidence = 0.95,
      rule_applied = "large_study_rule"
    ))
  }
}

#' Recommend Effect Measure
#' 
#' Recommends effect measure based on data type and event rate
#' 
#' @param data_type Character string: "binary" or "continuous"
#' @param avg_event_rate Numeric average event rate (for binary data only)
#' @return List containing effect measure recommendation
recommend_effect_measure <- function(data_type, avg_event_rate = NULL) {
  if (data_type == "continuous") {
    return(list(
      recommended = "MD",
      reason = "均数差(MD)提供直接的临床意义解释，是连续数据的首选效应量",
      confidence = 0.95,
      rule_applied = "continuous_default_rule"
    ))
  } else if (data_type == "binary") {
    if (is.null(avg_event_rate) || is.na(avg_event_rate)) {
      return(list(
        recommended = "RR",
        reason = "无法计算平均事件率，默认推荐相对危险度(RR)作为常用的二分类效应量",
        confidence = 0.7,
        rule_applied = "binary_default_rule"
      ))
    }
    
    if (avg_event_rate >= 0.1 && avg_event_rate <= 0.9) {
      return(list(
        recommended = "RR",
        reason = sprintf("平均事件率为%.1f%%，在中等范围内，相对危险度(RR)临床解释性最佳", avg_event_rate * 100),
        confidence = 0.9,
        rule_applied = "moderate_event_rate_rule"
      ))
    } else {
      return(list(
        recommended = "OR",
        reason = sprintf("平均事件率为%.1f%%，属于极端事件率，比值比(OR)数学性质更稳定", avg_event_rate * 100),
        confidence = 0.85,
        rule_applied = "extreme_event_rate_rule"
      ))
    }
  } else {
    stop("Invalid data_type. Must be 'binary' or 'continuous'")
  }
}

#' Recommend Continuity Correction
#' 
#' Recommends continuity correction based on zero event proportion
#' 
#' @param zero_event_proportion Numeric proportion of studies with zero events
#' @return List containing continuity correction recommendation
recommend_continuity_correction <- function(zero_event_proportion) {
  if (is.null(zero_event_proportion) || is.na(zero_event_proportion)) {
    return(list(
      recommended = FALSE,
      value = 0,
      reason = "无法计算零事件比例，默认不使用连续性校正",
      rule_applied = "missing_data_rule",
      confidence = 0.5
    ))
  }
  
  if (zero_event_proportion > 0.2) {
    return(list(
      recommended = TRUE,
      value = 0.5,
      reason = sprintf("零事件研究比例为%.1f%%，超过20%%阈值，推荐使用0.5连续性校正以提高效应量估计稳定性", zero_event_proportion * 100),
      rule_applied = "high_zero_event_rule",
      confidence = 0.9
    ))
  } else {
    return(list(
      recommended = FALSE,
      value = 0,
      reason = sprintf("零事件研究比例为%.1f%%，低于20%%阈值，不使用连续性校正以避免引入偏倚", zero_event_proportion * 100),
      rule_applied = "low_zero_event_rule",
      confidence = 0.9
    ))
  }
}

#' Recommend Model Type
#' 
#' Recommends random effects vs fixed effects model
#' 
#' @param study_count Integer number of studies
#' @param complexity_score Numeric complexity score (0-100)
#' @return List containing model type recommendation
recommend_model_type <- function(study_count, complexity_score) {
  if (study_count < 3) {
    return(list(
      recommended = "fixed",
      reason = "研究数量少于3个，固定效应模型更适合，随机效应模型可能不稳定",
      confidence = 0.9,
      rule_applied = "very_small_study_rule"
    ))
  } else if (study_count < 5) {
    return(list(
      recommended = "both",
      reason = "研究数量较少(3-4个)，建议同时考虑固定效应和随机效应模型，比较结果稳定性",
      confidence = 0.8,
      rule_applied = "small_study_rule"
    ))
  } else if (complexity_score < 30) {
    return(list(
      recommended = "fixed",
      reason = sprintf("复杂度评分较低(%.1f/100)，网络结构简单，固定效应模型可能足够", complexity_score),
      confidence = 0.8,
      rule_applied = "low_complexity_rule"
    ))
  } else {
    return(list(
      recommended = "random",
      reason = sprintf("研究数量充足(%d个)且复杂度较高(%.1f/100)，随机效应模型能更好地处理异质性", study_count, complexity_score),
      confidence = 0.9,
      rule_applied = "standard_rule"
    ))
  }
}

#' Calculate Overall Confidence
#' 
#' Calculates overall confidence score for recommendations
#' 
#' @param tau_conf Numeric confidence for tau method
#' @param effect_conf Numeric confidence for effect measure
#' @param continuity_conf Numeric confidence for continuity correction
#' @param model_conf Numeric confidence for model type
#' @param network_connected Logical indicating network connectivity
#' @return Numeric overall confidence score
calculate_overall_confidence <- function(tau_conf, effect_conf, continuity_conf, model_conf, network_connected) {
  # Weight the confidences
  weights <- c(0.3, 0.3, 0.2, 0.2)  # tau, effect, continuity, model
  confidences <- c(tau_conf, effect_conf, continuity_conf, model_conf)
  
  weighted_confidence <- sum(weights * confidences)
  
  # Penalize if network is not connected
  if (!network_connected) {
    weighted_confidence <- weighted_confidence * 0.7
  }
  
  return(round(weighted_confidence, 3))
}

#' Determine Complexity Level
#' 
#' Determines complexity level based on complexity score
#' 
#' @param complexity_score Numeric complexity score (0-100)
#' @return Character complexity level
determine_complexity_level <- function(complexity_score) {
  if (complexity_score < 30) {
    return("simple")
  } else if (complexity_score < 70) {
    return("moderate")
  } else {
    return("complex")
  }
}

#' Generate Special Considerations
#' 
#' Generates special considerations based on data characteristics
#' 
#' @param characteristics List of data characteristics
#' @param data_type Character string data type
#' @return Character vector of special considerations
generate_special_considerations <- function(characteristics, data_type) {
  considerations <- character(0)
  
  # Network connectivity
  if (!characteristics$network_stats$connectivity) {
    considerations <- c(considerations, 
                        sprintf("网络不连通，存在%d个独立组件，无法进行标准网络荟萃分析", 
                                length(characteristics$network_stats$disconnected_components)))
  }
  
  # Low network density
  if (characteristics$network_stats$density < 0.3) {
    considerations <- c(considerations, 
                        sprintf("网络密度较低(%.1f%%)，可能存在间接比较的不确定性", 
                                characteristics$network_stats$density * 100))
  }
  
  # Type-specific considerations
  if (data_type == "binary") {
    # High zero event proportion
    if (characteristics$type_specific_stats$zero_event_proportion > 0.3) {
      considerations <- c(considerations, 
                          sprintf("零事件研究比例较高(%.1f%%)，需要特别注意效应量估计的稳定性", 
                                  characteristics$type_specific_stats$zero_event_proportion * 100))
    }
    
    # Extreme event rates
    if (characteristics$type_specific_stats$average_event_rate < 0.05 || 
        characteristics$type_specific_stats$average_event_rate > 0.95) {
      considerations <- c(considerations, 
                          sprintf("平均事件率极端(%.1f%%)，建议考虑使用贝叶斯方法或其他稳健方法", 
                                  characteristics$type_specific_stats$average_event_rate * 100))
    }
  } else {
    # High zero SD proportion
    if (characteristics$type_specific_stats$zero_sd_proportion > 0.1) {
      considerations <- c(considerations, 
                          sprintf("%.1f%%的研究标准差为零，可能影响异质性评估", 
                                  characteristics$type_specific_stats$zero_sd_proportion * 100))
    }
  }
  
  # Small study count
  if (characteristics$basic_stats$study_count < 5) {
    considerations <- c(considerations, 
                        sprintf("研究数量较少(%d个)，结果解释需谨慎，建议进行敏感性分析", 
                                characteristics$basic_stats$study_count))
  }
  
  # Large network
  if (characteristics$basic_stats$treatment_count > 10) {
    considerations <- c(considerations, 
                        sprintf("治疗网络较大(%d个治疗)，建议考虑网络一致性检验和子组分析", 
                                characteristics$basic_stats$treatment_count))
  }
  
  return(considerations)
}

# =========================
# Helper Functions
# =========================

#' Generate User-Friendly Error Message
#' 
#' Converts technical validation results into user-friendly messages
#' 
#' @param validation_result List returned by validate_data_quality()
#' @return Character string with formatted error message
generate_user_friendly_error_message <- function(validation_result) {
  if (validation_result$is_valid) {
    return("✅ Data validation passed successfully!")
  }
  
  summary <- validation_result$summary
  issues <- validation_result$issues
  
  message_parts <- c()
  
  # Summary message
  if (summary$error_count > 0) {
    message_parts <- c(message_parts, 
                       sprintf("❌ Found %d error(s) that must be fixed", summary$error_count))
  }
  
  if (summary$warning_count > 0) {
    message_parts <- c(message_parts, 
                       sprintf("⚠️ Found %d warning(s) that should be reviewed", summary$warning_count))
  }
  
  # Detailed issues
  if (nrow(issues) > 0) {
    message_parts <- c(message_parts, "\nDetailed Issues:")
    
    for (i in seq_len(min(5, nrow(issues)))) {  # Show max 5 issues
      issue <- issues[i, ]
      severity_icon <- if (issue$severity == "error") "❌" else "⚠️"
      message_parts <- c(message_parts, 
                         sprintf("%s Row %d in %s: %s", 
                                 severity_icon, issue$row_number, issue$file, issue$description))
    }
    
    if (nrow(issues) > 5) {
      message_parts <- c(message_parts, sprintf("... and %d more issues", nrow(issues) - 5))
    }
  }
  
  return(paste(message_parts, collapse = "\n"))
}

#' Print Validation Results
#' 
#' Pretty print validation results for debugging
#' 
#' @param validation_result List returned by validate_data_quality()
print_validation_results <- function(validation_result) {
  cat("=== Data Validation Results ===\n")
  cat("Overall Status:", if (validation_result$is_valid) "✅ PASSED" else "❌ FAILED", "\n")
  cat("Total Issues:", validation_result$summary$total_issues, "\n")
  cat("Errors:", validation_result$summary$error_count, "\n")
  cat("Warnings:", validation_result$summary$warning_count, "\n")
  
  if (nrow(validation_result$issues) > 0) {
    cat("\n=== Issue Details ===\n")
    print(validation_result$issues)
  }
  
  cat("\n")
}