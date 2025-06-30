from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from poem_generator import generate_poem
from svg_converter import save_poem_as_svg
from plotter_runner import run_plotter

app = Flask(__name__, template_folder='templates')
CORS(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate-poem', methods=['POST'])
def generate():
    print("📩 /generate-poem endpoint called")
    data = request.get_json()
    print("Data received from frontend:", data)

    name = data.get("name", "").strip()
    subject = data.get("subject", "").strip()
    language = data.get("language", "mr")

    if not name or not subject:
        return jsonify({"error": "Name and subject required."}), 400

    try:
        print("🧠 Generating poem...")
        poem = generate_poem(name, subject, language)
        print("✅ Poem generated:\n", poem)

        filename_base = f"{name}_{subject}"
        print(f"💾 Saving SVG to {filename_base}...")
        vector_path = save_poem_as_svg(poem, filename_base=filename_base)
        print("✅ Vector SVG saved at:", vector_path)
        import time
        time.sleep(1)

        print("🔄 Calling run_plotter() now...")
        stdout, stderr = run_plotter()  # <- Auto picks latest vector.svg
        print("✅ Plotting complete.")
        print("🧩 STDOUT:", stdout)
        print("🧩 STDERR:", stderr)
        return jsonify({
            "poem": poem,
            "message": "✅ Poem generated, SVG created, and plotting started!",
            "plotter_output_stdout": stdout,
            "plotter_output_stderr": stderr
        }), 200

    except Exception as e:
        print("❌ ERROR during generation:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/test-plot')
def test_plot():
    from plotter_runner import run_plotter
    print("🧪 Running test_plot route...")
    stdout, stderr = run_plotter()
    return jsonify({
        "stdout": stdout,
        "stderr": stderr
    })


if __name__ == '__main__':
    app.run(debug=True)
