from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

app = Flask(__name__)

@app.route('/check-mobile', methods=['POST'])
def check_mobile():
    try:
        data = request.get_json(force=True)
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'error': 'Phone number parameter is required'}), 400
        
        check = carrier._is_mobile(number_type(phonenumbers.parse(phone_number)))
        
        return jsonify({
            'number': phone_number,
            'is_mobile': check
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
