from flask import Flask, request, render_template
from openai import OpenAI
import base64
from PIL import Image
import pytesseract
import io
import os

app = Flask(__name__)
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', 'sk-your-default-key')
client = OpenAI(api_key=app.config['OPENAI_API_KEY'])

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            image = Image.open(file)
            base64_image = encode_image(image)
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": "Answer the question based on the image provided below:"},
                    {"role": "user", "content": [
                        {"type": "text", "text": "List out the details of the bill."},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]}
                ],
                temperature=0.0,
            )
            result = response.choices[0].message.content
            return render_template('result.html', result=result)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
