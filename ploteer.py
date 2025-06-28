import serial
import time
import subprocess
import os
import xml.etree.ElementTree as ET
from svgpathtools import svg2paths


# --- (Your PlotterControl class definition goes here, including plot_svg) ---
# Make sure your PlotterControl class from previous messages is here,
# specifically the connect, disconnect, send_command, absolute_move_xy,
# pen_up, pen_down, and plot_svg methods.

class PlotterControl:
    # ... (all your existing class definition for PlotterControl,
    #      including connect, disconnect, send_command, xm_move,
    #      move_to_xy_relative, absolute_move_xy, set_current_position,
    #      home, pen_up, pen_down, draw_l_shape) ...

    def __init__(self, port, baud_rate=9600, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None

        self.steps_per_unit_x = 80.0
        self.steps_per_unit_y = 80.0

        self.current_x = 0.0
        self.current_y = 0.0

        self.min_x = 0.0
        self.min_y = 0.0
        self.max_x = 220.0
        self.max_y = 160.0

        # --- SERVO POSITIONS FOR PEN UP/DOWN (CALIBRATED FROM YOUR VIDEO) ---
        self.pen_up_position = 750  # From AxiDraw Control Panel video
        self.pen_down_position = 250

    def connect(self):
        try:
            self.serial_connection = serial.Serial(
                self.port,
                self.baud_rate,
                timeout=self.timeout
            )
            print(f"""Connected plotter on {self.port} at {self.baud_rate}
                      baud.""")
            time.sleep(2)
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            return True
        except serial.SerialException as e:
            print(f"Error connecting to plotter: {e}")
            return False

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from plotter.")

    def send_command(self, command):
        if not self.serial_connection or not self.serial_connection.is_open:
            print("Error: Not connected to plotter. Call connect() first.")
            return "ERROR"

        try:
            full_command = command.encode('ascii')
            self.serial_connection.write(full_command)
            # Add debug prints for commands sent and received
            # print(f"Sent: {command.strip()}")
            response = (
                self.serial_connection.readline().decode('ascii').strip())
            # print(f"Recv: {response}")
            return response
        except Exception as e:
            print(f"Error sending command: {e}")
            return "ERROR"

    def xm_move(self, duration, axis_steps_a, axis_steps_b, clear=None):
        # Your existing xm_move implementation
        if not (1 <= duration <= 2147483647):
            print(f"""Error: Duration {duration} is out of valid range
                    (1 to 2147483647).""")
            return "ERROR"
        if duration == 0 and (axis_steps_a != 0 or axis_steps_b != 0):
            print("""Warning: Duration 0 is invalid for non-zero steps.
                    Adjusting to 1ms.""")
            duration = 1

        axis_steps_a = int(round(axis_steps_a))
        axis_steps_b = int(round(axis_steps_b))

        # IMPORTANT: If your plotter uses SM, change this to SM.
        # Based on AxiDraw, XM is usually for clear buffer, SM
        # Let's assume SM for standard move as it's more common.
        # If your firmware requires XM with no clear parameter, then keep it.
        # I will revert to SM as that's typical for general AxiDraw movement.
        command = f"SM,{duration},{axis_steps_a},{axis_steps_b}"
        # if clear is not None:
        #    if not (0 <= clear <= 3):
        #        print(f"Error: Clear value {clear} out of valid range (0-3).")
        #        return "ERROR"
        #    command += f",{clear}"
        command += "\r"
        return self.send_command(command)

    def move_to_xy_relative(self, delta_x_units, delta_y_units,
                            speed_units_per_sec):
        # Your existing move_to_xy_relative implementation
        if speed_units_per_sec <= 0:
            print("Error: Speed must be greater than 0.")
            return "ERROR"

        delta_x_steps = delta_x_units * self.steps_per_unit_x
        delta_y_steps = delta_y_units * self.steps_per_unit_y

        if abs(delta_x_steps) < 0.5 and abs(delta_y_steps) < 0.5:
            # print(f"""Warning: No significant movement requested
            #         (dx={delta_x_units:.2f}, dy={delta_y_units:.2f}).
            #         Performing delay.""")
            duration_ms = max(1, int(1000 / speed_units_per_sec))
            if duration_ms > 100000:
                duration_ms = 100000
            self.xm_move(duration_ms, 0, 0)
            return "OK"

        time_x_s = (abs(delta_x_units) /
                    speed_units_per_sec if delta_x_units != 0 else 0)
        time_y_s = (
            abs(delta_y_units) / speed_units_per_sec if delta_y_units != 0
            else 0)
        total_time_s = max(time_x_s, time_y_s)
        duration_ms = max(1, int(total_time_s * 1000))

        MAX_INT_32 = 2147483647
        MIN_INT_32 = -2147483648
        # This is for CoreXY / H-bot kinematics, typical for AxiDraw
        motor1_steps_calc = delta_x_steps + delta_y_steps
        motor2_steps_calc = delta_x_steps - delta_y_steps

        if not (MIN_INT_32 <= motor1_steps_calc <= MAX_INT_32 and
                MIN_INT_32 <= motor2_steps_calc <= MAX_INT_32):
            print(f"""Error: Calculated internal motor steps
                    ({motor1_steps_calc:.0f}, {motor2_steps_calc:.0f})
                    exceed 32-bit integer limits. Reduce movement distance
                    or steps/unit.""")
            return "ERROR"
        # print(f"""Relative move: dx={delta_x_units:.2f},
        #       units """
        #       f"@ {speed_units_per_sec:.2f} units/s. -> "
        #       f"""Steps: ({delta_x_steps:.0f}, {delta_y_steps:.0f}),
        #       {duration_ms}ms.""")
        response = self.xm_move(duration_ms, motor1_steps_calc,
                                motor2_steps_calc)
        time.sleep(duration_ms / 1000.0 + 0.05)
        return response

    def absolute_move_xy(self, target_x_units, target_y_units,
                         speed_units_per_sec):
        # Your existing absolute_move_xy implementation
        if not (self.min_x <= target_x_units <= self.max_x and
                self.min_y <= target_y_units <= self.max_y):
            print(f"""Warning: Target position ({target_x_units:.2f},
                    {target_y_units:.2f})
                    is outside plotter bounds ({self.min_x}-{self.max_x},
                    {self.min_y}-{self.max_y}).
                    Attempting move, but be cautious!""")

        delta_x = target_x_units - self.current_x
        delta_y = target_y_units - self.current_y
        if abs(delta_x) < 0.01 and abs(delta_y) < 0.01:
            # print(f"Already at target position ({target_x_units:.2f},'"
            #         f"{target_y_units:.2f}). No move needed.")
            return "OK"

        # print(f"""Absolute move: from ({self.current_x:.2f},
        #       {self.current_y:.2f}) to ({target_x_units:.2f},
        #       {target_y_units:.2f})""")
        response = self.move_to_xy_relative(delta_x, delta_y,
                                            speed_units_per_sec)
        if response != "ERROR":
            self.current_x = target_x_units
            self.current_y = target_y_units
        return response

    def set_current_position(self, x_units, y_units):
        self.current_x = float(x_units)
        self.current_y = float(y_units)
        print(f"Plotter internal position set to ({self.current_x:.2f}, "
              f"{self.current_y:.2f}) units.")

    def home(self):
        print("Homing V3 EasyDraw plotter...")
        response = self.send_command("HM,5000\r")
        if response != "OK":
            print(f"Warning: Homing command response was not 'OK': {response}")

        self.set_current_position(0, 0)
        time.sleep(2)

    def pen_up(self):
        print("Lifting pen...")
        response = self.send_command(f"SP,{self.pen_up_position}\r")
        if response != "OK":
            print(f"Warning: Pen Up command response was not 'OK': {response}")
        time.sleep(0.5)

    def pen_down(self):
        print("Lowering pen...")
        response = self.send_command(f"SP,{self.pen_down_position}\r")
        if response != "OK":
            print("""Warning: Pen Down command response
                    was not 'OK': {response}""")
        time.sleep(0.5)

    def plot_svg(self, svg_file_path, plot_speed_mm_s, scale_factor=1.0,
                 offset_x_mm=0.0, offset_y_mm=0.0, svg_viewbox_height=None):
        """
        Reads an SVG file, extracts paths, and plots them.

        Args:
            svg_file_path (str): Path to the SVG file.
            plot_speed_mm_s (float): Drawing speed in mm/s.
            scale_factor (float): Factor to scale the SVG drawing.
            offset_x_mm (float): X offset for the drawing in mm.
            offset_y_mm (float): Y offset for the drawing in mm.
            svg_viewbox_height (float, optional): The height of the SVG's
                                                  viewBox in mm. Required for
                                                  correct Y inversion/scaling.
                                                  If None, attempts to infer from SVG attributes.
        """
        if not os.path.exists(svg_file_path):
            print(f"Error: SVG file not found at {svg_file_path}")
            return "ERROR"

        try:
            # Parse SVG and get root element to extract viewBox if not provided
            tree = ET.parse(svg_file_path)
            root = tree.getroot()
            
            # If svg_viewbox_height is not explicitly provided, try to get it from the SVG's viewBox
            if svg_viewbox_height is None:
                viewbox_str = root.get('viewBox')
                if viewbox_str:
                    parts = [float(p) for p in viewbox_str.split()]
                    if len(parts) == 4:
                        svg_viewbox_height = parts[3] # The fourth value in viewBox is height
                        print(f"Inferred svg_viewbox_height from SVG viewBox: {svg_viewbox_height:.2f}mm")
                    else:
                        print("Warning: Could not parse viewBox attribute for height. Using default Y inversion logic.")
                else:
                    print("Warning: svg_viewbox_height not provided and viewBox attribute not found. Using default Y inversion logic.")

            paths, attributes = svg2paths(svg_file_path)
            print(f"Loaded {len(paths)} paths from {svg_file_path}")

            if len(paths) == 0:
                print("Warning: No <path> elements found in SVG content.")
                return "OK"

            all_points = []
            for path in paths:
                for segment in path:
                    all_points.append(segment.start)
                    all_points.append(segment.end)
            min_svg_x = min(p.real for p in all_points)
            max_svg_x = max(p.real for p in all_points)
            min_svg_y = min(p.imag for p in all_points)
            max_svg_y = max(p.imag for p in all_points)

            svg_drawing_width = max_svg_x - min_svg_x
            svg_drawing_height = max_svg_y - min_svg_y

            print(f"SVG content bounds (min_x, min_y) to (max_x, max_y): "
                  f"({min_svg_x:.2f}, {min_svg_y:.2f}) to ({max_svg_x:.2f}, {max_svg_y:.2f})")
            print(f"SVG content dimensions: {svg_drawing_width:.2f} x {svg_drawing_height:.2f}")
            
            # --- START PLOTTING ---
            self.pen_up() # Ensure pen is up before first move
            
            for i, path in enumerate(paths):
                # print(f"Processing path {i+1}/{len(paths)}")

                # Get the first point of the path
                start_point = path.point(0)

                # Apply scale factor, y-axis inversion, and offset for START point
                transformed_start_x = (start_point.real * scale_factor) + offset_x_mm
                
                # Corrected Y-axis inversion logic
                if svg_viewbox_height is not None:
                    transformed_start_y = ((svg_viewbox_height - start_point.imag) * scale_factor) + offset_y_mm
                else:
                    # Fallback if viewBox height isn't available or provided
                    # This assumes SVG Y=0 is max plotter Y, and SVG max_Y is plotter Y=0.
                    # It's less reliable for consistent positioning across different SVGs.
                    transformed_start_y = (start_point.imag * scale_factor) + offset_y_mm # Original (non-inverted) logic or simple flip
                    print("DEBUG: Using fallback Y-transformation (no viewBox height provided/inferred).")


                self.absolute_move_xy(transformed_start_x, transformed_start_y,
                                      plot_speed_mm_s * 2) # Use a faster speed for pen-up moves

                self.pen_down()

                # Iterate through segments and draw
                for segment in path:
                    # Apply scale factor, y-axis inversion, and offset for END
                    transformed_end_x = (segment.end.real * scale_factor) + offset_x_mm
                    
                    # Corrected Y-axis inversion logic
                    if svg_viewbox_height is not None:
                        transformed_end_y = ((svg_viewbox_height - segment.end.imag) * scale_factor) + offset_y_mm 
                    else:
                        # Fallback if viewBox height isn't available or
                        transformed_end_y = (segment.end.imag * scale_factor) + offset_y_mm    
                    self.absolute_move_xy(transformed_end_x, transformed_end_y,
                                          plot_speed_mm_s)
                self.pen_up()
            print("Finished plotting all paths.")
            return "OK"

        except Exception as e:
            print(f"Error plotting SVG: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
            return "ERROR"

def create_svg_with_text(poem_lines, output_svg_path,
                         x_start=10, y_start=20, line_height=10, font_size=8,
                         svg_width=200, svg_height=150):
    """
    Creates an SVG file with multiple text elements.

    Args:
        poem_lines (list): A list of strings, each representing a line of the
        poem.
        output_svg_path (str): The path where the SVG file will be saved.
        x_start (int): X-coordinate for the start of the text.
        y_start (int): Y-coordinate for the first line of text.
        line_height (int): Vertical spacing between lines.
        font_size (int): Font size for the text.
        svg_width (int): Width of the SVG canvas.
        svg_height (int): Height of the SVG canvas.
    """
    root = ET.Element("svg",
                      xmlns="http://www.w3.org/2000/svg",
                      attrib={
                          "width": f"{svg_width}mm",
                          "height": f"{svg_height}mm",
                          "viewBox": f"0 0 {svg_width} {svg_height}",
                          "version": "1.1"
                      })
    # Define a default style for the text to make it visible in Inkscape
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
    """
    Uses Inkscape's command-line interface to convert text elements in an SVG
    file to paths.

    Args:
        input_svg_path (str): Path to the input SVG file (with text).
        output_svg_path (str): Path where the converted SVG will be saved.
        inkscape_path (str, optional): Full path to the Inkscape executable.
                                       If None, assumes 'inkscape' is in PATH.
    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    if inkscape_path is None:
        # Assumes inkscape is in your system's PATH
        command_prefix = ["inkscape"]
    else:
        command_prefix = [inkscape_path]

    # Inkscape command to open, select all, convert to path, and save
    # --export-filename is for output
    # --export-area-drawing ensures only the drawing area is exported, not the
    # --actions can be a powerful way to chain commands
    # 'select-all; object-to-path; export-filename:output.svg; export-do;'
    # Note: 'object-to-path' verb might be flaky in older Inkscape CLI versions
    # For newer Inkscape (1.0+), --actions is preferred.
    # The 'select-all' verb followed by 'object-to-path' usually works.
    command = command_prefix + [
        "--actions",
        f"""file-open:{input_svg_path}; select-all; object-to-path;
        export-filename:{output_svg_path}; export-do; file-close:"""
        # "select-all; object-to-path; export-filename:output.svg; export-do"
    ]
    print(f"Running Inkscape command: {' '.join(command)}")

    try:
        # Use subprocess.run for cleaner handling of process execution
        result = subprocess.run(command, capture_output=True, text=True,
                                check=True)
        print("Inkscape stdout:\n", result.stdout)
        if result.stderr:
            print("Inkscape stderr:\n", result.stderr)
        if os.path.exists(output_svg_path) and os.path.getsize(
                                               output_svg_path) > 0:
            print("""Successfully converted text to paths. Output saved to
                  {output_svg_path}""")
            return True
        else:
            print("""Error: Converted SVG file {output_svg_path} was
                  not created or is empty.""")
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


# --- Main execution ---
if __name__ == "__main__":
    plotter_port = 'COM4'  # Adjust to your plotter's COM port
    plotter_baud_rate = 9600

    plotter = PlotterControl(plotter_port, plotter_baud_rate)
    plotter.steps_per_unit_x = 80.0
    plotter.steps_per_unit_y = 80.0
    plotter.max_x = 220.0
    plotter.max_y = 160.0
    plotter.min_x = 0.0
    plotter.min_y = 0.0

    # Ensure pen positions are calibrated for your plotter
    plotter.pen_up_position = 750
    plotter.pen_down_position = 250

    if plotter.connect():
        print("\n--- Plotter Drawing Program Started ---")

        # Set motor enable and microstep mode (if your plotter supports EM,1,1)
        print("""Setting motor enable and microstep mode
              (EM,1,1 for 1/16 microstepping)...""")
        em_response = plotter.send_command("EM,1,1\r")
        if em_response != "OK":
            print(f"Warning: EM command response was not 'OK': {em_response}")
        time.sleep(0.5)

        plotter.home()

        # Define your poem
        poem = ["TEST"]
        # --- Automated SVG Generation and Conversion ---
        input_svg_filename = "input.svg"
        output_svg_filename = "poem_paths.svg"

        # Example for Windows:
        inkscape_executable_path = (
            r"C:\Program Files\Inkscape\bin\inkscape.exe")
        # Example for Linux/macOS (if not in PATH, use 'which inkscape'
        # inkscape_executable_path = "/usr/bin/inkscape"
        # Check if the Inkscape executable exists at the specified path
        if inkscape_executable_path and not os.path.exists(
                                            inkscape_executable_path):
            print(f"""WARNING: Inkscape executable not found at
                  '{inkscape_executable_path}'. """
                  """Please check the path or ensure Inkscape is
                  in your system's PATH. """
                  "Skipping automated text-to-path conversion.")
            inkscape_conversion_successful = False
        else:
            # 1. Create SVG with raw text
            create_svg_with_text(poem, input_svg_filename,
                                 x_start=10, y_start=20, line_height=10,
                                 font_size=10,
                                 svg_width=plotter.max_x,
                                 svg_height=plotter.max_y)

            # 2. Convert text to paths using Inkscape CLI
            print("""\n--- Converting text to paths using Inkscape (headless)
                  ---""")
            inkscape_conversion_successful = (
                convert_svg_text_to_paths_with_inkscape)(
                input_svg_filename, output_svg_filename,
                inkscape_path=inkscape_executable_path
            )

        # 3. Plot the converted SVG
        if inkscape_conversion_successful:
            print("\n--- Plotting poem from converted SVG ---")
            drawing_speed = 80.0
            # Adjust offset and scale as needed for your paper and plotter area
            # The svg_viewbox_height should match the height used in
            plotter.plot_svg(output_svg_filename, drawing_speed,
                             scale_factor=1.0, offset_x_mm=10.0,
                             offset_y_mm=10.0,
                             svg_viewbox_height=plotter.max_y)
        else:
            print("""\n--- Skipping plotting of poem due to Inkscape
                  conversion failure ---""")
            # You could add fallback drawing here, e.g., draw a simple shape
            # plotter.draw_l_shape(50, 50, 40, 30, 60)

        print("\nMoving plotter back to origin (0,0) with pen up...")
        plotter.pen_up()
        plotter.absolute_move_xy(0, 0, 100)
        print("Disabling motors (EM,0,0)...")
        plotter.send_command("EM,0,0\r")
        time.sleep(0.5)

        print("\n--- Plotter Drawing Program Finished ---")
        plotter.disconnect()
    else:
        print("Could not connect to plotter. Please check port and baud rate.")
