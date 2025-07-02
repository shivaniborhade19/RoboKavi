from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from poem_generator import generate_poem
from svg_converter import save_poem_as_svg
from plotter_runner import run_plotter
import threading
import time
import traceback
import os
import subprocess
import sys
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

    print("🧠 Generating poem...")
    poem = generate_poem(name, subject, language)
    print("✅ Poem generated:\n", poem)

    filename_base1 = f"{name}_{subject}"
    print(f"💾 Saving SVG to {filename_base1}...")
    vector_path = save_poem_as_svg(poem, filename_base=filename_base1)
    time.sleep(2)
    print("✅ Vector SVG saved at:", vector_path)

    def background_plot():
        try:
            print("🧵 Starting plotter in background thread...")

            # ✅ Full absolute folder path
            folder_path = os.path.dirname(os.path.abspath(__file__))
            template_svg = os.path.join(folder_path, "template3.svg")

            if os.path.exists(template_svg):
                print("🖨️ Plotting template3.svg...")

                result = subprocess.run([
                    sys.executable, "axicli.py", "template3.svg"
                ], cwd=folder_path)

                print("✅ Template plotted. Result code:", result.returncode)
            else:
                print("⚠️ template3.svg not found at:", template_svg)

            # 2️⃣ Then plot the newly generated vector SVG
            from plotter_runner import run_plotter
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
        "message": "✅ Poem generated. Plotting started with template first.",
    }), 200


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
