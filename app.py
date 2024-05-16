import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI, APIConnectionError
import base64
from PIL import Image
import io
from helpers.file_manipulation import clear_tmp_directory, extract_images_base64_from_file, write_file_to_disk
import time

from aws_helper import analyze_image

app = Flask(__name__)
api_key = os.environ.get('OPENAI_API_KEY', 'sk-your-default-key')
print(f"OpenAI API Key: {api_key}")  # Debug print
client = OpenAI(api_key=api_key)

# Ensure the static directory exists
STATIC_DIRECTORY = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(STATIC_DIRECTORY):
    os.makedirs(STATIC_DIRECTORY)

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('upload.html', error="No file part")

    file = request.files['file']
    if file.filename == '':
        return render_template('upload.html', error="No selected file")

    if file:
        messages = [{"role": "system", "content": "List out the details of a document provided as images below. Do no miss out on Receipt ID or Number, Merchant Name, Date/Time in ISO format, Total Amount, and Currency. If the currency is not explicitly mentioned, infer it based on the merchant's location or other contextual clues. Additionally, indicate whether the receipt includes any alcohol items:"}]

        try:
            if file.filename.endswith(".pdf"):
                write_file_to_disk(file)
                images = extract_images_base64_from_file(file.filename)
                clear_tmp_directory()
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
        except IOError as e:
            print(f"error: {e}")
            return render_template('upload.html', error="Invalid file, must be pdf or images")

        # Implementing a retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model='gpt-4o',
                    messages=messages,
                    temperature=0.0,
                )
                result = response.choices[0].message.content
                return render_template('result.html', result=result)
            except APIConnectionError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return render_template('upload.html', error="Connection error. Please try again later.")

    return render_template('upload.html', error="Invalid file")

@app.route('/ocr', methods=['POST'])
def ocr_api():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        messages = [{"role": "system", "content": "List out the details of a document provided as images below. Do no miss out on Receipt ID or Number, Merchant Name, Date/Time in ISO format, Total Amount, and Currency. If the currency is not explicitly mentioned, infer it based on the merchant's location or other contextual clues. Additionally, indicate whether the receipt includes any alcohol items:"}]

        try:
            if file.filename.endswith(".pdf"):
                write_file_to_disk(file)
                images = extract_images_base64_from_file(file.filename)
                clear_tmp_directory()
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
        except IOError as e:
            print(f"error: {e}")
            return jsonify({"error": "Invalid file, must be pdf or images"}), 400

        # Implementing a retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model='gpt-4o',
                    messages=messages,
                    temperature=0.0,
                )
                result = response.choices[0].message.content
                return jsonify({"result": result})
            except APIConnectionError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return jsonify({"error": "Connection error. Please try again later."}), 500

    return jsonify({"error": "Invalid file"}), 400

@app.route('/aws-textract', methods=['POST'])
def textract_api():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        if file.filename.endswith(".png") or file.filename.endswith(".jpeg") or file.filename.endswith(".jpg"):
            image = Image.open(file)
            base64_image = encode_image(image)
            result = analyze_image(base64_image)
            return jsonify({"result": result})
        else:
            return jsonify({"error": "Invalid file, must be an image"}), 400
    except Exception as e:
        print(f"error: {e}")
        return jsonify({"error": "Something went wrong. Please try again later."}), 500

if __name__ == '__main__':
    clear_tmp_directory()
    app.run(debug=True, host='0.0.0.0')

