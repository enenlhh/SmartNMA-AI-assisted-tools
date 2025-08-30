# A script to check and install required packages for the SartNMA Tool

# List of required packages
required_packages <- c(
  "shiny", 
  "readxl", 
  "dplyr", 
  "showtext", 
  "writexl", 
  "tools", 
  "meta", 
  "netmeta", 
  "shinyFiles"
)

cat("Checking and installing required packages...\n\n")

# Loop through the list of packages
for (pkg in required_packages) {
  # Check if the package is already installed
  if (!requireNamespace(pkg, quietly = TRUE)) {
    cat(paste("Package '", pkg, "' not found. Installing...\n", sep = ""))
    tryCatch({
      install.packages(pkg, dependencies = TRUE)
      cat(paste("Successfully installed '", pkg, "'\n\n", sep = ""))
    }, error = function(e) {
      cat(paste("Failed to install '", pkg, "'. Please install it manually.\nError: ", e$message, "\n\n", sep = ""))
    })
  } else {
    cat(paste("Package '", pkg, "' is already installed.\n", sep = ""))
  }
}

cat("\nAll required packages are checked. You can now run the tool.\n")
