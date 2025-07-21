from flask import Flask, jsonify, request
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import re
from urllib.parse import unquote

app = Flask(__name__)

def format_phone_number(number: str) -> str:
    # Handle URL encoding - decode first
    number = unquote(number)
    
    # ניקוי רווחים, מקפים וסוגריים
    number = re.sub(r"[ \-\(\)]", "", number)

    if number.startswith("+"):
        # כבר קידומת בינלאומית, להשאיר כמו שהוא
        return number
    else:
        # מספר בלי קידומת
        # אם מתחיל ב-0, מסירים את ה-0 ומוסיפים +972
        if number.startswith("0"):
            return "+972" + number[1:]
        else:
            # במקרה ומספר בלי קידומת ובלי 0 בהתחלה, פשוט מוסיפים +972
            return "+972" + number

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
        
        # Format the phone number using the provided logic
        formatted_number = format_phone_number(number)
        
        # Parse and check if the number is mobile
        parsed_number = phonenumbers.parse(formatted_number)
        is_mobile = carrier._is_mobile(number_type(parsed_number))
        
        return jsonify({
            'original_number': original_number,
            'formatted_number': formatted_number,
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
