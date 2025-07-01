from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from poem_generator import generate_poem
from svg_converter import save_poem_as_svg
from plotter_runner import run_plotter
import threading
import traceback

app = Flask(__name__, template_folder='templates')
CORS(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate-poem', methods=['POST'])
def generate():
    print("📩 /generate-poem endpoint called")
    data = request.get_json()
    print("📥 Data received from frontend:", data)

    name = data.get("name", "").strip()
    subject = data.get("subject", "").strip()
    language = data.get("language", "mr")

    if not name or not subject:
        print("⚠️ Name or subject missing!")
        return jsonify({"error": "Name and subject required."}), 400

    try:
        print("🧠 Generating poem...")
        poem = generate_poem(name, subject, language)
        print("✅ Poem generated:\n", poem)

        filename_base1 = f"{name}_{subject}"
        print(f"💾 Saving SVG to {filename_base1}...")
        vector_path = save_poem_as_svg(poem, filename_base=filename_base1)
        print("✅ Vector SVG saved at:", vector_path)

        # Try to start plotter in background
        def background_plot():
            try:
                print("🧵 Starting plotter in background thread...")
                stdout, stderr = run_plotter()
                print("🖨️ Plotter finished:\nSTDOUT:\n", stdout)
                if stderr:
                    print("⚠️ STDERR:", stderr)
            except Exception as e:
                print("❌ Background plot error:", e)
                traceback.print_exc()

        threading.Thread(target=background_plot).start()
        print("✅ Background thread launched")

        return jsonify({
            "poem": poem,
            "message": "✅ Poem generated Plotter command started.",
        }), 200

    except Exception as e:
        print("❌ ERROR during poem generation or plotting:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/test-plot')
def test_plot():
    print("🧪 Running test_plot route...")
    try:
        stdout, stderr = run_plotter()
        print("✅ Plotting finished:\n", stdout)
        return jsonify({
            "stdout": stdout,
            "stderr": stderr
        })
    except Exception as e:
        print("❌ Plotting error in test_plot:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
