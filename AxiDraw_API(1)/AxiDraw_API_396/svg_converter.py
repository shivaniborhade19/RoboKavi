import os
import subprocess

SVG_OUTPUT_BASE_DIR = (
    r"C:\Users\hp\Downloads\robokavi_gemini_web\AxiDraw_API(1)\AxiDraw_API_396"
)


def save_poem_as_svg(poem_text, filename_base, save_dir=None):
    if save_dir is None:
        save_dir = SVG_OUTPUT_BASE_DIR

    os.makedirs(save_dir, exist_ok=True)

    svg_path = os.path.join(save_dir, f"{filename_base}.svg")
    svg_vector_path = os.path.join(save_dir, f"{filename_base}_vector.svg")

    # --- Layout settings ---
    svg_width = 800
    svg_height = 600
    font_size = 20
    line_spacing = 40

    # Calculate vertical start point for centering poem block vertically
    lines = poem_text.strip().splitlines()
    num_lines = len(lines)
    total_text_height = (num_lines - 1) * line_spacing
    start_y = (svg_height // 2) - (total_text_height // 2)
    center_x = svg_width // 2  # Horizontal center

    # --- Generate SVG content ---
    svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{svg_width}"
    height="{svg_height}"
    viewBox="0 0 {svg_width} {svg_height}">
  <g>
'''

    for i, line in enumerate(lines):
        y = start_y + i * line_spacing
        svg_content += f'''    <text
        x="{center_x}"
        y="{y}"
        text-anchor="middle"
        font-family="Hershey Sans 1"
        font-size="{font_size}px"
        fill="#000000">{line}</text>\n'''

    svg_content += '''  </g>
</svg>'''

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("📄 SVG file saved:", svg_path)

    # --- Use Inkscape to convert text to path (Hershey) ---
    try:
        result = subprocess.run([
            "C:/Program Files/Inkscape/bin/inkscape.com",
            svg_path,
            '--actions=select-all;object-to-path;export-do;quit',
            f'--export-filename={svg_vector_path}'
        ], check=True, timeout=20, capture_output=True, text=True)

        print("✅ Vector SVG saved successfully:", svg_vector_path)
        print("📤 Inkscape STDOUT:", result.stdout)
        print("⚠ Inkscape STDERR:", result.stderr)

    except subprocess.TimeoutExpired:
        print("⏰ Inkscape command timed out!")
        return None

    except subprocess.CalledProcessError as e:
        print("❌ Vectorization failed:", e)
        print("📤 STDOUT:", e.stdout)
        print("⚠ STDERR:", e.stderr)
        return None

    return svg_vector_path
