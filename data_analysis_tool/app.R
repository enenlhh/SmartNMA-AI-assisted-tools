# =========================
# 1. Load Required Packages
# =========================
library(shiny)
library(readxl)
library(dplyr)
library(showtext)
library(writexl)
library(tools)
library(meta)
library(netmeta)
library(shinyFiles)

# =========================
# 2. UI Section
# =========================
ui <- fluidPage(
  tags$head(
    tags$style(HTML("
      body { 
        background: #f6f8fa; 
        font-family: 'Segoe UI', Arial, sans-serif; 
      }
      .main-title {
        text-align: center;
        color: #1f2937;
        font-size: 28px;
        font-weight: 700;
        margin: 20px 0 30px 0;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      }
      .intro-section {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #e5e7eb;
      }
      .intro-title {
        font-size: 20px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
      }
      .intro-icon {
        font-size: 24px;
        margin-right: 12px;
        color: #3b82f6;
      }
      .intro-text {
        font-size: 16px;
        line-height: 1.6;
        color: #374151;
        margin-bottom: 16px;
      }
      .feature-list {
        list-style: none;
        padding: 0;
        margin: 16px 0;
      }
      .feature-item {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        font-size: 15px;
        color: #374151;
      }
      .feature-icon {
        color: #10b981;
        margin-right: 12px;
        font-weight: bold;
      }
      .collapsible-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        margin-bottom: 16px;
        overflow: hidden;
      }
      .collapsible-header {
        background: #f1f5f9;
        padding: 16px;
        cursor: pointer;
        font-weight: 600;
        color: #1f2937;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.2s ease;
      }
      .collapsible-header:hover {
        background: #e2e8f0;
      }
      .collapsible-content {
        padding: 16px;
        display: none;
        font-size: 14px;
        line-height: 1.5;
        color: #374151;
      }
      .collapsible-content.active {
        display: block;
      }
      .toggle-icon {
        transition: transform 0.3s ease;
      }
      .toggle-icon.rotated {
        transform: rotate(180deg);
      }
      .template-info {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        font-size: 14px;
        color: #92400e;
        line-height: 1.5;
      }
      .config-card { 
        background: #fff; 
        border-radius: 12px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); 
        padding: 24px; 
        margin-bottom: 24px;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
      }
      .config-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
      }
      .card-title { 
        font-size: 18px; 
        font-weight: 600; 
        color: #1f2937; 
        margin-bottom: 16px; 
        display: flex; 
        align-items: center;
        padding-bottom: 12px;
        border-bottom: 2px solid #f3f4f6;
      }
      .card-icon { 
        font-size: 20px; 
        margin-right: 10px; 
        color: #3b82f6; 
      }
      .form-label { 
        font-size: 14px; 
        color: #374151; 
        font-weight: 500; 
        margin-bottom: 6px; 
        display: block;
      }
      .form-input, .form-select { 
        border-radius: 8px; 
        border: 2px solid #e5e7eb; 
        padding: 10px 12px; 
        font-size: 14px; 
        width: 100%; 
        box-sizing: border-box; 
        margin-bottom: 16px; 
        background: #fafbfc; 
        transition: all 0.2s ease;
      }
      .form-input:focus, .form-select:focus { 
        border-color: #3b82f6; 
        outline: none; 
        background: #fff;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
      .btn-primary { 
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
        color: #fff; 
        border: none; 
        border-radius: 8px; 
        font-weight: 600; 
        padding: 12px 24px; 
        width: 100%; 
        font-size: 16px; 
        transition: all 0.3s ease;
        cursor: pointer;
      }
      .btn-primary:hover:not(:disabled) { 
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
      }
      .btn-primary:disabled {
        background: #9ca3af;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
      }
      .btn-secondary { 
        background: #f8fafc; 
        color: #374151; 
        border: 2px solid #e5e7eb; 
        border-radius: 8px; 
        font-weight: 500; 
        padding: 10px 16px; 
        width: 100%; 
        font-size: 14px;
        transition: all 0.2s ease;
        cursor: pointer;
      }
      .btn-secondary:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
      }
      .btn-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        width: 100%;
        font-size: 16px;
        transition: all 0.3s ease;
        cursor: pointer;
        margin-top: 12px;
      }
      .btn-danger:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
      }
      .section-gap { 
        margin-top: 20px; 
      }
      .help-text { 
        font-size: 12px; 
        color: #6b7280; 
        margin-bottom: 12px; 
        font-style: italic;
      }
      .divider { 
        border-bottom: 1px solid #e5e7eb; 
        margin: 20px 0; 
      }
      .info-box { 
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
        border-left: 4px solid #3b82f6; 
        border-radius: 8px; 
        padding: 16px; 
        margin-bottom: 20px; 
        font-size: 14px; 
        color: #1e40af;
        line-height: 1.5;
      }
      .status-box { 
        background: #f9fafb; 
        border-radius: 8px; 
        padding: 16px; 
        font-size: 14px; 
        margin-bottom: 16px; 
        color: #374151;
        border: 1px solid #e5e7eb;
        min-height: 60px;
      }
      .log-box { 
        background: #f8fafc; 
        border-radius: 8px; 
        padding: 16px; 
        font-size: 13px; 
        color: #6b7280; 
        max-height: 200px; 
        overflow-y: auto; 
        margin-bottom: 16px;
        border: 1px solid #e5e7eb;
        font-family: 'Courier New', monospace;
        line-height: 1.4;
      }
      .checkbox-container { 
        margin-bottom: 16px; 
        font-size: 14px;
      }
      .checkbox-container input[type='checkbox'] {
        margin-right: 8px;
        transform: scale(1.1);
      }
      .small-text { 
        font-size: 12px; 
        color: #6b7280; 
      }
      .progress-container {
        width: 100%;
        background-color: #e5e7eb;
        border-radius: 8px;
        margin: 16px 0;
        overflow: hidden;
      }
      .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        border-radius: 8px;
        transition: width 0.3s ease;
        animation: pulse 2s infinite;
      }
      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
      }
      .analyzing-text {
        text-align: center;
        color: #3b82f6;
        font-weight: 600;
        margin: 16px 0;
        font-size: 16px;
      }
      .row-equal-height {
        display: flex;
        flex-wrap: wrap;
      }
      .row-equal-height > [class*='col-'] {
        display: flex;
        flex-direction: column;
      }
      .row-equal-height .config-card {
        flex: 1;
      }
    "))
  ),
  
  # JavaScript for collapsible functionality
  tags$script(HTML("
    $(document).ready(function() {
      $('.collapsible-header').click(function() {
        var content = $(this).next('.collapsible-content');
        var icon = $(this).find('.toggle-icon');
        
        content.toggleClass('active');
        icon.toggleClass('rotated');
      });
    });
  ")),
  
  div(class = "main-title", "📊 SartNMA: Network Meta-Analysis Tool"),
  
  # Tool Introduction Section
  div(class = "intro-section",
      div(class = "intro-title",
          span(class = "intro-icon", "🚀"),
          "About SartNMA"
      ),
      div(class = "intro-text",
          "SartNMA is a comprehensive, user-friendly tool designed to streamline the entire Network Meta-Analysis (NMA) workflow. This tool enables researchers to efficiently conduct high-quality frequentist NMA with minimal technical barriers, supporting both binary and continuous outcome data."
      ),
      
      div(class = "intro-title",
          span(class = "intro-icon", "✨"),
          "Key Features"
      ),
      tags$ul(class = "feature-list",
              tags$li(class = "feature-item",
                      tags$span(class = "feature-icon", "✓"),
                      "Automated frequentist network meta-analysis for both binary and continuous outcomes"
              ),
              tags$li(class = "feature-item",
                      tags$span(class = "feature-icon", "✓"),
                      "Comprehensive statistical outputs: effect estimates, league tables, treatment rankings (P-scores)"
              ),
              tags$li(class = "feature-item",
                      tags$span(class = "feature-icon", "✓"),
                      "Advanced visualizations: network plots, forest plots, funnel plots, node-splitting analysis"
              ),
              tags$li(class = "feature-item",
                      tags$span(class = "feature-icon", "✓"),
                      "Publication bias assessment and consistency evaluation"
              ),
              tags$li(class = "feature-item",
                      tags$span(class = "feature-icon", "✓"),
                      "Batch processing of multiple outcomes with standardized reporting"
              ),
              tags$li(class = "feature-item",
                      tags$span(class = "feature-icon", "✓"),
                      "GRADE-ready output files for evidence certainty assessment"
              )
      )
  ),
  
  # Usage Instructions Section
  div(class = "intro-section",
      div(class = "collapsible-card",
          div(class = "collapsible-header",
              span(class = "intro-icon", "📋"),
              "Usage Instructions",
              span(class = "toggle-icon", "▼")
          ),
          div(class = "collapsible-content",
              # Data Preparation Instructions
              div(class = "collapsible-card",
                  div(class = "collapsible-header",
                      "1. Data Preparation",
                      span(class = "toggle-icon", "▼")
                  ),
                  div(class = "collapsible-content",
                      HTML("
                        <p><strong>Prepare one Excel file (.xlsx) for each outcome:</strong></p>
                        <ul>
                          <li><strong>File naming:</strong> Use descriptive outcome names (e.g., 'Mortality.xlsx', 'Pain_Score.xlsx')</li>
                          <li><strong>Data format:</strong> Each row represents one treatment arm from one study</li>
                        </ul>
                        
                        <p><strong>For Binary Outcomes:</strong></p>
                        <ul>
                          <li><strong>study:</strong> Study identifier (same for all arms within a study)</li>
                          <li><strong>treatment:</strong> Treatment name (consistent across studies)</li>
                          <li><strong>event:</strong> Number of events (e.g., deaths, adverse events)</li>
                          <li><strong>n:</strong> Total sample size for this treatment arm</li>
                          <li><strong>ROB:</strong> Risk of bias assessment - must be either 'Low' or 'High'</li>
                        </ul>
                        
                        <p><strong>For Continuous Outcomes:</strong></p>
                        <ul>
                          <li><strong>study:</strong> Study identifier (same for all arms within a study)</li>
                          <li><strong>treatment:</strong> Treatment name (consistent across studies)</li>
                          <li><strong>n:</strong> Sample size for this treatment arm</li>
                          <li><strong>mean:</strong> Mean value of the outcome</li>
                          <li><strong>sd:</strong> Standard deviation of the outcome</li>
                          <li><strong>ROB:</strong> Risk of bias assessment - must be either 'Low' or 'High'</li>
                        </ul>
                    ")
                  )
              ),
              
              # Step-by-step Instructions
              div(class = "collapsible-card",
                  div(class = "collapsible-header",
                      "2. Step-by-Step Analysis",
                      span(class = "toggle-icon", "▼")
                  ),
                  div(class = "collapsible-content",
                      HTML("
                        <ol>
                          <li><strong>Upload Data Files:</strong> Select all Excel files containing your outcome data</li>
                          <li><strong>Choose Output Directory:</strong> Select a folder where results will be saved</li>
                          <li><strong>Configure Analysis Settings:</strong>
                            <ul>
                              <li>Select data type (Binary or Continuous)</li>
                              <li>Choose appropriate effect measure</li>
                              <li>Configure analysis methods</li>
                            </ul>
                          </li>
                          <li><strong>Set Model Preferences:</strong>
                            <ul>
                              <li>Choose between random effects, fixed effects, or both</li>
                              <li>Set reference treatment (or leave blank for auto-selection)</li>
                              <li>Configure heterogeneity estimation method</li>
                            </ul>
                          </li>
                          <li><strong>Start Analysis:</strong> Click 'Start Analysis' and monitor progress</li>
                          <li><strong>Review Results:</strong> Check the output directory for comprehensive results</li>
                        </ol>
                    ")
                  )
              ),
              
              # Output Description
              div(class = "collapsible-card",
                  div(class = "collapsible-header",
                      "3. Understanding Output Files",
                      span(class = "toggle-icon", "▼")
                  ),
                  div(class = "collapsible-content",
                      HTML("
                        <p><strong>For each outcome, the tool generates:</strong></p>
                        <ul>
                          <li><strong>Network Graph:</strong> Visual representation of treatment comparisons</li>
                          <li><strong>Forest Plots:</strong> Effect estimates with confidence intervals</li>
                          <li><strong>League Tables:</strong> Pairwise comparison results in matrix format</li>
                          <li><strong>Treatment Rankings:</strong> P-scores for treatment hierarchy</li>
                          <li><strong>Funnel Plots:</strong> Publication bias assessment</li>
                          <li><strong>Node-Split Analysis:</strong> Consistency evaluation</li>
                          <li><strong>Pairwise Meta-Analysis:</strong> Traditional meta-analysis results</li>
                          <li><strong>GRADE-Ready Files:</strong> Prepared for evidence certainty assessment</li>
                        </ul>
                        
                        <p><strong>Additional Files:</strong></p>
                        <ul>
                          <li><strong>Methodology Report:</strong> Comprehensive analysis documentation</li>
                          <li><strong>Analysis Settings:</strong> Record of all configuration choices</li>
                          <li><strong>Original Data:</strong> Processed input data for verification</li>
                        </ul>
                    ")
                  )
              ),
              
              # Tips and Best Practices
              div(class = "collapsible-card",
                  div(class = "collapsible-header",
                      "4. Tips and Best Practices",
                      span(class = "toggle-icon", "▼")
                  ),
                  div(class = "collapsible-content",
                      HTML("
                        <ul>
                          <li><strong>Data Quality:</strong> Ensure consistent treatment naming across all studies</li>
                          <li><strong>Network Connectivity:</strong> Verify that treatments form a connected network</li>
                          <li><strong>Reference Treatment:</strong> Choose the most commonly used or clinically relevant comparator</li>
                          <li><strong>Effect Direction:</strong> Correctly specify whether smaller values indicate better or worse outcomes</li>
                          <li><strong>Zero Events:</strong> For binary outcomes, consider continuity correction for studies with zero events</li>
                          <li><strong>Model Selection:</strong> Random effects models are generally preferred for heterogeneous data</li>
                          <li><strong>Result Interpretation:</strong> Always review consistency analysis and publication bias assessment</li>
                        </ul>
                    ")
                  )
              )
          )
      )
  ),
  
  # Template Information
  div(class = "intro-section",
      div(class = "intro-title",
          span(class = "intro-icon", "📋"),
          "Data Template Requirements"
      ),
      div(class = "collapsible-card",
          div(class = "collapsible-header",
              "Click to read more",
              span(class = "toggle-icon", "▼")
          ),
          div(class = "collapsible-content",
              HTML("
                <strong>📋 Data Template Requirements:</strong><br>
                • <strong>study:</strong> Study identifier (text)<br>
                • <strong>treatment:</strong> Treatment name (text, consistent across studies)<br>
                • <strong>Binary data:</strong> event (number), n (sample size)<br>
                • <strong>Continuous data:</strong> n (sample size), mean (numeric), sd (numeric)<br>
                • <strong>ROB:</strong> Risk of bias - MUST be either 'Low' or 'High' only<br>
                • Upload all outcome files at once - the tool will process them in batch
            ")
          )
      )
  ),
  
  # Configuration Cards Row
  div(class = "row-equal-height",
      # Data Upload Card
      div(class = "col-md-4",
          div(class = "config-card",
              div(class = "card-title", 
                  span(class = "card-icon", "📤"), 
                  "Data Upload"
              ),
              div(class = "form-label", "Select Excel Files"),
              div(class = "form-input",
                  fileInput("datafiles", NULL, multiple = TRUE, accept = ".xlsx",
                            buttonLabel = "Choose Files", width = "100%")
              ),
              div(class = "help-text", "Support multiple selection. Files will be displayed below."),
              
              div(class = "divider"),
              
              div(class = "form-label", "Output Directory (Optional)"),
              textInput("outputdir", NULL, "", 
                        placeholder = "Example: C:/Users/YourName/Desktop/NMA_Results; Leave blank to auto-create folder in input file location", 
                        width = "100%"),
              div(class = "help-text", "If empty, results will be saved in a new folder next to your input files")
          )
      ),
      
      # Analysis Settings Card
      div(class = "col-md-4",
          div(class = "config-card",
              div(class = "card-title", 
                  span(class = "card-icon", "⚙️"), 
                  "Analysis Settings"
              ),
              
              div(class = "form-label", "Data Type"),
              selectInput("analysis_type", NULL, 
                          choices = c("Binary Data" = "binary", "Continuous Data" = "continuous"),
                          selected = "binary", width = "100%"),
              
              conditionalPanel(
                condition = "input.analysis_type == 'binary'",
                div(class = "form-label", "Effect Measure"),
                selectInput("binary_effect_measure", NULL, 
                            choices = c("RR", "OR", "RD", "ASD"),
                            selected = "RR", width = "100%"),
                
                div(class = "form-label", "Analysis Method"),
                selectInput("method_binary", NULL, 
                            choices = c("Inverse", "MH", "NCH"),
                            selected = "Inverse", width = "100%"),
                
                div(class = "checkbox-container",
                    checkboxInput("use_continuity_correction", "Zero Event Correction", FALSE)
                ),
                
                conditionalPanel(
                  condition = "input.use_continuity_correction == true",
                  div(class = "form-label", "Correction Value"),
                  numericInput("incr_value", NULL, 0.5, min = 0, max = 1, step = 0.1, width = "100%")
                )
              ),
              
              conditionalPanel(
                condition = "input.analysis_type == 'continuous'",
                div(class = "form-label", "Effect Measure"),
                selectInput("continuous_effect_measure", NULL, 
                            choices = c("MD", "SMD", "ROM"),
                            selected = "MD", width = "100%")
              )
          )
      ),
      
      # Model Settings Card
      div(class = "col-md-4",
          div(class = "config-card",
              div(class = "card-title", 
                  span(class = "card-icon", "🧩"), 
                  "Model Settings"
              ),
              
              div(class = "checkbox-container",
                  checkboxInput("include_random_effect", "Random Effects Model", TRUE)
              ),
              
              div(class = "checkbox-container",
                  checkboxInput("include_fixed_effect", "Fixed Effects Model", TRUE)
              ),
              
              div(class = "form-label", "Heterogeneity Method"),
              selectInput("method_tau", NULL, 
                          choices = c("DL", "REML", "ML", "PM", "EB"),
                          selected = "REML", width = "100%"),
              
              div(class = "form-label", "Effect Direction"),
              selectInput("small_values_direction", NULL, 
                          choices = c("Smaller Values Indicate Better Outcomes" = "good", 
                                      "Smaller Values Indicate Worse Outcomes" = "bad"),
                          selected = "good", width = "100%"),
              
              div(class = "form-label", "Reference Treatment"),
              textInput("ref_treatment", NULL, "", 
                        placeholder = "Leave empty for auto-selection", width = "100%"),
              div(class = "help-text", "Auto-selects most frequent treatment if empty")
          )
      )
  ),
  
  # Control Buttons Row
  fluidRow(
    column(12,
           div(class = "config-card",
               div(style = "display: flex; gap: 16px;",
                   div(style = "flex: 1;",
                       actionButton("run", "🚀 Start Analysis", class = "btn-primary")
                   ),
                   conditionalPanel(
                     condition = "output.show_stop_button",
                     div(style = "flex: 1;",
                         actionButton("stop", "⏹️ Stop Analysis", class = "btn-danger")
                     )
                   )
               )
           )
    )
  ),
  
  # Analysis Status Card
  fluidRow(
    column(12,
           div(class = "config-card",
               div(class = "card-title", 
                   span(class = "card-icon", "📊"), 
                   "Analysis Status"
               ),
               
               # Status Message (new)
               div(class = "analyzing-text", textOutput("analysis_status_message")),
               
               # Current Status Box
               div(class = "form-label", "📶 Current Status"),
               div(class = "status-box", verbatimTextOutput("status")),
               
               # Progress bar (shown during analysis)
               conditionalPanel(
                 condition = "output.show_progress",
                 div(class = "progress-container",
                     div(class = "progress-bar", style = "width: 100%;")
                 )
               ),
               
               # Log output
               div(class = "form-label", "📜 Analysis Log"),
               div(class = "log-box", verbatimTextOutput("log"))
           )
    )
  )
)

# =========================
# 3. Server Section
# =========================
server <- function(input, output, session) {
  # Reactive values for analysis state
  values <- reactiveValues(
    analyzing = FALSE,
    analysis_complete = FALSE
  )
  
  # Directory selection
  roots <- c(
    "C Drive" = "C:/",
    "D Drive" = "D:/",
    "E Drive" = "E:/",
    "F Drive" = "F:/",
    "Home" = normalizePath("~")
  )
  
  output_dir <- reactive({
    req(input$datafiles)
    
    default_parent <- dirname(dirname(input$datafiles$datapath[1]))
    default_subdir <- paste0("NMA_Results_", format(Sys.time(), "%Y%m%d_%H%M%S"))
    default_path <- file.path(default_parent, default_subdir)
    
    user_path <- input$outputdir
    final_path <- if (is.null(user_path) || user_path == "") {
      default_path
    } else {
      normalizePath(user_path, winslash = "/", mustWork = FALSE)
    }
    
    if (!dir.exists(final_path)) {
      dir.create(final_path, recursive = TRUE)
    }
    
    final_path
  })
  
  output$chosen_dir <- renderText({
    if (!is.null(output_dir())) {
      paste("Results will be saved to:", output_dir())
    } else {
      "Waiting for input files..."
    }
  })
  
  
  # Initial status
  output$status <- renderText({
    "Ready to start analysis. Please upload data files and configure settings."
  })
  
  output$log <- renderText({
    "System ready. Waiting for user input..."
  })
  
  # Start analysis
  observeEvent(input$run, {
    req(input$datafiles)
    # Show analyzing message
    output$analysis_status_message <- renderText({
      "🔄 Analysis in progress, please wait..."
    })
    # Prevent repeated clicks
    values$analyzing <- TRUE
    # Validate inputs
    if (is.null(output_dir()) || length(output_dir()) == 0) {
      output$status <- renderText({"❌ Error: Please select an output directory!"})
      output$log <- renderText({"No output directory detected. Please select a folder to save results."})
      output$analysis_status_message <- renderText("❌ Analysis failed")
      values$analyzing <- FALSE
      return()
    }
    # Update UI status
    output$status <- renderText({"🔄 Analysis in progress... Please wait"})
    output$log <- renderText({
      "Initializing analysis...\nProcessing uploaded files...\nThis may take several minutes depending on data size."
    })
    # Get user output directory
    user_output_dir <- output_dir()
    if (!dir.exists(user_output_dir)) {
      dir.create(user_output_dir, recursive = TRUE)
      cat("Created output directory:", user_output_dir, "\n")
    }
    # Save uploaded data
    data_dir <- file.path(user_output_dir, "input_data")
    if (!dir.exists(data_dir)) dir.create(data_dir)
    for(i in 1:nrow(input$datafiles)){
      file.copy(input$datafiles$datapath[i], 
                file.path(data_dir, input$datafiles$name[i]), 
                overwrite = TRUE)
    }
    # Clear old results
    result_dir <- file.path(user_output_dir, "Results")
    if (dir.exists(result_dir)) unlink(result_dir, recursive = TRUE)
    dir.create(result_dir)
    # Run analysis
    tryCatch({
      run_nma_analysis(
        ref_treatment = input$ref_treatment,
        binary_effect_measure = input$binary_effect_measure,
        continuous_effect_measure = input$continuous_effect_measure,
        include_random_effect = input$include_random_effect,
        include_fixed_effect = input$include_fixed_effect,
        method_tau = input$method_tau,
        method_binary = input$method_binary,
        use_continuity_correction = input$use_continuity_correction,
        incr_value = input$incr_value,
        small_values_direction = input$small_values_direction,
        data_dir = data_dir,
        output_dir = result_dir,
        font_name = "Arial",
        font_path = ifelse(.Platform$OS.type == "windows", 
                           "C:/Windows/Fonts/arial.ttf", 
                           "/System/Library/Fonts/Arial.ttf")
      )
      # Analysis completed successfully
      values$analyzing <- FALSE
      values$analysis_complete <- TRUE
      output$status <- renderText({"✅ Analysis completed successfully!"})
      output$log <- renderText({
        paste("Analysis finished at:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
              "\n\nResults saved to your selected directory.",
              "\nMethodology report and all detailed analysis results are available in the output folder.",
              "\n\nYou can now review the results in the output directory.")
      })
      output$analysis_status_message <- renderText("✅ Analysis completed successfully!")
    }, error = function(e){
      values$analyzing <- FALSE
      values$analysis_complete <- FALSE
      output$status <- renderText({"❌ Analysis failed!"})
      output$log <- renderText({
        paste("Error occurred at:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
              "\n\nError details:", e$message,
              "\n\nPlease check your data format and try again.")
      })
      output$analysis_status_message <- renderText("❌ Analysis failed")
    })
  })
  
  # Stop analysis
  observeEvent(input$stop, {
    values$analyzing <- FALSE
    values$analysis_complete <- FALSE
    
    output$status <- renderText({"⏹️ Analysis stopped by user"})
    output$log <- renderText({
      paste("Analysis interrupted at:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
            "\n\nYou can restart the analysis anytime by clicking 'Start Analysis'.")
    })
  })
}

# =========================
# 4. Main Analysis Function
# =========================
run_nma_analysis <- function(
    ref_treatment,
    binary_effect_measure,
    continuous_effect_measure,
    include_random_effect,
    include_fixed_effect,
    method_tau,
    method_binary,
    use_continuity_correction,
    incr_value,
    small_values_direction,
    data_dir,
    output_dir,
    font_name,
    font_path
){
  
  # Load necessary packages
  library(netmeta)
  library(readxl)
  library(dplyr)
  library(showtext)
  library(writexl)
  library(tools)
  library(meta)
  
  #Generate Interactive HTML League Table
  generate_interactive_league_table <- function(net_result, 
                                                outcome_name, 
                                                model_type, # "random" or "fixed"
                                                effect_measure,
                                                output_filepath) {
    
    # 1. Select the correct data based on model type
    if (model_type == "random" && net_result$comb.random) {
      TE_matrix <- net_result$TE.random
      seTE_matrix <- net_result$seTE.random
      model_title <- "Random Effects Model"
    } else if (model_type == "fixed" && net_result$comb.fixed) {
      TE_matrix <- net_result$TE.fixed
      seTE_matrix <- net_result$seTE.fixed
      model_title <- "Fixed Effects Model"
    } else {
      warning(paste("Model type", model_type, "not available for", outcome_name))
      return(NULL)
    }
    
    treatments <- net_result$trts
    
    # 2. 修正：准备NMA数据，考虑矩阵方向问题
    nma_data <- list()
    is_ratio <- effect_measure %in% c("RR", "OR", "ROM")
    
    for (t1 in treatments) {
      nma_data[[t1]] <- list()
      for (t2 in treatments) {
        if (t1 == t2) next
        
        # 关键修正：TE_matrix[t1, t2] 实际表示 t2 vs t1
        # 为了得到 t1 vs t2，我们需要取 TE_matrix[t2, t1] 并取负值（对于非比值测量）
        # 或者取倒数（对于比值测量）
        
        if (!is.na(TE_matrix[t2, t1])) {
          log_te_raw <- TE_matrix[t2, t1]  # 这是 t1 vs t2 的原始值
          log_se_raw <- seTE_matrix[t2, t1]
          
          if (is_ratio) {
            # 对于比值测量（RR, OR, ROM），直接使用
            te <- exp(log_te_raw)
            lower <- exp(log_te_raw - 1.96 * log_se_raw)
            upper <- exp(log_te_raw + 1.96 * log_se_raw)
          } else {
            # 对于差值测量（MD, SMD, RD），直接使用
            te <- log_te_raw
            lower <- log_te_raw - 1.96 * log_se_raw
            upper <- log_te_raw + 1.96 * log_se_raw
          }
          
          nma_data[[t1]][[t2]] <- list(te = te, lower = lower, upper = upper)
        }
      }
    }
    
    # 3. 准备直接比较数据（同样的逻辑修正）
    direct_data <- list()
    
    if (!is.null(net_result$A.matrix)) {
      if (model_type == "random") {
        direct_TE <- net_result$TE.direct.random
        direct_seTE <- net_result$seTE.direct.random
      } else {
        direct_TE <- net_result$TE.direct.fixed  
        direct_seTE <- net_result$seTE.direct.fixed
      }
      
      if (!is.null(direct_TE)) {
        for (t1 in treatments) {
          direct_data[[t1]] <- list()
          for (t2 in treatments) {
            if (t1 == t2) next
            
            if (!is.na(direct_TE[t2, t1])) {  # 同样的修正
              log_te_raw <- direct_TE[t2, t1]
              log_se_raw <- direct_seTE[t2, t1]
              
              if (is_ratio) {
                te <- exp(log_te_raw)
                lower <- exp(log_te_raw - 1.96 * log_se_raw)
                upper <- exp(log_te_raw + 1.96 * log_se_raw)
              } else {
                te <- log_te_raw
                lower <- log_te_raw - 1.96 * log_se_raw
                upper <- log_te_raw + 1.96 * log_se_raw
              }
              
              direct_data[[t1]][[t2]] <- list(te = te, lower = lower, upper = upper)
            }
          }
        }
      }
    }
    
    # 4. Convert R list to JSON string
    json_data <- jsonlite::toJSON(list(
      treatments = treatments,
      effectMeasure = effect_measure,
      nmaData = nma_data,
      directData = direct_data
    ), auto_unbox = TRUE, pretty = TRUE)
    
    # 5. HTML模板保持不变，因为数据已经在R端修正了
    html_template <- '
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive League Table: __OUTCOME_NAME__</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.15.0/Sortable.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f8f9fa; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #0056b3; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
        .controls { display: flex; gap: 30px; margin-bottom: 20px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }
        .treatment-list-container { flex: 1; }
        #treatment-list { list-style: none; padding: 0; margin: 0; border: 1px solid #ccc; background: #fdfdfd; min-height: 50px; border-radius: 4px; }
        #treatment-list li { padding: 10px; background: #fff; border-bottom: 1px solid #eee; cursor: grab; user-select: none; }
        #treatment-list li:last-child { border-bottom: none; }
        #treatment-list li:hover { background-color: #f0f8ff; }
        .instructions { font-size: 0.9em; color: #666; margin-top: 5px; }
        .export-button { padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
        .export-button:hover { background-color: #218838; }
        #league-table-container { overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 0.9em; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        .diagonal { background-color: #e9ecef; font-weight: bold; }
        .upper-triangle { background-color: #f0f8ff; }
        .lower-triangle { background-color: #fff8f0; }
        .legend { margin-top: 15px; font-size: 0.9em; }
        .legend-item { display: inline-block; margin-right: 20px; }
        .legend-color { display: inline-block; width: 20px; height: 15px; margin-right: 5px; vertical-align: middle; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Interactive League Table</h1>
        <h2>Outcome: __OUTCOME_NAME__ (__MODEL_TITLE__)</h2>
        
        <div class="controls">
            <div class="treatment-list-container">
                <strong>Treatment Order</strong>
                <p class="instructions">Drag and drop treatments to reorder the table below.</p>
                <ul id="treatment-list"></ul>
            </div>
            <div>
                <strong>Export</strong><br><br>
                <button onclick="exportToXLSX()" class="export-button">Export as XLSX</button>
            </div>
        </div>
        <div id="league-table-container"></div>
        
        <div class="legend">
            <div class="legend-item">
                <span class="legend-color" style="background-color: #fff8f0; border: 1px solid #ddd;"></span>
                Network Meta-Analysis
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #f0f8ff; border: 1px solid #ddd;"></span>
                Direct Comparison
            </div>
        </div>
    </div>
    <script>
        const leagueData = __JSON_DATA__;
        
        document.addEventListener("DOMContentLoaded", () => {
            const list = document.getElementById("treatment-list");
            
            leagueData.treatments.forEach(trt => {
                const li = document.createElement("li");
                li.textContent = trt;
                li.dataset.id = trt;
                list.appendChild(li);
            });
            
            new Sortable(list, {
                animation: 150,
                onEnd: () => {
                    const orderedTreatments = Array.from(list.children).map(li => li.dataset.id);
                    renderTable(orderedTreatments);
                }
            });
            
            renderTable(leagueData.treatments);
        });
        
        function renderTable(orderedTreatments) {
            const container = document.getElementById("league-table-container");
            container.innerHTML = "";
            const table = document.createElement("table");
            table.id = "league-table-export";
            const tbody = document.createElement("tbody");
            
            orderedTreatments.forEach((rowTrt, rowIndex) => {
                const row = document.createElement("tr");
                
                orderedTreatments.forEach((colTrt, colIndex) => {
                    const cell = document.createElement("td");
                    
                    if (rowIndex === colIndex) {
                        cell.className = "diagonal";
                        cell.textContent = rowTrt;
                    } else if (rowIndex > colIndex) {
                        // Lower triangle: NMA results
                        cell.className = "lower-triangle";
                        const comparison = getNMAComparison(rowTrt, colTrt);
                        if (comparison) {
                            cell.textContent = formatComparison(comparison);
                        } else {
                            cell.textContent = ".";
                        }
                    } else {
                        // Upper triangle: Direct comparisons
                        cell.className = "upper-triangle";
                        const comparison = getDirectComparison(rowTrt, colTrt);
                        if (comparison) {
                            cell.textContent = formatComparison(comparison);
                        } else {
                            cell.textContent = ".";
                        }
                    }
                    row.appendChild(cell);
                });
                tbody.appendChild(row);
            });
            
            table.appendChild(tbody);
            container.appendChild(table);
        }
        
        function getNMAComparison(trt1, trt2) {
            if (leagueData.nmaData[trt1] && leagueData.nmaData[trt1][trt2]) {
                return leagueData.nmaData[trt1][trt2];
            }
            return null;
        }
        
        function getDirectComparison(trt1, trt2) {
            if (leagueData.directData[trt1] && leagueData.directData[trt1][trt2]) {
                return leagueData.directData[trt1][trt2];
            }
            return null;
        }
        
        function formatComparison(data) {
            const te = data.te.toFixed(2);
            const lower = data.lower.toFixed(2);
            const upper = data.upper.toFixed(2);
            return `${te} (${lower}, ${upper})`;
        }
        
        function exportToXLSX() {
            const table = document.getElementById("league-table-export");
            const wb = XLSX.utils.table_to_book(table, { sheet: "League Table" });
            const filename = `LeagueTable_${leagueData.effectMeasure}_${new Date().toISOString().slice(0, 10)}.xlsx`;
            XLSX.writeFile(wb, filename);
        }
    </script>
</body>
</html>
  '
    
    # 6. Populate the template and write to file
    html_content <- gsub("__OUTCOME_NAME__", outcome_name, html_template, fixed = TRUE)
    html_content <- gsub("__MODEL_TITLE__", model_title, html_content, fixed = TRUE)
    html_content <- gsub("__JSON_DATA__", json_data, html_content)
    
    writeLines(html_content, con = output_filepath)
    cat("Interactive league table saved to:", output_filepath, "\n")
  }
  
  
  # Define methodology report generation function
  generate_methodology_report <- function(
    ref_treatment,
    binary_effect_measure,
    continuous_effect_measure,
    include_random_effect,
    include_fixed_effect,
    method_tau,
    method_binary,
    use_continuity_correction,
    incr_value,
    font_name,
    font_path,
    data_dir,
    output_dir,
    skipped_outcomes = NULL,
    skip_reasons = NULL,
    outcome_stats = NULL,
    selected_outcomes = NULL
  ) {
    
    # Create a list to store each sheet's data frame
    all_sheets <- list()
    
    # Create basic information table (will be repeated in each outcome sheet)
    general_info <- data.frame(
      Setting = c(
        "Analysis Date and Time", 
        "Software Used", 
        "R Packages", 
        "Operating System",
        "Reference Treatment",
        "Binary Outcome Effect Measure",
        "Continuous Outcome Effect Measure",
        "Random Effects Model",
        "Fixed Effects Model",
        "Heterogeneity Estimation Method",
        "Binary Outcome Analysis Method"
      ),
      Value = c(
        format(Sys.time(), "%Y/%m/%d %H:%M"), 
        R.version$version.string,
        paste(c("netmeta", "readxl", "dplyr", "showtext", "writexl", "tools", "meta"), collapse = ", "),
        .Platform$OS.type,
        ifelse(ref_treatment == "", "Automatically selected (most frequent treatment)", ref_treatment),
        binary_effect_measure,
        continuous_effect_measure,
        ifelse(include_random_effect, "Yes", "No"),
        ifelse(include_fixed_effect, "Yes", "No"),
        method_tau,
        method_binary
      ),
      stringsAsFactors = FALSE
    )
    
    # Add zero event handling information
    if (use_continuity_correction) {
      continuity_correction <- data.frame(
        Setting = "Zero Event Continuity Correction Value",
        Value = as.character(incr_value),
        stringsAsFactors = FALSE
      )
      general_info <- rbind(general_info, continuity_correction)
    } else {
      no_correction <- data.frame(
        Setting = "Zero Event Continuity Correction",
        Value = "No",
        stringsAsFactors = FALSE
      )
      general_info <- rbind(general_info, no_correction)
    }
    
    # Add global summary table
    summary_sheet <- data.frame(
      Setting = c(
        "Total Outcomes Analyzed", 
        "Outcomes Skipped", 
        "Analysis Completion Status",
        "Data Issues",
        "Recommendations"
      ),
      Value = c(
        as.character(length(selected_outcomes) - length(skipped_outcomes)),
        as.character(length(skipped_outcomes)),
        ifelse(length(skipped_outcomes) > 0, "Partial", "Complete"),
        if (length(skipped_outcomes) > 0) {
          paste("Skipped outcomes due to:", paste(unique(skip_reasons), collapse = "; "))
        } else {
          "None"
        },
        "Ensure all data files are correctly formatted before analysis."
      ),
      stringsAsFactors = FALSE
    )
    
    all_sheets[["Summary"]] <- summary_sheet
    
    # Create separate sheet for each outcome
    if (!is.null(outcome_stats) && length(outcome_stats) > 0) {
      for (outcome_name in names(outcome_stats)) {
        stats <- outcome_stats[[outcome_name]]
        
        # Create data frame for this outcome
        outcome_df <- rbind(
          general_info,
          data.frame(
            Setting = c("", "OUTCOME STATISTICS", ""),  # Add separator row
            Value = c("", outcome_name, ""),
            stringsAsFactors = FALSE
          ),
          data.frame(
            Setting = c(
              "Number of Studies",
              "Number of Pairwise Comparisons",
              "Number of Observations",
              "Number of Treatments",
              "Number of Designs",
              "",
              "ANALYSIS OUTPUTS",
              "Network Graph",
              "Forest Plots",
              "Treatment Ranking (P-scores)",
              "League Tables",
              "Funnel Plots",
              "Node-Split Analysis",
              "Pairwise Meta-Analysis",
              "GRADE-Ready Files"
            ),
            Value = c(
              as.character(stats$num_studies),
              as.character(stats$num_pairwise_comparisons),
              as.character(stats$num_observations),
              as.character(stats$num_treatments),
              as.character(stats$num_designs),
              "",
              "",
              "Generated",
              paste0("Generated for ", ifelse(include_random_effect, "random effects", ""), 
                     ifelse(include_random_effect && include_fixed_effect, " and ", ""),
                     ifelse(include_fixed_effect, "fixed effects", ""), " models"),
              paste0("Generated for ", ifelse(include_random_effect, "random effects", ""), 
                     ifelse(include_random_effect && include_fixed_effect, " and ", ""),
                     ifelse(include_fixed_effect, "fixed effects", ""), " models"),
              paste0("Generated for ", ifelse(include_random_effect, "random effects", ""), 
                     ifelse(include_random_effect && include_fixed_effect, " and ", ""),
                     ifelse(include_fixed_effect, "fixed effects", ""), " models"),
              paste0("Generated for ", ifelse(include_random_effect, "random effects", ""), 
                     ifelse(include_random_effect && include_fixed_effect, " and ", ""),
                     ifelse(include_fixed_effect, "fixed effects", ""), " models"),
              paste0("Generated for ", ifelse(include_random_effect, "random effects", ""), 
                     ifelse(include_random_effect && include_fixed_effect, " and ", ""),
                     ifelse(include_fixed_effect, "fixed effects", ""), " models"),
              paste0("Generated for ", ifelse(include_random_effect, "random effects", ""), 
                     ifelse(include_random_effect && include_fixed_effect, " and ", ""),
                     ifelse(include_fixed_effect, "fixed effects", ""), " models"),
              "Generated"
            ),
            stringsAsFactors = FALSE
          )
        )
        
        # Add to sheets list
        all_sheets[[outcome_name]] <- outcome_df
      }
    }
    
    # If there are skipped outcomes, add a dedicated sheet
    if (length(skipped_outcomes) > 0) {
      skipped_df <- data.frame(
        Outcome = skipped_outcomes,
        Reason = skip_reasons,
        stringsAsFactors = FALSE
      )
      all_sheets[["Skipped Outcomes"]] <- skipped_df
    }
    
    # Save report to output directory
    report_file <- file.path(output_dir, "NMA_Methodology_Report.xlsx")
    write_xlsx(all_sheets, path = report_file)
    
    cat("Methodology report saved to:", report_file, "\n")
  }
  
  
  ###############################################################################
  #                            Program Execution Area                           #
  ###############################################################################
  # Check data and output directories
  if (!dir.exists(data_dir)) {
    stop("Data directory does not exist:", data_dir)
  }
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
    cat("Created output directory:", output_dir, "\n")
  }
  
  
  # Get all xlsx files - fix file pattern matching
  excel_files <- list.files(path = data_dir, pattern = "\\.xlsx$", full.names = TRUE)
  
  outcome_names <- basename(excel_files)
  outcome_names <- file_path_sans_ext(outcome_names)  # Remove extension
  
  # Display all outcome data files to be analyzed
  cat("Will analyze the following outcome data files:\n")
  for (i in seq_along(outcome_names)) {
    cat(i, ": ", outcome_names[i], "\n")
  }
  
  # Default analyze all outcomes
  selected_files <- excel_files
  selected_outcomes <- outcome_names
  
  # Create a list to store outcomes not analyzed
  skipped_outcomes <- character(0)
  skip_reasons <- character(0)
  outcome_stats <- list()
  
  # Analyze each outcome
  for (i in seq_along(selected_files)) {
    current_file <- selected_files[i]
    current_outcome <- selected_outcomes[i]
    
    cat("\nAnalyzing outcome:", current_outcome, "\n")
    
    # Create output subdirectory for this outcome
    outcome_output_dir <- file.path(output_dir, current_outcome)
    if (!dir.exists(outcome_output_dir)) {
      dir.create(outcome_output_dir, recursive = TRUE)
    }
    
    # Create random effects and fixed effects subdirectories
    random_dir <- file.path(outcome_output_dir, "Results of Random Effect Model")
    fixed_dir <- file.path(outcome_output_dir, "Results of Common Effect Model")
    
    if (!dir.exists(random_dir) && include_random_effect) {
      dir.create(random_dir, recursive = TRUE)
    }
    if (!dir.exists(fixed_dir) && include_fixed_effect) {
      dir.create(fixed_dir, recursive = TRUE)
    }
    
    # Load data
    error_occurred <- FALSE
    data_check_passed <- TRUE
    check_reason <- ""
    
    tryCatch({
      data <- read_xlsx(current_file, sheet = 1, col_types = NULL, range = NULL, col_names = TRUE)
      
      # Check data type: binary or continuous variables
      is_binary <- all(c("event", "n") %in% colnames(data))
      is_continuous <- all(c("mean", "sd", "n") %in% colnames(data))
      
      # ------------ Data Check Module ------------
      cat("Starting data checks...\n")
      
      # 1. Binary variable check: whether event count is greater than sample size
      if (is_binary) {
        event_gt_n <- data %>% 
          filter(event > n) %>%
          nrow()
        
        if (event_gt_n > 0) {
          cat("Warning: Found", event_gt_n, "rows where event count exceeds sample size!\n")
          problematic_rows <- data %>% filter(event > n)
          print(problematic_rows)
          data_check_passed <- FALSE
          check_reason <- paste("There are", event_gt_n, "rows where event count exceeds sample size")
        }
      }
      
      # Continue processing data
      if (data_check_passed) {
        # Check if specified reference treatment exists
        available_treatments <- unique(data$treatment)
        original_ref_treatment <- ref_treatment
        
        if (ref_treatment == "" || is.null(ref_treatment) || !ref_treatment %in% available_treatments) {
          if (ref_treatment != "" && !is.null(ref_treatment)) {
            cat("Warning: Specified reference treatment '", ref_treatment, "' does not exist in data!\n")
            cat("Available treatments include:", paste(available_treatments, collapse = ", "), "\n")
          }
          
          cat("Will automatically select the most frequent treatment as reference.\n")
          
          # Count frequency of each treatment
          treatment_freq <- data %>%
            count(treatment) %>%
            arrange(desc(n))  # Sort by frequency descending
          
          # Select most frequent treatment as reference
          ref_treatment <- treatment_freq$treatment[1]
          cat("Auto-selected reference treatment:", ref_treatment, "\n")
          
          if (original_ref_treatment != "" && !is.null(original_ref_treatment)) {
            cat("Original specified reference treatment '", original_ref_treatment, "' changed to '", ref_treatment, "'\n")
          }
        } else {
          cat("Using specified reference treatment:", ref_treatment, "\n")
        }
        
        if (is_binary) {
          # Binary variable data processing
          cat("Detected binary variable data\n")
          data_processed <- data[, c(1:5)]
          colnames(data_processed) <- c("study", "treatment", "event", "n", "ROB")
          
          # Convert treatment-based data to comparison-based data format
          p1 <- pairwise(treatment, event, n, studlab = study,
                         data = data_processed, 
                         incr = ifelse(use_continuity_correction, incr_value, 0), 
                         allincr = FALSE, 
                         addincr = FALSE, 
                         allstudies = FALSE,
                         sm = binary_effect_measure)
          
          # 2. Check network connectivity
          net_connection <- netconnection(p1)
          print(net_connection)
          
          if (length(net_connection$comb.fixed) > 1 || length(net_connection$comb.random) > 1) {
            cat("Warning: Network has separate sub-networks!\n")
            data_check_passed <- FALSE
            check_reason <- "Network has separate sub-networks, cannot perform overall network analysis"
          }
          
          if (data_check_passed) {
            # Use netmeta for network meta-analysis
            net1 <- netmetabin(p1, 
                               ref = ref_treatment, 
                               sm = binary_effect_measure, 
                               method = method_binary,
                               comb.fixed = include_fixed_effect,
                               comb.random = include_random_effect,
                               method.tau = method_tau)
            data_type <- "binary"
            effect_measure <- binary_effect_measure  # Set effect measure for traditional meta-analysis
          }
          
        } else if (is_continuous) {
          # Continuous variable data processing
          cat("Detected continuous variable data\n")
          data_processed <- data[, c(1:6)]
          colnames(data_processed) <- c("study", "treatment", "n", "mean", "sd", "ROB")
          
          # Convert continuous outcome data
          p1 <- pairwise(treatment, n=n, mean=mean, sd=sd, studlab = study,
                         data = data_processed, 
                         incr = 0, 
                         allincr = FALSE, 
                         addincr = FALSE, 
                         allstudies = FALSE,
                         sm = continuous_effect_measure)
          
          # 2. Check network connectivity
          net_connection <- netconnection(p1)
          print(net_connection)
          
          if (length(net_connection$comb.fixed) > 1 || length(net_connection$comb.random) > 1) {
            cat("Warning: Network has separate sub-networks!\n")
            data_check_passed <- FALSE
            check_reason <- "Network has separate sub-networks, cannot perform overall network analysis"
          }
          
          if (data_check_passed) {
            # Use netmeta for continuous outcome network meta-analysis
            net1 <- netmeta(p1, 
                            ref = ref_treatment,
                            sm = continuous_effect_measure,
                            comb.fixed = include_fixed_effect,
                            comb.random = include_random_effect,
                            method.tau = method_tau)
            data_type <- "continuous"
            effect_measure <- continuous_effect_measure  # Set effect measure for traditional meta-analysis
          }
          
        } else {
          stop("Data format does not meet requirements, cannot identify as binary or continuous variables")
        }
        
        if (!data_check_passed) {
          cat("Data check failed, skipping analysis for this outcome. Reason:", check_reason, "\n")
          skipped_outcomes <- c(skipped_outcomes, current_outcome)
          skip_reasons <- c(skip_reasons, check_reason)
          next  # Skip current outcome, continue to next outcome
        }
        
        print(summary(net1))
        
        # Set output file name prefix
        file_prefix <- current_outcome
        
        # Netgraph - save in main directory
        treatments <- net1$trts
        n.sample <- tapply(data_processed$n, data_processed$treatment, sum)
        print(n.sample)
        n.sample <- n.sample[treatments]
        pdf(file.path(outcome_output_dir, paste0(file_prefix, "-netgraph.pdf")), width=16, height=10)
        netgraph(net1,
                 thickness = "number.of.studies",
                 dim = "2d",
                 points = TRUE, 
                 cex.points = n.sample,
                 family = font_name, 
                 offset = 0.03,
                 iterate = FALSE,
                 plastic = FALSE,
                 col.points = "#9D99D5",
                 col = "#9A008A",
                 cex = 1)
        dev.off()
        
        # Get ordering
        ord <- sort(unique(c(net1$data$treat1, net1$data$treat2)))
        ord <- c(ord[ord != ref_treatment], ref_treatment)
        
        # Random effects model results
        if (include_random_effect) {
          # Comparison-adjusted funnel plot for random effects
          pdf(file.path(random_dir, paste0(file_prefix, "-funnel plot.pdf")), width=10, height=8)
          funnel(net1, order = ord, method.bias = c("Egger", "Begg", "Thompson"), 
                 digits.pval = 3, pooled = "random")
          dev.off()
          
          # Draw forest plot (Random Effects)
          pdf(file.path(random_dir, paste0(file_prefix, "-forestplot.pdf")), width=9, height=7)
          forest(net1, ref=ref_treatment, rightcols=c("effect", "ci", "Pscore"),
                 family = font_name,
                 rightlabs="P-Score", pooled="random",
                 sortvar=Pscore, leftcols=c("studlab", "k"),
                 leftlabs=c("Treatment", "name3"),
                 drop=TRUE, small.values="good", smlab="Random Effects Model")
          dev.off()
          
          # nettable (Random Effects)
          nt1 <- nettable(net1, digits = 2)
          print(nt1, common = FALSE)
          # Save as both xlsx and csv formats
          write_xlsx(nt1$random, path = file.path(random_dir, paste0(file_prefix, "-nettable.xlsx")))
          # Save as CSV format
          write.csv(nt1$random, file = file.path(random_dir, paste0(file_prefix, "-nettable.csv")), 
                    row.names = FALSE)
          
          # netsplit (Random Effects)
          ns1 <- netsplit(net1)
          n_comparisons <- length(ns1$comparison)
          height <- n_comparisons * 0.7
          pdf(file.path(random_dir, paste0(file_prefix, "-random-nodesplit.pdf")), width=8, height=height)
          forest(ns1, pooled="random",
                 overall = TRUE, direct = TRUE, indirect = TRUE,
                 col.square = "blue", col.square.lines = "blue",
                 col.inside = "white",
                 col.diamond = "red", col.diamond.lines = "red",
                 family = font_name,
                 fontsize = 6, spacing = 0.5, addrow.subgroups = TRUE,
                 show = "all")
          dev.off()
          
          # League table (Random Effects)
          trts <- sort(unique(c(net1$data$treat1, net1$data$treat2)))
          trts <- c(trts[trts != ref_treatment], ref_treatment)
          
          league1 <- netleague(net1, digits = 2, direct = TRUE, seq = trts,
                               bracket = "(", separator = " - ")
          
          write_xlsx(league1$random, path = file.path(random_dir, paste0(file_prefix, "-league table.xlsx")))
          generate_interactive_league_table(
            net_result = net1,
            outcome_name = current_outcome,
            model_type = "random",
            effect_measure = effect_measure,
            output_filepath = file.path(random_dir, paste0(file_prefix, "-interactive_league_table.html"))
          )
          
          # netpairwise for Random Effects
          np1_random <- netpairwise(net1, random = TRUE)
          write.table(np1_random, file = file.path(random_dir, paste0(file_prefix, "-netpairwise.csv")), 
                      row.names = FALSE, col.names = TRUE, sep = ",")
          
          # Generate traditional pairwise meta forest plot (random effects model)
          pairwise_data_random <- np1_random
          
          # Perform traditional meta-analysis (random effects)
          meta_result_random <- metagen(data = pairwise_data_random, 
                                        TE = TE, 
                                        seTE = seTE, 
                                        subset = NULL, 
                                        sm = effect_measure,
                                        byvar = subgroup, 
                                        studlab = studlab,
                                        comb.fixed = TRUE, 
                                        comb.random = TRUE,
                                        overall = FALSE)
          
          # Save meta_result_random as CSV, this is a key file needed for GRADE module
          meta_result_table_random <- as.data.frame(meta_result_random)
          write.csv(meta_result_table_random, file = file.path(random_dir, paste0(file_prefix, "-meta_result_random.csv")), 
                    row.names = FALSE)
          
          # Generate forest plot (random effects)
          study_count <- nrow(pairwise_data_random)
          height_inches <- n_comparisons * 4
          
          pdf(file.path(random_dir, paste0(file_prefix, "-pairwise forestplot.pdf")), 
              width = 12, height = height_inches)
          forest(meta_result_random, 
                 digits = 2, 
                 family = font_name,
                 fontsize = 9.5, 
                 lwd = 2,
                 col.diamond.fixed = "lightslategray",
                 col.diamond.lines.fixed = "lightslategray",
                 col.diamond.random = "maroon",
                 col.diamond.lines.random = "maroon",
                 col.square = "skyblue",
                 col.study = "lightslategray",
                 lty.fixed = 4, 
                 plotwidth = "8cm",
                 colgap.forest.left = "1cm",
                 colgap.forest.right = "1cm",
                 just.forest = "right",
                 colgap.left = "0.5cm",
                 colgap.right = "0.5cm",
                 weight.study = "random",
                 rightcols = c("effect", "ci", "w.random"),
                 rightlabs = c("Estimate", "95% CI", "Weight(%)"))
          dev.off()
          
          # netrank (Random Effects)
          Pscore_random <- netrank(net1, small.values = small_values_direction)
          
          # Save Pscore results as txt
          capture.output(print(Pscore_random), 
                         file = file.path(random_dir, paste0(file_prefix, "-Pscore_random.txt")))
          
          # Publication bias detection
          np1_random_separate <- netpairwise(net1, random = TRUE, separate = TRUE)
          
          # Add debug information
          cat("np1_random_separate length:", length(np1_random_separate), "\n")
          cat("np1_random_separate names:", names(np1_random_separate), "\n")
          
          egger_results <- list()
          
          # Check if there is comparison data
          if (length(np1_random_separate) == 0) {
            cat("Warning: np1_random_separate is empty, cannot perform Egger test\n")
            egger_df <- data.frame(
              comparison = "No available comparisons",
              n_studies = 0,
              p_egger = NA,
              reason = "No available comparison data",
              stringsAsFactors = FALSE
            )
          } else {
            # Fix: use index instead of names to iterate
            for (i in 1:length(np1_random_separate)) {
              current_meta <- np1_random_separate[[i]]
              
              # Try to extract comparison information from metagen object
              if (is.null(names(np1_random_separate)) || names(np1_random_separate)[i] == "") {
                # If no names, try to extract comparison info from object
                if (!is.null(current_meta$complab)) {
                  comp_name <- current_meta$complab
                } else if (!is.null(current_meta$call)) {
                  comp_name <- paste("Comparison", i)
                } else {
                  comp_name <- paste("Comparison", i)
                }
              } else {
                comp_name <- names(np1_random_separate)[i]
              }
              
              cat("Analyzing comparison", i, ":", comp_name, "\n")
              
              # Add more debug information
              cat("  Current comparison type:", class(current_meta), "\n")
              
              # Check if current_meta is a valid metagen object
              if (!"metagen" %in% class(current_meta)) {
                cat("  Skip: not a valid metagen object\n")
                egger_results[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = 0,
                  p_egger = NA,
                  reason = "Not a valid metagen object",
                  stringsAsFactors = FALSE
                )
                next
              }
              
              # Check if there are enough studies
              n_studies <- length(current_meta$studlab)
              cat("  Number of studies:", n_studies, "\n")
              
              if (n_studies > 0) {
                cat("  Study labels:", paste(current_meta$studlab, collapse = ", "), "\n")
              }
              
              # Check if number of studies >= 3 (Egger test recommends at least 3 studies)
              if (n_studies < 3) {
                cat("  Skip: fewer than 3 studies\n")
                egger_results[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = n_studies,
                  p_egger = NA,
                  reason = "Fewer than 3 studies, cannot perform Egger test",
                  stringsAsFactors = FALSE
                )
                next
              }
              
              tryCatch({
                cat("  Attempting Egger test...\n")
                # Perform Egger regression test
                bias_test <- metabias(current_meta, method = "Egger", digits = 3)
                
                # Extract p value
                p_value <- bias_test$pval
                cat("  Egger test successful, p value:", p_value, "\n")
                
                egger_results[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = n_studies,
                  p_egger = p_value,
                  reason = "Success",
                  stringsAsFactors = FALSE
                )
              }, error = function(e) {
                cat("  Egger test error:", e$message, "\n")
                egger_results[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = n_studies,
                  p_egger = NA,
                  reason = paste0("Error: ", e$message),
                  stringsAsFactors = FALSE
                )
              })
            }
            
            # Combine results
            cat("egger_results length:", length(egger_results), "\n")
            
            if (length(egger_results) > 0) {
              # Print each result for debugging
              for (i in 1:length(egger_results)) {
                cat("Result", i, ":\n")
                print(egger_results[[i]])
              }
              
              egger_df <- do.call(rbind, egger_results)
              rownames(egger_df) <- NULL
            } else {
              egger_df <- data.frame(
                comparison = character(0),
                n_studies = numeric(0),
                p_egger = numeric(0),
                reason = character(0),
                stringsAsFactors = FALSE
              )
            }
          }
          
          # Check again before saving as CSV file
          cat("Final egger_df dimensions:", dim(egger_df), "\n")
          cat("Final egger_df content:\n")
          print(egger_df)
          
          egger_output_file <- file.path(random_dir, paste0(file_prefix, "-egger_test_results.csv"))
          write.csv(egger_df, egger_output_file, row.names = FALSE)
          
        }
        
        # Fixed effects model results
        if (include_fixed_effect) {
          # Comparison-adjusted funnel plot for fixed effects
          pdf(file.path(fixed_dir, paste0(file_prefix, "-funnel plot.pdf")), width=10, height=8)
          funnel(net1, order = ord, method.bias = c("Egger", "Begg", "Thompson"), 
                 digits.pval = 3, pooled = "fixed")
          dev.off()
          
          # Draw forest plot (Fixed Effects)
          pdf(file.path(fixed_dir, paste0(file_prefix, "-forestplot.pdf")), width=9, height=7)
          forest(net1, ref=ref_treatment, rightcols=c("effect", "ci", "Pscore"),
                 family = font_name,
                 rightlabs="P-Score", pooled="fixed",
                 sortvar=Pscore, leftcols=c("studlab", "k"),
                 leftlabs=c("Treatment", "name3"),
                 drop=TRUE, small.values="good", smlab="Fixed Effects Model")
          dev.off()
          
          # nettable (Fixed Effects)
          nt1 <- nettable(net1, digits = 2)
          print(nt1, common = TRUE)
          # Save as both xlsx and csv formats
          write_xlsx(nt1$fixed, path = file.path(fixed_dir, paste0(file_prefix, "-nettable.xlsx")))
          # Save as CSV format
          write.csv(nt1$fixed, file = file.path(fixed_dir, paste0(file_prefix, "-nettable.csv")), 
                    row.names = FALSE)
          
          # netsplit (Fixed Effects)
          ns1 <- netsplit(net1)
          pdf(file.path(fixed_dir, paste0(file_prefix, "-fixed-nodesplit.pdf")), width=8, height=height)
          forest(ns1, pooled="fixed",
                 overall = TRUE, direct = TRUE, indirect = TRUE,
                 col.square = "blue", col.square.lines = "blue",
                 col.inside = "white",
                 col.diamond = "red", col.diamond.lines = "red",
                 family = font_name,
                 fontsize = 6, spacing = 0.5, addrow.subgroups = TRUE,
                 show = "all")
          dev.off()
          
          # League table (Fixed Effects)
          write_xlsx(league1$fixed, path = file.path(fixed_dir, paste0(file_prefix, "-league table.xlsx")))
          generate_interactive_league_table(
            net_result = net1,
            outcome_name = current_outcome,
            model_type = "fixed",
            effect_measure = effect_measure,
            output_filepath = file.path(fixed_dir, paste0(file_prefix, "-interactive_league_table.html"))
          )
          
          # netpairwise for Fixed Effects
          np1_fixed <- netpairwise(net1, random = FALSE)
          write.table(np1_fixed, file = file.path(fixed_dir, paste0(file_prefix, "-netpairwise.csv")), 
                      row.names = FALSE, col.names = TRUE, sep = ",")
          
          # Generate traditional pairwise meta forest plot (fixed effects model)
          pairwise_data_fixed <- np1_fixed
          
          # Perform traditional meta-analysis (fixed effects)
          meta_result_fixed <- metagen(data = pairwise_data_fixed, 
                                       TE = TE, 
                                       seTE = seTE, 
                                       subset = NULL, 
                                       sm = effect_measure,
                                       byvar = subgroup, 
                                       studlab = studlab,
                                       comb.fixed = TRUE, 
                                       comb.random = TRUE,
                                       overall = FALSE)
          
          # Save meta_result_fixed as CSV, this is a key file needed for GRADE module
          meta_result_table_fixed <- as.data.frame(meta_result_fixed)
          write.csv(meta_result_table_fixed, file = file.path(fixed_dir, paste0(file_prefix, "-meta_result_fixed.csv")), 
                    row.names = FALSE)
          
          # Generate forest plot (fixed effects)
          study_count <- nrow(pairwise_data_fixed)
          height_inches <- n_comparisons * 4
          
          pdf(file.path(fixed_dir, paste0(file_prefix, "-pairwise forestplot.pdf")), 
              width = 12, height = height_inches)
          forest(meta_result_fixed, 
                 digits = 2, 
                 family = font_name,
                 fontsize = 9.5, 
                 lwd = 2,
                 col.diamond.fixed = "lightslategray",
                 col.diamond.lines.fixed = "lightslategray",
                 col.diamond.random = "maroon",
                 col.diamond.lines.random = "maroon",
                 col.square = "skyblue",
                 col.study = "lightslategray",
                 lty.fixed = 4, 
                 plotwidth = "8cm",
                 colgap.forest.left = "1cm",
                 colgap.forest.right = "1cm",
                 just.forest = "right",
                 colgap.left = "0.5cm",
                 colgap.right = "0.5cm",
                 weight.study = "common",
                 rightcols = c("effect", "ci", "w.fixed"),
                 rightlabs = c("Estimate", "95% CI", "Weight(%)"))
          dev.off()
          
          # netrank (Fixed Effects)
          Pscore_fixed <- netrank(net1, small.values = small_values_direction)
          
          # Save Pscore results as txt
          capture.output(print(Pscore_fixed), 
                         file = file.path(fixed_dir, paste0(file_prefix, "-Pscore_fixed.txt")))
          
          # Publication bias detection
          np1_fixed_separate <- netpairwise(net1, random = FALSE, separate = TRUE)
          
          # Add debug information
          cat("Fixed effects model - np1_fixed_separate length:", length(np1_fixed_separate), "\n")
          cat("Fixed effects model - np1_fixed_separate names:", names(np1_fixed_separate), "\n")
          
          egger_results_fixed <- list()
          
          # Check if there is comparison data
          if (length(np1_fixed_separate) == 0) {
            cat("Warning: Fixed effects model np1_fixed_separate is empty, cannot perform Egger test\n")
            egger_df_fixed <- data.frame(
              comparison = "No available comparisons",
              n_studies = 0,
              p_egger = NA,
              reason = "No available comparison data",
              stringsAsFactors = FALSE
            )
          } else {
            # Use index instead of names to iterate
            for (i in 1:length(np1_fixed_separate)) {
              current_meta <- np1_fixed_separate[[i]]
              
              # Try to extract comparison information from metagen object
              if (is.null(names(np1_fixed_separate)) || names(np1_fixed_separate)[i] == "") {
                # If no names, try to extract comparison info from object
                if (!is.null(current_meta$complab)) {
                  comp_name <- current_meta$complab
                } else if (!is.null(current_meta$call)) {
                  comp_name <- paste("Comparison", i)
                } else {
                  comp_name <- paste("Comparison", i)
                }
              } else {
                comp_name <- names(np1_fixed_separate)[i]
              }
              
              cat("Fixed effects model - Analyzing comparison", i, ":", comp_name, "\n")
              
              # Add more debug information
              cat("  Current comparison type:", class(current_meta), "\n")
              
              # Check if current_meta is a valid metagen object
              if (!"metagen" %in% class(current_meta)) {
                cat("  Skip: not a valid metagen object\n")
                egger_results_fixed[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = 0,
                  p_egger = NA,
                  reason = "Not a valid metagen object",
                  stringsAsFactors = FALSE
                )
                next
              }
              
              # Check if there are enough studies
              n_studies <- length(current_meta$studlab)
              cat("  Number of studies:", n_studies, "\n")
              
              if (n_studies > 0) {
                cat("  Study labels:", paste(current_meta$studlab, collapse = ", "), "\n")
              }
              
              # Check if number of studies >= 3 (Egger test recommends at least 3 studies)
              if (n_studies < 3) {
                cat("  Skip: fewer than 3 studies\n")
                egger_results_fixed[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = n_studies,
                  p_egger = NA,
                  reason = "Fewer than 3 studies, cannot perform Egger test",
                  stringsAsFactors = FALSE
                )
                next
              }
              
              tryCatch({
                cat("  Attempting Egger test...\n")
                # Perform Egger regression test
                bias_test <- metabias(current_meta, method = "Egger", digits = 3)
                
                # Extract p value
                p_value <- bias_test$pval
                cat("  Egger test successful, p value:", p_value, "\n")
                
                egger_results_fixed[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = n_studies,
                  p_egger = p_value,
                  reason = "Success",
                  stringsAsFactors = FALSE
                )
              }, error = function(e) {
                cat("  Egger test error:", e$message, "\n")
                egger_results_fixed[[i]] <- data.frame(
                  comparison = comp_name,
                  n_studies = n_studies,
                  p_egger = NA,
                  reason = paste0("Error: ", e$message),
                  stringsAsFactors = FALSE
                )
              })
            }
            
            # Combine results
            cat("Fixed effects model - egger_results_fixed length:", length(egger_results_fixed), "\n")
            
            if (length(egger_results_fixed) > 0) {
              # Print each result for debugging
              for (i in 1:length(egger_results_fixed)) {
                cat("Fixed effects model - Result", i, ":\n")
                print(egger_results_fixed[[i]])
              }
              
              egger_df_fixed <- do.call(rbind, egger_results_fixed)
              rownames(egger_df_fixed) <- NULL
            } else {
              egger_df_fixed <- data.frame(
                comparison = character(0),
                n_studies = numeric(0),
                p_egger = numeric(0),
                reason = character(0),
                stringsAsFactors = FALSE
              )
            }
          }
          
          # Check again before saving as CSV file
          cat("Fixed effects model - Final egger_df_fixed dimensions:", dim(egger_df_fixed), "\n")
          cat("Fixed effects model - Final egger_df_fixed content:\n")
          print(egger_df_fixed)
          
          egger_output_file_fixed <- file.path(fixed_dir, paste0(file_prefix, "-egger_test_results.csv"))
          write.csv(egger_df_fixed, egger_output_file_fixed, row.names = FALSE)
        }
        
        # Capture summary(net1) output
        summary_text <- capture.output(summary(net1))
        
        # Extract statistical information
        num_studies <- as.numeric(gsub("[^0-9]", "", grep("Number of studies: k =", summary_text, value = TRUE)))
        num_pairwise_comparisons <- as.numeric(gsub("[^0-9]", "", grep("Number of pairwise comparisons: m =", summary_text, value = TRUE)))
        num_observations <- as.numeric(gsub("[^0-9]", "", grep("Number of observations: o =", summary_text, value = TRUE)))
        num_treatments <- as.numeric(gsub("[^0-9]", "", grep("Number of treatments: n =", summary_text, value = TRUE)))
        num_designs <- as.numeric(gsub("[^0-9]", "", grep("Number of designs: d =", summary_text, value = TRUE)))
        
        # Store statistical information
        stats <- list(
          outcome = current_outcome,
          num_studies = num_studies,
          num_pairwise_comparisons = num_pairwise_comparisons,
          num_observations = num_observations,
          num_treatments = num_treatments,
          num_designs = num_designs
        )
        
        # Add statistical information to list
        outcome_stats[[current_outcome]] <- stats
        
        # Save original data (for subsequent GRADE assessment)
        write.csv(data_processed, file = file.path(outcome_output_dir, paste0(file_prefix, "-original_data.csv")), 
                  row.names = FALSE)
        
        # Create analysis settings data frame
        analysis_settings <- data.frame(
          setting = c(
            "data_type", 
            "effect_measure", 
            "ref_treatment", 
            "model_types", 
            "method_tau", 
            "method_binary",
            "use_continuity_correction",
            "incr_value"
          ),
          value = c(
            data_type,  # Determined through previous is_binary/is_continuous check
            effect_measure,  # Passed from binary_effect_measure or continuous_effect_measure
            ref_treatment, 
            ifelse(include_random_effect && include_fixed_effect, "both",
                   ifelse(include_random_effect, "random", "fixed")),
            method_tau,
            method_binary,
            as.character(use_continuity_correction),
            as.character(incr_value)
          ),
          stringsAsFactors = FALSE
        )
        
        # Save to outcome main directory (e.g., Results/Outcome1/)
        write.csv(
          analysis_settings, 
          file = file.path(outcome_output_dir, paste0(file_prefix, "-analysis_settings.csv")),
          row.names = FALSE
        )
        
        cat("Outcome", current_outcome, "analysis completed!\n")
      } else {
        cat("Outcome", current_outcome, "data check failed, skipping analysis. Reason:", check_reason, "\n")
        skipped_outcomes <- c(skipped_outcomes, current_outcome)
        skip_reasons <- c(skip_reasons, check_reason)
      }
    }, error = function(e) {
      cat("Error analyzing outcome", current_outcome, ":", e$message, "\n")
      skipped_outcomes <<- c(skipped_outcomes, current_outcome)
      skip_reasons <<- c(skip_reasons, paste("Error:", e$message))
      error_occurred <- TRUE
    })
    
    # If error occurred, log but don't interrupt loop, continue analyzing other outcomes
    if (error_occurred) {
      error_occurred <- FALSE  # Reset error flag, continue to next outcome
    }
  }
  
  cat("\nNMA analysis process completed! Results saved in output directory, you can proceed with GRADE assessment.\n")
  
  # Report unanalyzed outcomes
  if (length(skipped_outcomes) > 0) {
    cat("\nThe following outcomes were not fully analyzed:\n")
    for (i in 1:length(skipped_outcomes)) {
      cat(skipped_outcomes[i], "- Reason:", skip_reasons[i], "\n")
    }
    cat("\nPlease check the data for these outcomes, resolve issues and re-run.\n")
  } else {
    cat("\nAll outcomes analyzed successfully.\n")
  }
  
  # Generate methodology report
  generate_methodology_report(
    ref_treatment = ref_treatment,
    binary_effect_measure = binary_effect_measure,
    continuous_effect_measure = continuous_effect_measure,
    include_random_effect = include_random_effect,
    include_fixed_effect = include_fixed_effect,
    method_tau = method_tau,
    method_binary = method_binary,
    use_continuity_correction = use_continuity_correction,
    incr_value = incr_value,
    font_name = font_name,
    font_path = font_path,
    data_dir = data_dir,
    output_dir = output_dir,
    skipped_outcomes = skipped_outcomes,
    skip_reasons = skip_reasons,
    outcome_stats = outcome_stats,
    selected_outcomes = selected_outcomes
  )
}

# =========================
# 5. Launch Shiny App
# =========================
shinyApp(ui, server)

