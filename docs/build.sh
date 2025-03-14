export PYTHONPATH="../camunda-rpa:$PYTHONPATH"


# Define the location of the libdoc.py script

# Define the output directory
OUTPUT_DIR="./src/pages"

# Create the output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

export PYTHONPATH=".:$PYTHONPATH"

# Function to generate documentation for a library
generate_doc() {
  local package_name=$1
  local output_file="$OUTPUT_DIR/$2"
  libdoc $package_name $output_file

  # Fix the Package name in the generated documentation
  sed -i "s/RPA\.$(basename $output_file .html)/Camunda.$(basename $output_file .html)/g" $output_file
}

# Generate documentation for each library
generate_doc "Camunda.Archive" "Archive.html"
generate_doc "Camunda.Browser.Selenium" "Browser.Selenium.html"
generate_doc "Camunda.Calendar" "Calendar.html"
generate_doc "Camunda.Desktop" "Desktop.html"
generate_doc "Camunda.Desktop.OperatingSystem" "Desktop.OperatingSystem.html"
generate_doc "Camunda.Excel.Application" "Excel.Application.html"
generate_doc "Camunda.Excel.Files" "Excel.Files.html"
generate_doc "Camunda.FileSystem" "FileSystem.html"
generate_doc "Camunda.FTP" "FTP.html"
generate_doc "Camunda.HTTP" "HTTP.html"
generate_doc "Camunda.Images" "Images.html"
generate_doc "Camunda.JavaAccessBridge" "JavaAccessBridge.html"
generate_doc "Camunda.html" "JSON.html"
generate_doc "Camunda.MFA" "MFA.html"
generate_doc "Camunda.MSGraph" "MSGraph.html"
generate_doc "Camunda.Outlook.Application" "Outlook.Application.html"
generate_doc "Camunda.PDF" "PDF.html"
generate_doc "Camunda.SAP" "SAP.html"
generate_doc "Camunda.Tables" "Tables.html"
generate_doc "Camunda.Tasks" "Tasks.html"
generate_doc "Camunda.Windows" "Windows.html"
generate_doc "Camunda.Word.Application" "Word.Application.html"

export PYTHONPATH="../camunda-utils:$PYTHONPATH"
generate_doc "Camunda" "Camunda.html"
