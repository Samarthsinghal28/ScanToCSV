<<<<<<< HEAD
# PDF Data Extractor

This is a web application for extracting data from PDF files. It allows users to upload a PDF file, extracts data from it, and displays the extracted data on the webpage.

## Installation

1. Clone the repository: git clone <repository_url>

2. Install the required Python dependencies: pip install -r requirements.txt

3. Install `Tesseract` OCR and `poppler`:

- **Tesseract OCR**: Follow the installation instructions for your operating system from the official repository: https://github.com/tesseract-ocr/tesseract


4. Set environment variables:
   
   - **For Windows**:
     - Add the path to the `Tesseract` executable (`tesseract.exe`) to the `PATH` environment variable.
     -Add the TESSDATA_PREFIX user variable to  environment variables and set the value(path) to the tessdata folder of Tessaract-OCR.

   - **For Unix/Linux**:
     - Add the path to the `Tesseract` executable (`tesseract`) to the `PATH` environment variable.
    

5. Run the Flask application: python app.py

6. Open a web browser and go to `http://127.0.0.1:5000/` to access the application.

## Usage

- Upload a PDF file using the provided form.
- Click on the "Upload" button to extract data from the uploaded PDF file.
- The extracted data will be saved into a csv file in the csv folder.


