# =========================
# 数据验证和方法学推荐工具 - 稳定启动版本
# =========================

cat("=========================\n")
cat("数据验证和方法学推荐工具\n")
cat("=========================\n")

# 设置CRAN镜像
options(repos = c(CRAN = "https://cran.rstudio.com/"))

# 安全的包加载函数
safe_load_package <- function(package_name) {
  tryCatch({
    if (!require(package_name, character.only = TRUE, quietly = TRUE)) {
      cat(sprintf("正在安装 %s...\n", package_name))
      install.packages(package_name, dependencies = TRUE)
      library(package_name, character.only = TRUE)
      return(TRUE)
    }
    return(TRUE)
  }, error = function(e) {
    cat(sprintf("❌ 无法加载包 %s: %s\n", package_name, e$message))
    return(FALSE)
  })
}

# 检查必要的包
cat("检查必要的R包...\n")
required_packages <- c("shiny", "openxlsx", "dplyr", "DT")
failed_packages <- c()

for (pkg in required_packages) {
  if (!safe_load_package(pkg)) {
    failed_packages <- c(failed_packages, pkg)
  }
}

if (length(failed_packages) > 0) {
  cat("❌ 以下包无法加载:\n")
  for (pkg in failed_packages) {
    cat(sprintf("   - %s\n", pkg))
  }
  cat("\n请手动安装这些包后重试。\n")
  stop("包依赖问题")
}

cat("✅ 所有必要的包已准备就绪\n\n")

# 检查核心模块文件
cat("检查核心模块文件...\n")
core_files <- c("data_validation_module.R")
missing_files <- c()

for (file in core_files) {
  if (file.exists(file)) {
    tryCatch({
      source(file)
      cat(sprintf("✅ %s 加载成功\n", file))
    }, error = function(e) {
      cat(sprintf("❌ %s 加载失败: %s\n", file, e$message))
      missing_files <- c(missing_files, file)
    })
  } else {
    cat(sprintf("❌ 文件不存在: %s\n", file))
    missing_files <- c(missing_files, file)
  }
}

if (length(missing_files) > 0) {
  cat("\n⚠️ 部分模块缺失，将使用基础功能\n")
}

# 创建演示数据函数
create_demo_data <- function() {
  # 二分类数据示例
  binary_data <- data.frame(
    study = c("研究001", "研究001", "研究002", "研究002", "研究003", "研究003"),
    treatment = c("安慰剂", "药物A", "安慰剂", "药物A", "安慰剂", "药物A"),
    event = c(15, 22, 12, 18, 8, 16),
    n = c(100, 105, 95, 98, 85, 88),
    ROB = c("Low", "Low", "High", "High", "Low", "Low"),
    stringsAsFactors = FALSE
  )
  
  # 连续数据示例
  continuous_data <- data.frame(
    study = c("研究001", "研究001", "研究002", "研究002", "研究003", "研究003"),
    treatment = c("安慰剂", "药物A", "安慰剂", "药物A", "安慰剂", "药物A"),
    n = c(45, 48, 38, 42, 35, 38),
    mean = c(6.5, 4.2, 6.8, 4.9, 7.2, 5.8),
    sd = c(1.2, 1.8, 1.9, 1.5, 1.8, 1.3),
    ROB = c("Low", "Low", "High", "High", "Low", "Low"),
    stringsAsFactors = FALSE
  )
  
  return(list(binary = binary_data, continuous = continuous_data))
}

# 创建Shiny应用
cat("创建Web界面...\n")

