from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import re

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload .xlsx or .xls files'}), 400
        
        # Read the Excel file directly from memory
        df = pd.read_excel(file)
        
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
            'csv_string': csv_content  # Raw CSV string if needed
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
####################################################
def format_phone_number(number: str) -> str:
    number = re.sub(r"[ \-\(\)]", "", number)

    if number.startswith("+"):
        return number
    else:
        if number.startswith("0"):
            return "+972" + number[1:]
        else:
            return "+972" + number

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

if __name__ == '__main__':
    app.run(debug=True)
