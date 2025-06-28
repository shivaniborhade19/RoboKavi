from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import subprocess
import sys
from googletrans import Translator
from poem_to_svg import save_poem_as_svg

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__, template_folder='templates')
CORS(app)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
translator = Translator()

# === Plotter Paths ===
# Define the base directory where SVGs should be stored and where axicli will
SVG_OUTPUT_BASE_DIR = (
    r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)")

# Define the subdirectory containing axicli.py relative to SVG_OUTPUT_BASE_DIR.
AXICLI_SUBDIRECTORY = "AxiDraw_API_396"

# Construct the full path to the 'axicli.py' script.
AXICLI_SCRIPT_FULL_PATH = os.path.join(SVG_OUTPUT_BASE_DIR,
                                       AXICLI_SUBDIRECTORY, "axicli.py")

# --- Diagnostic Prints for Path Verification on app startup ---
print("\n--- AxiDraw Path Configuration (Initial Load) ---")
print(f"SVG Output Base Directory: {SVG_OUTPUT_BASE_DIR}")
print(f"AxiCLI Script Full Path: {AXICLI_SCRIPT_FULL_PATH}")
print(f"Python Executable Used: {sys.executable}")
print(f"Does AxiCLI Script Exist? {os.path.exists(AXICLI_SCRIPT_FULL_PATH)}")
print("--------------------------------------------------\n")


def to_marathi(text):
    """Translates English text to Marathi."""
    return translator.translate(text, src='en', dest='mr').text


@app.route('/')
def index():
    """Renders the main index page."""
    return render_template("index.html")


@app.route('/generate-poem', methods=['POST'])
def generate_poem():
    """
    Generates a Marathi/English poem, converts it to SVG, and then
    automatically sends it to AxiDraw for plotting.
    """
    data = request.get_json()
    name_en = data.get("name", "").strip()
    subject_en = data.get("subject", "").strip()
    language = data.get("language", "mr")  # default is marathi

    if not name_en or not subject_en:
        return jsonify({"error": "Please provide both name and subject."}), 400

    if language == "mr":
        name_final = to_marathi(name_en)
        subject_final = to_marathi(subject_en)
        prompt = f"""{name_final} आणि {subject_final} या विषयावर आधारित एक
        छोटी,
३-४ ओळींची, यमकबद्ध मराठी कविता लिहा.
फक्त कविता लिहा, दुसरे काहीही नाही."""
    else:  # English
        name_final = name_en
        subject_final = subject_en
        prompt = f"""Write a short English poem (3–4 lines) with rhyme,
based on the name '{name_final}' and the theme '{subject_final}'.
Only the poem, no explanations."""

    try:
        response = model.generate_content(prompt)
        poem = (response.text.strip() if hasattr(response, 'text')
                and response.text else "Could not generate poem.")

        filename_base1 = f"{name_en}_{subject_en}"
        print(f"""\nDebug: Attempting to save SVG for '{filename_base1}' to
              '{SVG_OUTPUT_BASE_DIR}'""")
        svg_vector_path = save_poem_as_svg(
            poem, filename_base=filename_base1, save_dir=SVG_OUTPUT_BASE_DIR)

        if not svg_vector_path:
            print(f"""Debug: SVG conversion failed or returned no vector path
                  for {filename_base1}.""")
            return jsonify({"error": "SVG vector conversion failed."}), 500
        else:
            print(f"Debug: SVG vector path generated: {svg_vector_path}")
            if not os.path.exists(svg_vector_path):
                print(f"""Debug: WARNING! Generated SVG file does NOT exist at
                      {svg_vector_path} immediately after save.""")
                return jsonify({"""error": "Generated SVG file not found after
                                conversion."""}), 500

        # --- AUTOMATIC PLOTTING LOGIC IS NOW HERE ---
        try:
            # Extract just the filename of the generated SVG.
            # axicli.py, when run with cwd, expects just the filename.
            svg_filename_only = os.path.basename(svg_vector_path)

            # Command to run axicli.py using the Python interpreter
            # 'sys.executable' ensures we use the same Python that runs this
            # We then provide the full path to axicli.py and the SVG filename.
            cmd_list = [sys.executable, AXICLI_SCRIPT_FULL_PATH,
                        svg_filename_only]

            print("""\n🔧 Debug: Entering AxiDraw plotting attempt from
                  /generate-poem endpoint...""")
            print(f"  Command to be executed: {cmd_list}")
            print(f"""  Current Working Directory (cwd) for subprocess:
                  {SVG_OUTPUT_BASE_DIR}""")
            print(f"""  SVG filename to be passed to axicli:
                  {svg_filename_only}""")
            print(f"""  Does SVG file exist at cwd/filename?
                  {os.path.exists(os.path.join(SVG_OUTPUT_BASE_DIR,
                  svg_filename_only))}""")
            print("-" * 40)

            # Run the subprocess.
            # 'cwd=SVG_OUTPUT_BASE_DIR' is crucial: it tells axicli.py to look
            # in this directory, even though we're providing its full path.
            result = subprocess.run(cmd_list, check=True, capture_output=True,
                                    text=True, cwd=SVG_OUTPUT_BASE_DIR)

            print("\n✅ AxiDraw Plotting Command Executed Successfully.")
            print("--- AxiDraw STDOUT ---")
            print(result.stdout)
            print("----------------------")
            if result.stderr:
                print("--- AxiDraw STDERR (Warnings/Errors) ---")
                print(result.stderr)
                print("----------------------------------------")
            else:
                print("✅ No errors reported by AxiDraw (STDERR empty).")

            # Return success response for both poem generation and plotting
            return jsonify({
                "name": name_final,
                "subject": subject_final,
                "poem": poem,
                "message": """✅ Poem generated and plotting initiated
                successfully!""",
                "svg_filename": svg_filename_only,
                "plotter_output_stdout": result.stdout,
                "plotter_output_stderr": result.stderr
            })

        except subprocess.CalledProcessError as e:
            error_message = (
                f"""❌ AxiDraw plotting command failed with exit code
                {e.returncode}.\n"""
                f"Command: {' '.join(e.cmd)}\n"
                f"AxiDraw STDOUT: {e.stdout}\n"
                f"AxiDraw STDERR: {e.stderr}"
            )
            print(error_message)
            return jsonify({"error": error_message, "plotter_stdout": e.stdout,
                            "plotter_stderr": e.stderr}), 500
        except FileNotFoundError as e:
            error_message = (
                f"""❌ Error: Python executable ('{sys.executable}') or
                AxiCLI script """
                f"('{AXICLI_SCRIPT_FULL_PATH}') not found. "
                f"""Check permissions, Python installation, and the specified
                path to axicli.py.\n"""
                f"Error detail: {e}"
            )
            print(error_message)
            return jsonify({"error": error_message}), 500
        except Exception as e:
            error_message = f"""❌ An unexpected error occurred during plotting:
            {str(e)}"""
            print(error_message)
            return jsonify({"error": error_message}), 500

    except Exception as e:
        # This catches errors from Gemini API or the initial SVG conversion
        print(f"""Debug: Top-level error in generate_poem
              (Gemini/SVG creation): {e}""")
        return jsonify({
            "error": f"Gemini or SVG generation error: {str(e)}"
        }), 500

# We no longer need a separate /start-plot endpoint if everything is automated.
# @app.route('/start-plot', methods=['POST'])
# def start_plot():
#    ... (this function is removed for full automation)


if __name__ == '__main__':
    app.run(debug=True)
