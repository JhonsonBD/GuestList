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
                'usage': 'GET /check-mobile?number=+972547773320'
            }), 400
        
        # Check if the number is mobile
        check = carrier._is_mobile(number_type(phonenumbers.parse(number)))
        
        return jsonify({
            'number': number,
            'is_mobile': check,
            'success': True
        })
        
    except phonenumbers.phonenumberutil.NumberParseException as e:
        return jsonify({
            'error': f'Invalid phone number: {str(e)}',
            'number': number if 'number' in locals() else None,
            'success': False
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
