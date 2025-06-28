# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from poem_generator import generate_poem
from svg_converter import save_poem_as_svg
from plotter_runner import run_plotter
import os

app = Flask(__name__, template_folder='templates')
CORS(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate-poem', methods=['POST'])
def generate():
    data = request.get_json()
    name = data.get("name", "").strip()
    subject = data.get("subject", "").strip()
    language = data.get("language", "mr")

    if not name or not subject:
        return jsonify({"error": "Name and subject required."}), 400

    try:
        poem = generate_poem(name, subject, language)
        filename_base = f"{name}_{subject}"
        vector_path = save_poem_as_svg(poem, filename_base=filename_base,
                                       save_dir="AxiDraw_API(1)")

        svg_vector_filename = os.path.basename(vector_path)
        stdout, stderr = run_plotter(svg_vector_filename)

        return jsonify({
            "poem": poem,
            "message": "✅ Poem generated, SVG created, and plotting started!",
            "plotter_output_stdout": stdout,
            "plotter_output_stderr": stderr
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
