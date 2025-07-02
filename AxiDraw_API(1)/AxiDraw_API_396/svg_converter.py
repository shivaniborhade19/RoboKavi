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
    # --- ADJUSTED STARTING COORDINATES ---
    initial_x = 350      # Horizontal center-ish
    initial_y = 500      # Start near bottom of canvas
    font_size = 20       # Smaller font
    line_spacing = 40    # Moderate spacing upwards
    svg_width = 800
    svg_height = 600

    # SVG Content with the requested nested <tspan> structure and sodipodi
    svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   width="{svg_width}"
   height="{svg_height}"
   viewBox="0 0 {svg_width} {svg_height}"
   version="1.1"
   id="svg1">
  <defs id="defs1" />
  <sodipodi:namedview
     id="namedview1"
     pagecolor="#ffffff"
     bordercolor="#000000"
     borderopacity="0.25"
     inkscape:showpageshadow="2"
     inkscape:pageopacity="0.0"
     inkscape:pagecheckerboard="0"
     inkscape:deskcolor="#d1d1d1" />
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(0,0)"> <text
       xml:space="preserve"
       text-anchor="middle"
       style="font-size:{font_size}px;line-height:1.25;font-family:Kalam;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none"
       x="{initial_x}"
       y="{initial_y}"
       id="text1">
      <tspan sodipodi:role="line" id="tspan_outer" x="{initial_x}"
      y="{initial_y}">
'''

    # Generate inner tspans
    lines = poem_text.splitlines()
    num_lines = len(lines)
    for i, line in enumerate(lines):
        # Reverse direction: start lower and move up
        y_current = initial_y - (num_lines - 1 - i) * line_spacing
        svg_content += (f"""<tspan sodipodi:role="line" x="{initial_x}"
                        y="{y_current}" id="tspan_{i+1}">{line}</tspan>\n""")

    svg_content += '''      </tspan>
    </text>
  </g>
</svg>'''

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("📄 SVG file saved:", svg_path)

    # Inkscape vectorization
    try:
        result = subprocess.run([
            "C:/Program Files/Inkscape/bin/inkscape.com",
            svg_path,
            '--actions=select-all;object-to-path;export-do;quit',
            f"--export-filename={svg_vector_path}"
        ], check=True, timeout=15, capture_output=True, text=True)

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
