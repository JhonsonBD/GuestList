from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import re

app = Flask(__name__)

@app.route('/check-mobile', methods=['POST'])
def format_phone_number(number: str) -> str:
    number = re.sub(r"[ \-\(\)]", "", number)

    if number.startswith("+"):
        return number
    else:
        if number.startswith("0"):
            return "+972" + number[1:]
        else:
            return "+972" + number

def check_mobile():
    try:
        data = request.get_json(force=True)
        phone_number = format_phone_number(data.get('phone_number'))

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
