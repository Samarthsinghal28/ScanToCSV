from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from pro import extract_text_from_pdf
from pro import extract_key_value_pairs_and_tabular_data
from pro import extract_text_from_image

import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.endswith('.pdf'):
            # Extract data from the uploaded PDF
            extracted_data = extract_text_from_pdf(filepath)

        elif filename.endswith('.png') or filename.endswith('.jpeg') or filename.endswith('.jpg'):
            # Extract data from the uploaded PDF
            extracted_data = extract_text_from_image(filepath)
   
        # Delete the uploaded file after extraction
        os.remove(filepath)

    # Extract key-value pairs and tabular data
        key_value_pairs, tabular_data = extract_key_value_pairs_and_tabular_data(extracted_data)

        csv_filename = filename.split('.')[0] + '_key_value_pairs.csv'
        csv_filepath = os.path.join('csv', csv_filename)


        # Write key-value pairs to a CSV file
        with open(csv_filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Key', 'Value'])
            for key, value in key_value_pairs.items():
                writer.writerow([key, value])
        
        tabular_csv_filename = filename.split('.')[0] + '_tabular.csv'
        tabular_csv_filepath = os.path.join('csv', tabular_csv_filename)

        with open(tabular_csv_filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in tabular_data:
                writer.writerow(row)
            

        return jsonify({'success': f'Key-value pairs saved to {csv_filename} \n '})

    return jsonify({'error': 'Invalid file format'})

if __name__ == '__main__':
    app.run(debug=True)
