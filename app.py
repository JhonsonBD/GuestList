from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

app = Flask(__name__)

@app.route('/check-mobile', methods=['GET'])
def check_mobile():
    try:
        # Get phone number from query parameter
        number = request.args.get('number')
        
        if not number:
            return jsonify({
                'error': 'Phone number parameter is required',
                'usage': 'GET /check-mobile?number=0547773320'
            }), 400
        
        original_number = number
        
        # If number doesn't start with + or country code, assume Israeli number
        if not number.startswith('+') and not number.startswith('00'):
            # Remove leading 0 if present and add Israeli prefix
            if number.startswith('0'):
                number = number[1:]
            number = '+972' + number
        
        # Parse and check if the number is mobile
        parsed_number = phonenumbers.parse(number)
        is_mobile = carrier._is_mobile(number_type(parsed_number))
        
        return jsonify({
            'original_number': original_number,
            'formatted_number': number,
            'is_mobile': is_mobile,
            'success': True
        })
        
    except phonenumbers.phonenumberutil.NumberParseException as e:
        return jsonify({
            'error': f'Invalid phone number: {str(e)}',
            'original_number': original_number if 'original_number' in locals() else None,
            'success': False
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
