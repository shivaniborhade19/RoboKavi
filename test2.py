import os
import subprocess
import xml.etree.ElementTree as ET
from axidraw import AxiDraw


# --- Your existing create_svg_with_text and
def create_svg_with_text(poem_lines, output_svg_path,
                         x_start=10, y_start=20, line_height=10, font_size=8,
                         svg_width=200, svg_height=150):
    root = ET.Element("svg",
                      xmlns="http://www.w3.org/2000/svg",
                      attrib={
                          "width": f"{svg_width}mm",
                          "height": f"{svg_height}mm",
                          "viewBox": f"0 0 {svg_width} {svg_height}",
                          "version": "1.1"
                      })
    defs = ET.SubElement(root, "defs")
    style = ET.SubElement(defs, "style")
    style.text = f"""text {{ font-family: sans-serif; font-size:
    {font_size}px; fill: black; }}"""

    g_element = ET.SubElement(root, "g")

    current_y = y_start
    for line in poem_lines:
        text_element = ET.SubElement(g_element, "text",
                                     x=str(x_start),
                                     y=str(current_y))
        text_element.text = line
        current_y += line_height

    tree = ET.ElementTree(root)
    tree.write(output_svg_path, encoding="utf-8", xml_declaration=True)
    print(f"Created SVG with text: {output_svg_path}")


