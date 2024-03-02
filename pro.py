import pypdfium2 as pdfium
from io import BytesIO
from PIL import Image
from pytesseract import image_to_string
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import asyncio
import asyncio
import aiofiles
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


def convert_to_csv_data(extracted_data):
    # Split the extracted data into lines
    lines = extracted_data.split('\n')

    # Create a list to hold rows of CSV data
    csv_data = []

    # Process each line of extracted data
    for line in lines:
        # Split each line into columns using a delimiter (if applicable)
        columns = line.split(':')  # Adjust delimiter based on the data structure
        csv_data.append(columns)

    return csv_data

# Convert PDF file into images via pdfium
async def convert_pdf_to_images(file_path, scale=300/72):
    pdf_file = pdfium.PdfDocument(file_path)
    page_indices = [i for i in range(len(pdf_file))]
    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )
    final_images = []
    for i, image in zip(page_indices, renderer):
        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        final_images.append(dict({i: image_byte_array}))
    return final_images

# Extract text from images via pytesseract
async def extract_text_from_img(list_dict_final_images):
    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []
    for index, image_bytes in enumerate(image_list):
        image = Image.open(BytesIO(image_bytes))
        raw_text = str(image_to_string(image))
        image_content.append(raw_text)
    return "\n".join(image_content)



async def handle_upload(file, filename, filepath):
    if filename.endswith('.pdf'):
        # Extract data from the uploaded PDF
        images = await convert_pdf_to_images(filepath)
        extracted_data = await extract_text_from_img(images)
    elif filename.endswith('.png') or filename.endswith('.jpeg') or filename.endswith('.jpg'):
        # Extract data from the uploaded image
        extracted_data = await extract_text_from_img(filepath)

    # Try to delete the file with a delay and retry mechanism
    for _ in range(5):  # Try up to 5 times
        try:
            await asyncio.sleep(1)  # Introduce a delay
            async with aiofiles.open(filepath, 'rb'):
                os.remove(filepath)
                break  # If successful, exit the loop
        except PermissionError:
            pass  # Retry if PermissionError occurs

    return extracted_data

@app.route('/upload', methods=['POST'])
async def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        extracted_data = await handle_upload(file, filename, filepath)
        csv_data=convert_to_csv_data(extracted_data)

        csv_filename = filename.split('.')[0] + '_key_value.csv'
        csv_filepath = os.path.join('csv_files', csv_filename)

        with open(csv_filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_data)

        return jsonify({'success': f'Key-value pairs saved to {csv_filename}'})

    return jsonify({'error': 'Invalid file format'})

if __name__ == '__main__':
    asyncio.run(app.run(debug=True))
