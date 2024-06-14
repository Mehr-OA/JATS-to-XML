from flask import Flask, request, jsonify
from FileService import process_file, pdf_to_txt, pdf_to_xml

app = Flask(__name__)

@app.route('/create_xml', methods=['GET'])
def create_xml():
    fileName = request.args.get('fileName')

    if not fileName:
        return jsonify({"error": "Invalid or missing fileName"}), 400
    print(fileName)
    try:
        #xml_str = process_file(fileName)
        return pdf_to_xml(fileName)
        #return xml_str, 200, {'Content-Type': 'application/xml'}
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def welcome():
    return "This API converts PDF articles to XML"

if __name__ == '__main__':
    app.run(debug=True)