def convert_svg_text_to_paths_with_inkscape(input_svg_path, output_svg_path,
                                            inkscape_path=None):
    if inkscape_path is None:
        command_prefix = ["inkscape"]
    else:
        command_prefix = [inkscape_path]

    # Note: Inkscape's --actions string is very sensitive to whitespace and
    # The 'file-close:' at the end is important to ensure Inkscape exits
    command = command_prefix + [
        "--actions",
        f"""file-open:{input_svg_path}; select-all; object-to-path;
        export-filename:{output_svg_path}; export-do; file-close:"""
    ]
    print(f"Running Inkscape command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=True)
        print("Inkscape stdout:\n", result.stdout)
        if result.stderr:
            print("Inkscape stderr:\n", result.stderr)
        if os.path.exists(output_svg_path) and (
              os.path.getsize(output_svg_path) > 0):
            print(f"""Successfully converted text to paths. Output saved to
                  {output_svg_path}""")
            return True
        else:
            print(f"""Error: Converted SVG file {output_svg_path} was not
                  created or is empty.""")
            return False
    except FileNotFoundError:
        print("""Error: Inkscape executable not found. Please ensure
              Inkscape is installed and in your system's PATH, or provide the
              full path to inkscape_path.""")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error running Inkscape command: {e}")
        print("Inkscape stdout (on error):\n", e.stdout)
        print("Inkscape stderr (on error):\n", e.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Inkscape conversion: {e}")
        return False


if __name__ == "__main__":
    # --- 1. Initialize AxiDraw and Connect ---
    # You can specify the port directly if it's not automatically found
    # For example, on Windows: ad = AxiDraw(port='COM3')
    # On Linux/macOS: ad = AxiDraw(port='/dev/ttyUSB0')
    ad = AxiDraw(port='COM4')
    print("Attempting to connect to AxiDraw...")
    if not ad.connect():
        print("""Failed to connect to AxiDraw. Make sure it's plugged in and
              recognized.""")
        exit()

    print("AxiDraw connected successfully!")

    # --- 2. Set ALL AxiDraw Options (Replicating GUI "Setup") ---
    # These are directly analogous to the settings in your Inkscape GUI
    # Adjust these values based on your preferences and AxiDraw model.

    # Plot Tab Settings (image_c45ac3.png)
    ad.options.pen_pos_up = 75     # Percentage (0-100) for pen up
    ad.options.pen_pos_down = 35   # Percentage (0-100) for pen down
    ad.options.speed_pendown = 50  # Drawing speed in mm/s
    ad.options.speed_penup = 100   # Pen-up movement speed in mm/s
    ad.options.accel = 75          # Acceleration percentage (0-100)
    ad.options.cornering = 0       # Percentage (0-100), 0 for sharp corners
    ad.options.const_speed_value = 0.5
    ad.options.overshoot = 0.5     # mm, for over-drag
    ad.options.auto_rotate = False
    ad.options.x_offset = 0.0      # Global X offset for the drawing (mm)
    ad.options.y_offset = 0.0      # Global Y offset for the drawing (mm)
    ad.options.units = 'mm'        # Units of the SVG (usually auto-detected)

    # Layers Tab Settings (image_c45b1b.png)
    ad.options.mode = 'plot'       # 'plot' (all paths) or 'layers'
    # If mode is 'layers', you could also specify ad.options.layer = 0

    # Drawing Tab Settings (image_c45b5c.png)
    ad.options.x_scale = 1.0       # X scale factor (1.0 = no scaling)
    ad.options.y_scale = 1.0       # Y scale factor
    ad.options.x_mirror = False    # Mirror drawing horizontally
    ad.options.y_mirror = False    # Mirror drawing vertically
    ad.options.rot = 0.0           # Rotation in degrees

    # Motors Tab Settings (image_c45e61.png - generally not set by user per
    # These are usually handled by the AxiDraw model setting or firmware
    # ad.options.drive_mode = 'normal' # Motor current: 'low', 'normal', 'high'

    # Timing Tab Settings (image_c45ebd.png)
    ad.options.auto_pause_start = False
    ad.options.auto_pause_end = False   # Pause at end of plot

    # Setup Tab Settings (image_c45f1f.png)
    ad.options.model = 3           # Specify your AxiDraw model (e.g., 3 for
    # Port and Baudrate are set during AxiDraw() instantiation

    print("AxiDraw parameters set from script.")

    # --- 3. Create SVG and Convert Text to Paths ---
    input_svg_path = 'static/direct_plot_text_input.svg'
    poem_lines = ["Hello AxiDraw!", "From Python Script", "Today: "
                  + time.strftime("%Y-%m-%d %H:%M:%S IST")]
    # Define SVG canvas size. The AxiDraw library will handle positioning/
    # based on the options set above and the 'plot_run' parameters.
    svg_canvas_width = 200
    svg_canvas_height = 150

    create_svg_with_text(poem_lines,
                         input_svg_path,
                         x_start=10,
                         y_start=20,
                         line_height=10,
                         font_size=8,
                         svg_width=svg_canvas_width,
                         svg_height=svg_canvas_height)

    output_paths_svg_path = 'static/direct_plot_text_paths.svg'
    inkscape_exe_path = None

    conversion_successful = convert_svg_text_to_paths_with_inkscape(
        input_svg_path, output_paths_svg_path, inkscape_path=inkscape_exe_path
    )

    if conversion_successful:
        # --- 4. Plot the Converted SVG (The "Click Apply" Equivalent) ---
        print(f"\nPlotting SVG: {output_paths_svg_path}")
        # Tell AxiDraw library which file to plot
        ad.options.filename = output_paths_svg_path

        # The 'plot_run()' method initiates the entire plotting process.
        # It takes optional arguments for plot origin, scale, rotation, etc.
        # If not provided, it uses the ad.options values.
        # Example for placing the drawing:
        # If your SVG is 200x150mm, and you want its top-left corner
        # to be at (10mm, 10mm) on the plotter bed (from bottom-left),
        # you'd use x_pos=10, y_pos=(plotter_height - 10 - svg_height).
        # However, it's often simpler to just use ad.options.x_offset/y_offset
        # for general placement after setting scale/rotation in options.
        # This single call replaces all the complex coordinate transformations
        # and movement commands you were trying to do manually in plot_svg.
        ad.plot_run()
        print("\nDirect plotting completed successfully!")
    else:
        print("SVG conversion failed, cannot proceed with direct plotting.")

    # --- 5. Disconnect ---
    ad.disconnect()
    print("AxiDraw disconnected.")
