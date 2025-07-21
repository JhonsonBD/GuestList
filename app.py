from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers.phonenumberutil import number_type, PhoneNumberType

app = Flask(__name__)

@app.route('/is_mobile', methods=['GET'])
def is_mobile():
    number = request.args.get("number")
    if not number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    try:
        parsed = phonenumbers.parse(number)
        type_of_number = number_type(parsed)
        is_mobile = type_of_number in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE)

        return jsonify({
            "number": number,
            "is_mobile": is_mobile,
            "type": PhoneNumberType._VALUES_TO_NAMES.get(type_of_number)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
