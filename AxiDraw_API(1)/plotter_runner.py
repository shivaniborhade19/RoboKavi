# plotter_runner.py

import os
import subprocess
import sys

# ✅ AxiDraw paths
AXICLI_DIR = (
 r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)\AxiDraw_API_396")
AXICLI_SCRIPT = os.path.join(AXICLI_DIR, "axicli.py")
SVG_OUTPUT_DIR = r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)"


# ✅ FUNCTION DEFINITION
def run_plotter(svg_vector_filename):
    """
    Runs the AxiDraw plotter using axicli.py and the provided SVG file.
    """
    full_svg_path = os.path.join(SVG_OUTPUT_DIR, svg_vector_filename)

    if not os.path.exists(full_svg_path):
        raise FileNotFoundError(f"""{svg_vector_filename} not found in
                                {SVG_OUTPUT_DIR}""")

    cmd = [sys.executable, AXICLI_SCRIPT, svg_vector_filename]

    print(f"🔧 Running AxiDraw command: {' '.join(cmd)}")
    print(f"📂 Working directory: {SVG_OUTPUT_DIR}")

    result = subprocess.run(
        cmd,
        cwd=SVG_OUTPUT_DIR,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout, result.stderr


# ✅ MANUAL TESTING BLOCK
if __name__ == "__main__":
    try:
        # 🔁 Replace with your actual generated vector filename
        test_filename = "shiva_history_vector.svg"
        stdout, stderr = run_plotter(test_filename)

        print("✅ AxiDraw executed successfully.")
        print("📤 STDOUT:\n", stdout)
        if stderr:
            print("⚠️ STDERR:\n", stderr)

    except Exception as e:
        print("❌ Error during plotter run:", e)
