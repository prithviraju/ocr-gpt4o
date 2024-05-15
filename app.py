import os
from flask import Flask, request, jsonify
from openai import OpenAI
import base64
from PIL import Image
import pytesseract
import io
from helpers.file_manipulation import extract_images_base64_from_file, del_file_from_disk, write_file_to_disk

app = Flask(__name__)
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', 'sk-your-default-key')
client = OpenAI(api_key=app.config['OPENAI_API_KEY'])

# Ensure the static directory exists
STATIC_DIRECTORY = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(STATIC_DIRECTORY):
    os.makedirs(STATIC_DIRECTORY)

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.route('/ocr', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        messages = [{"role": "system", "content": "List out the details of a documents provided as images below:"}]

        try:
            image = Image.open(file)
            base64_image = encode_image(image)
            messages.append(
                    {"role": "user", "content": [
                        {"type": "text", "text": "Here is an image from the document:"},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]}
                )
        except IOError:
            # file is not image, only process pdf files
            if file.filename.endswith(".pdf"):
                write_file_to_disk(file)
                images = extract_images_base64_from_file(file.filename)
                del_file_from_disk(file.filename)
                for image_base64 in images:
                    messages.append(
                        {"role": "user", "content": [
                            {"type": "text", "text": "Here is an image from the document:"},
                            {"type": "image_url", "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"}
                            }
                        ]}
                    )
            else:
                return jsonify({"error": "Invalid file, must be pdf or images"}), 400

        response = client.chat.completions.create(
                model='gpt-4o',
                messages=messages,
                temperature=0.0,
            )
        result = response.choices[0].message.content
        return jsonify({"result": result})

    return jsonify({"error": "Invalid file"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

