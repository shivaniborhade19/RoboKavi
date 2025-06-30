import os
import subprocess
from glob import glob
import sys
print("🐍 Python running:", sys.executable)

# ✅ Paths
AXICLI_DIR = (
 r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)\AxiDraw_API_396")
AXICLI_SCRIPT = os.path.join(AXICLI_DIR, "axicli.py")
SVG_OUTPUT_DIR = (
 r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)\AxiDraw_API_396")


def get_latest_vector_svg():
    svg_files = glob(os.path.join(SVG_OUTPUT_DIR, "*_vector.svg"))
    if not svg_files:
        raise FileNotFoundError("""❌ No vector SVG files found in the
                                directory.""")
    latest_file = max(svg_files, key=os.path.getmtime)
    print(f"🆕 Latest vector SVG found: {os.path.basename(latest_file)}")
    return os.path.basename(latest_file)


def run_plotter(svg_vector_filename=None):
    print("🚀 Entered run_plotter() function")

    if svg_vector_filename is None:
        svg_vector_filename = get_latest_vector_svg()

    full_svg_path = os.path.join(SVG_OUTPUT_DIR, svg_vector_filename)
    if not os.path.exists(full_svg_path):
        raise FileNotFoundError(f"""{svg_vector_filename} not found in
                                {SVG_OUTPUT_DIR}""")

    print(f"🐍 Python: {sys.executable}")
    print(f"🧭 Running in folder: {AXICLI_DIR}")
    print(f"📄 SVG file to plot: {svg_vector_filename}")

    try:
        print(f"""🧪 Running axicli with: {sys.executable} axicli.py
              {svg_vector_filename}""")
        result = subprocess.run(
            [sys.executable, "axicli.py", svg_vector_filename],
            cwd=AXICLI_DIR,   # ✅ set working dir to where axicli.py is
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ Plotting complete.")
        print("📤 STDOUT:", result.stdout)
        print("⚠ STDERR:", result.stderr)
        return result.stdout, result.stderr

    except subprocess.CalledProcessError as e:
        print("❌ Subprocess error:")
        print("📤 STDOUT:", repr(e.stdout))
        print("⚠ STDERR:", repr(e.stderr))
        return "", f"❌ Subprocess error: {repr(e.stderr)}"

    except Exception as e:
        print("🔥 Unexpected error:", str(e))
        return "", f"🔥 Unexpected error: {e}"
