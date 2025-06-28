from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from googletrans import Translator

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__, template_folder='templates')  # Serve index.html
CORS(app)

# Gemini & Translation Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
translator = Translator()


def to_marathi(text):
    return translator.translate(text, src='en', dest='mr').text


# ✅ Serve index.html
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate-poem', methods=['POST'])
def generate_poem():
    data = request.get_json()
    name_en = data.get("name", "").strip()
    subject_en = data.get("subject", "").strip()

    if not name_en or not subject_en:
        return jsonify({"error": "Please provide both name and subject."}), 400

    name_mr = to_marathi(name_en)
    subject_mr = to_marathi(subject_en)

    prompt = f"""{name_mr} आणि {subject_mr} या विषयावर आधारित एक छोटी,
    ३-४ ओळींची, यमकबद्ध मराठी कविता लिहा.
फक्त कविता लिहा, दुसरे काहीही नाही."""

    try:
        response = model.generate_content(prompt)
        poem = (response.text.strip() if response and hasattr(response, "text")
                else "क्षमस्व, कविता निर्माण होऊ शकली नाही.")
        return jsonify({
            "name": name_mr,
            "subject": subject_mr,
            "poem": poem
        })

    except Exception as e:
        return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