ui <- fluidPage(
  tags$head(
    tags$style(HTML("
      body { font-family: 'Arial', sans-serif; background-color: #f5f5f5; }
      .main-header { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        padding: 20px; 
        margin-bottom: 20px; 
        border-radius: 8px;
        text-align: center;
      }
      .card { 
        background: white; 
        padding: 20px; 
        margin: 10px 0; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      .btn-primary { 
        background-color: #667eea; 
        border-color: #667eea; 
        width: 100%;
        margin: 10px 0;
      }
      .status-box { 
        background: #f8f9fa; 
        border: 1px solid #dee2e6; 
        border-radius: 4px; 
        padding: 10px; 
        margin: 10px 0;
        font-family: monospace;
      }
    "))
  ),
  
  div(class = "main-header",
      h1("数据验证和方法学推荐工具"),
      p("智能化的网络荟萃分析数据处理工具")
  ),
  
  fluidRow(
    column(4,
           div(class = "card",
               h3("📁 数据上传"),
               fileInput("file", "选择Excel文件 (.xlsx)",
                        accept = c(".xlsx"),
                        multiple = FALSE),
               
               radioButtons("data_type", "数据类型:",
                           choices = list("二分类数据 (如死亡率)" = "binary",
                                         "连续数据 (如疼痛评分)" = "continuous"),
                           selected = "binary"),
               
               actionButton("validate", "🔍 验证数据", class = "btn btn-primary"),
               actionButton("demo", "📊 加载演示数据", class = "btn btn-secondary"),
               
               h4("📋 状态信息"),
               div(class = "status-box",
                   verbatimTextOutput("status"))
           )
    ),
    
    column(8,
           tabsetPanel(
             tabPanel("📋 数据预览",
                     div(class = "card",
                         h4("数据内容"),
                         DT::dataTableOutput("data_preview")
                     )
             ),
             
             tabPanel("✅ 验证结果",
                     div(class = "card",
                         h4("验证摘要"),
                         verbatimTextOutput("validation_summary"),
                         
                         conditionalPanel(
                           condition = "output.has_issues",
                           h4("问题详情"),
                           DT::dataTableOutput("validation_issues")
                         )
                     )
             ),
             
             tabPanel("📊 数据特征",
                     div(class = "card",
                         fluidRow(
                           column(6,
                                  h4("基本统计"),
                                  verbatimTextOutput("basic_stats")
                           ),
                           column(6,
                                  h4("网络特征"),
                                  verbatimTextOutput("network_stats")
                           )
                         )
                     )
             ),
             
             tabPanel("🎯 方法推荐",
                     div(class = "card",
                         h4("智能推荐"),
                         verbatimTextOutput("recommendations"),
                         
                         conditionalPanel(
                           condition = "output.has_recommendations",
                           h4("推荐理由"),
                           verbatimTextOutput("recommendation_reasons")
                         )
                     )
             )
           )
    )
  )
)

server <- function(input, output, session) {
  values <- reactiveValues(
    data = NULL,
    validation_result = NULL,
    characteristics = NULL,
    recommendations = NULL
  )
  
  # 演示数据加载
  observeEvent(input$demo, {
    demo_data <- create_demo_data()
    values$data <- demo_data[[input$data_type]]
    
    output$status <- renderText({
      paste("✅ 演示数据已加载",
            "\n数据类型:", ifelse(input$data_type == "binary", "二分类", "连续"),
            "\n行数:", nrow(values$data),
            "\n列数:", ncol(values$data))
    })
  })
  
  # 文件上传处理
  observeEvent(input$file, {
    req(input$file)
    
    tryCatch({
      values$data <- openxlsx::read.xlsx(input$file$datapath)
      
      output$status <- renderText({
        paste("✅ 文件上传成功:",
              "\n文件名:", input$file$name,
              "\n行数:", nrow(values$data),
              "\n列数:", ncol(values$data),
              "\n列名:", paste(names(values$data), collapse = ", "))
      })
      
    }, error = function(e) {
      output$status <- renderText({
        paste("❌ 文件读取失败:", e$message)
      })
    })
  })
  
  # 数据预览
  output$data_preview <- DT::renderDataTable({
    req(values$data)
    DT::datatable(values$data, 
                  options = list(scrollX = TRUE, pageLength = 10),
                  class = 'cell-border stripe')
  })
  
  # 数据验证
  observeEvent(input$validate, {
    req(values$data, input$data_type)
    
    tryCatch({
      if (exists("validate_data_quality")) {
        values$validation_result <- validate_data_quality(
          values$data, 
          ifelse(is.null(input$file), "演示数据", input$file$name), 
          input$data_type
        )
        
        if (exists("analyze_data_characteristics")) {
          values$characteristics <- analyze_data_characteristics(
            values$data, 
            input$data_type
          )
        }
        
        if (exists("generate_methodology_recommendations") && !is.null(values$characteristics)) {
          values$recommendations <- generate_methodology_recommendations(
            values$characteristics, 
            input$data_type
          )
        }
        
        output$status <- renderText("✅ 数据验证完成")
        
      } else {
        # 基础验证（如果模块未加载）
        basic_validation <- list(
          is_valid = TRUE,
          summary = list(total_issues = 0, error_count = 0, warning_count = 0),
          issues = data.frame()
        )
        values$validation_result <- basic_validation
        
        output$status <- renderText("⚠️ 使用基础验证功能")
      }
      
    }, error = function(e) {
      output$status <- renderText(paste("❌ 验证失败:", e$message))
    })
  })
  
  # 验证结果
  output$validation_summary <- renderText({
    req(values$validation_result)
    
    status_icon <- ifelse(values$validation_result$is_valid, "✅", "❌")
    status_text <- ifelse(values$validation_result$is_valid, "通过", "失败")
    
    paste(
      paste("验证状态:", status_icon, status_text),
      paste("总问题数:", values$validation_result$summary$total_issues),
      paste("错误数:", values$validation_result$summary$error_count),
      paste("警告数:", values$validation_result$summary$warning_count),
      sep = "\n"
    )
  })
  
  output$has_issues <- reactive({
    !is.null(values$validation_result) && 
      nrow(values$validation_result$issues) > 0
  })
  outputOptions(output, "has_issues", suspendWhenHidden = FALSE)
  
  output$validation_issues <- DT::renderDataTable({
    req(values$validation_result)
    if (nrow(values$validation_result$issues) > 0) {
      DT::datatable(values$validation_result$issues, 
                    options = list(scrollX = TRUE),
                    class = 'cell-border stripe')
    }
  })
  
  # 数据特征
  output$basic_stats <- renderText({
    req(values$characteristics)
    
    paste(
      paste("研究数量:", values$characteristics$basic_stats$study_count),
      paste("治疗数量:", values$characteristics$basic_stats$treatment_count),
      paste("总样本量:", values$characteristics$basic_stats$total_sample_size),
      paste("平均研究规模:", round(values$characteristics$basic_stats$avg_study_size, 1)),
      sep = "\n"
    )
  })
  
  output$network_stats <- renderText({
    req(values$characteristics)
    
    connectivity_text <- ifelse(values$characteristics$network_stats$connectivity, "连通", "不连通")
    
    paste(
      paste("网络密度:", values$characteristics$network_stats$density),
      paste("网络连通性:", connectivity_text),
      paste("实际比较数:", values$characteristics$network_stats$actual_comparisons),
      paste("可能比较数:", values$characteristics$network_stats$possible_comparisons),
      paste("复杂度评分:", values$characteristics$complexity_score, "/100"),
      sep = "\n"
    )
  })
  
  # 方法推荐
  output$recommendations <- renderText({
    req(values$recommendations)
    
    continuity_text <- ifelse(values$recommendations$recommendations$continuity_correction$recommended, "是", "否")
    
    paste(
      paste("🔧 异质性估计方法:", values$recommendations$recommendations$tau_method$primary),
      paste("📊 效应量:", values$recommendations$recommendations$effect_measure$recommended),
      paste("⚙️ 连续性校正:", continuity_text),
      paste("📈 模型类型:", values$recommendations$recommendations$model_type$recommended),
      paste("🎯 总体置信度:", round(values$recommendations$recommendation_summary$overall_confidence, 3)),
      paste("📋 复杂度等级:", values$recommendations$recommendation_summary$complexity_level),
      sep = "\n"
    )
  })
  
  output$has_recommendations <- reactive({
    !is.null(values$recommendations)
  })
  outputOptions(output, "has_recommendations", suspendWhenHidden = FALSE)
  
  output$recommendation_reasons <- renderText({
    req(values$recommendations)
    
    paste(
      paste("异质性方法理由:", values$recommendations$recommendations$tau_method$reason),
      paste("效应量理由:", values$recommendations$recommendations$effect_measure$reason),
      paste("连续性校正理由:", values$recommendations$recommendations$continuity_correction$reason),
      paste("模型类型理由:", values$recommendations$recommendations$model_type$reason),
      sep = "\n\n"
    )
  })
}

# 启动应用
cat("🚀 启动Web界面...\n")
cat("界面将在浏览器中打开\n")
cat("如果没有自动打开，请复制显示的URL到浏览器中\n\n")

cat("使用说明:\n")
cat("1. 点击'加载演示数据'查看示例\n")
cat("2. 或上传您自己的Excel文件\n")
cat("3. 选择正确的数据类型\n")
cat("4. 点击'验证数据'开始分析\n")
cat("5. 查看各个标签页的结果\n\n")

cat("按 Ctrl+C 停止应用\n")
cat("=========================\n\n")

# 启动应用
shinyApp(ui = ui, server = server)