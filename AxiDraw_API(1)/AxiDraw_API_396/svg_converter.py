# svg_converter.py

import os
import subprocess

SVG_OUTPUT_BASE_DIR = (
  r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)\AxiDraw_API_396")


def save_poem_as_svg(poem_text, filename_base, save_dir=None):
    if save_dir is None:
        save_dir = SVG_OUTPUT_BASE_DIR

    os.makedirs(save_dir, exist_ok=True)

    svg_path = os.path.join(save_dir, f"{filename_base}.svg")
    svg_vector_path = os.path.join(save_dir, f"{filename_base}_vector.svg")

    svg_content = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
  <defs>
    <style type="text/css">
      @font-face {{
        font-family: 'Kalam';
        src: url('AxiDraw_API(1)/Kalam-Regular.ttf');
      }}
    </style>
  </defs>
  <g>
    <text x="50" y="100" font-size="32" font-family="Kalam">
'''

    for i, line in enumerate(poem_text.splitlines()):
        y = 100 + i * 50
        svg_content += f'      <tspan x="50" y="{y}">{line}</tspan>\n'

    svg_content += '''    </text>
  </g>
</svg>'''

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    try:
        subprocess.run([
            "C:/Program Files/Inkscape/bin/inkscape.exe",
            svg_path,
            "--actions=select-all;object-to-path;export-do;quit",
            f"--export-filename={svg_vector_path}"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Vectorization failed:", e)
        return None
    print("✅ Vector SVG saved successfully:", svg_vector_path)
    return svg_vector_path
