from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers.phonenumberutil import number_type, PhoneNumberType, NumberParseException

app = Flask(__name__)

@app.route('/is_mobile', methods=['GET'])
def is_mobile():
    number = request.args.get("number")
    if not number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    try:
        # ניתוח המספר לפי קידומת
        if number.startswith('+'):
            parsed = phonenumbers.parse(number)
        else:
            parsed = phonenumbers.parse(number, "IL")

        # סוג המספר
        num_type = number_type(parsed)
        is_mobile = num_type in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE)

        return jsonify({
            "input_number": number,
            "formatted_number": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "is_mobile": is_mobile,
            "type": num_type.name  # 👈 זה השינוי החשוב
        })

    except NumberParseException as e:
        return jsonify({"error": f"Invalid number: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
