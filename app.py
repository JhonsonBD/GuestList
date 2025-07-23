from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import re
import pandas as pd
import io
import csv
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def format_phone_number(number: str) -> str:
    if pd.isna(number) or number == '' or str(number).lower() == 'nan':
        return ''
    
    # Convert to string and apply your formatting logic
    number = str(number).strip()
    
    # Handle the case where leading zero was lost - add it back for Israeli numbers
    if len(number) == 9 and number.isdigit() and number.startswith('5'):
        number = '0' + number
    
    number = re.sub(r"[ \-\(\)]", "", number)
    
    if number.startswith("+"):
        return number
    else:
        if number.startswith("0"):
            return "+972" + number[1:]
        else:
            return "+972" + number

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>XLSX to CSV Converter</title>
    </head>
    <body>
        <h2>Upload XLSX File to Convert to CSV</h2>
        <form action="/convert" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx,.xls" required>
            <br><br>
            <input type="submit" value="Convert to CSV">
        </form>
    </body>
    </html>
    '''

@app.route('/convert', methods=['POST'])
def convert_xlsx_to_csv():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if sheet['GL1'].value != 'guestlistformat':
            return jsonify({'error': 'Please use the correct Excel format'}), 400
        
        # Read the Excel file directly from memory
        # Use dtype=str for phone columns to preserve leading zeros
        df = pd.read_excel(file, dtype={'טלפון האורח': str})
        
        # Check if phone column exists and format phone numbers
        phone_column = 'טלפון האורח'
        if phone_column in df.columns:
            # Apply phone formatting to create new column
            df['טלפון פורמט'] = df[phone_column].apply(format_phone_number)
        
        # Convert DataFrame to CSV string
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        # Parse CSV content into list of dictionaries for JSON response
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        csv_data = list(csv_reader)
        
        # Return JSON response with CSV data
        return jsonify({
            'success': True,
            'filename': secure_filename(file.filename),
            'rows': len(csv_data),
            'columns': list(csv_data[0].keys()) if csv_data else [],
            'data': csv_data,
            'csv_string': csv_content,
            'phone_formatted': phone_column in df.columns
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/check-mobile', methods=['POST'])
def check_mobile():
    try:
        data = request.get_json(force=True)
        raw_number = data.get('phone_number')
        if not raw_number:
            return jsonify({'error': 'Phone number parameter is required'}), 400
        
        phone_number = format_phone_number(raw_number)
        parsed = phonenumbers.parse(phone_number)
        is_mobile = carrier._is_mobile(number_type(parsed))
        
        return jsonify({
            'input': raw_number,
            'number': phone_number,
            'is_mobile': is_mobile
        })
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
