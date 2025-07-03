import os
import subprocess

# Path to Inkscape
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.com"

# Directory where the SVG will be saved
SAVE_DIR = os.getcwd()  # Current folder

# Output filenames
FILENAME_BASE = "test_poem"
SVG_PATH = os.path.join(SAVE_DIR, f"{FILENAME_BASE}.svg")
VECTOR_SVG_PATH = os.path.join(SAVE_DIR, f"{FILENAME_BASE}_vector.svg")

# Simple 3-line Marathi text
poem_text = """कावेरी वाहते, सागर सारखी,
निसर्गाची ती राणी, सुंदर स्वप्नं.
हरीत तिचे जीवन"""


# SVG creation with Hershey text style
def create_svg_with_text(text):
    font_size = 20
    line_spacing = 40
    initial_x = 100
    initial_y = 100
    svg_width = 800
    svg_height = 600

    lines = text.strip().splitlines()
    svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="{svg_width}" height="{svg_height}"
     viewBox="0 0 {svg_width} {svg_height}"
     version="1.1">
  <g inkscape:label="Layer 1" inkscape:groupmode="layer" id="layer1">
'''

    for i, line in enumerate(lines):
        y = initial_y + i * line_spacing
        svg_content += f'''
    <text
       x="{initial_x}"
       y="{y}"
       font-size="{font_size}"
       style="font-family:Hershey Simplex;"
       id="line{i+1}">{line}</text>'''

    svg_content += '''
  </g>
</svg>'''

    with open(SVG_PATH, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    print("✅ SVG with text saved:", SVG_PATH)


def convert_to_vector_with_inkscape():
    try:
        cmd = [
            INKSCAPE_PATH,
            SVG_PATH,
            '--actions=select-all;object-to-path;export-do;quit',
            f'--export-filename={VECTOR_SVG_PATH}'
        ]
        result = subprocess.run(cmd, check=True, timeout=15,
                                capture_output=True, text=True)
        print("✅ Hershey Vector SVG saved:", VECTOR_SVG_PATH)
        print("📤 Inkscape STDOUT:", result.stdout.strip())
        print("⚠ Inkscape STDERR:", result.stderr.strip())
    except subprocess.TimeoutExpired:
        print("⏰ Inkscape command timed out!")
    except subprocess.CalledProcessError as e:
        print("❌ Vectorization failed:", e)
        print("📤 STDOUT:", e.stdout)
        print("⚠ STDERR:", e.stderr)


if __name__ == "__main__":
    create_svg_with_text(poem_text)
    convert_to_vector_with_inkscape()
    print(f"🖨️ Now run: axicli {FILENAME_BASE}_vector.svg to test plotting")
