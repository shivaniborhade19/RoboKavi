# app.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from poem_generator import generate_poem
from svg_converter import save_poem_to_svg
from plotter_runner import run_plotter
import os

app = Flask(__name__, template_folder='templates')
CORS(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate-poem', methods=['POST'])
def generate_poem_route():
    data = request.get_json()
    name = data.get("name", "").strip()
    subject = data.get("subject", "").strip()
    language = data.get("language", "mr")

    if not name or not subject:
        return jsonify({"error": "Please enter both name and subject."}), 400

    try:
        # Step 1: Generate poem
        poem = generate_poem(name, subject, language)
        if not poem:
            return jsonify({"error": "Failed to generate poem."}), 500

        # Step 2: Convert to SVG
        filename_base = f"{name}_{subject}"
        svg_vector_path = save_poem_to_svg(poem, filename_base)
        if not svg_vector_path:
            return jsonify({"error": "SVG vectorization failed."}), 500

        # Step 3: Run plotter
        stdout, stderr = run_plotter(svg_vector_path)

        return jsonify({
            "poem": poem,
            "svg_filename": os.path.basename(svg_vector_path),
            "message": "✅ Poem generated, SVG created and plotting started!",
            "plotter_output_stdout": stdout,
            "plotter_output_stderr": stderr
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
