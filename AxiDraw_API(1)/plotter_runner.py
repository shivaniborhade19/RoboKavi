# plotter_runner.py

import os
import subprocess
import sys

SVG_OUTPUT_BASE_DIR = (
    r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)")
AXICLI_SUBDIRECTORY = "AxiDraw_API_396"
AXICLI_SCRIPT_FULL_PATH = os.path.join(SVG_OUTPUT_BASE_DIR,
                                       AXICLI_SUBDIRECTORY, "axicli.py")


def run_plotter(svg_vector_path):
    if not os.path.exists(svg_vector_path):
        raise FileNotFoundError("SVG file does not exist.")

    filename_only = os.path.basename(svg_vector_path)

    command = [sys.executable, AXICLI_SCRIPT_FULL_PATH, filename_only]
    result = subprocess.run(command, capture_output=True, text=True,
                            cwd=SVG_OUTPUT_BASE_DIR)

    return result.stdout, result.stderr
