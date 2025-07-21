from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import re

app = Flask(__name__)

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
