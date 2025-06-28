import serial
import time


class PlotterControl:
    # ... (all your existing class definition for PlotterControl) ...
    def __init__(self, port, baud_rate=9600, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None

        # --- CALIBRATION VALUES (YOU MUST ADJUST THESE) ---
        # These define how many stepper motor "steps" correspond to 1 unit of
        # physical movement (e.g., 1 mm or 1 inch) on your plotter.
        # and standard pulleys/belts. You MUST calibrate this for your setup.
        self.steps_per_unit_x = 80.0
        self.steps_per_unit_y = 80.0

        self.current_x = 0.0
        self.current_y = 0.0

        self.min_x = 0.0
        self.min_y = 0.0
        self.max_x = 220.0
        self.max_y = 160.0

        # --- SERVO POSITIONS FOR PEN UP/DOWN (YOU MUST CALIBRATE THESE) ---
        self.pen_up_position = 0     # Common 'pen up' servo position
        self.pen_down_position = 1   # Common 'pen down' servo position

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
            response = (
                self.serial_connection.readline().decode('ascii').strip())
            return response
        except Exception as e:
            print(f"Error sending command: {e}")
            return "ERROR"

    def xm_move(self, duration, axis_steps_a, axis_steps_b, clear=None):
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

        command = f"XM,{duration},{axis_steps_a},{axis_steps_b}"
        if clear is not None:
            if not (0 <= clear <= 3):
                print(f"Error: Clear value {clear} out of valid range (0-3).")
                return "ERROR"
            command += f",{clear}"
        command += "\r"
        return self.send_command(command)

    def move_to_xy_relative(self, delta_x_units, delta_y_units,
                            speed_units_per_sec):
        if speed_units_per_sec <= 0:
            print("Error: Speed must be greater than 0.")
            return "ERROR"

        delta_x_steps = delta_x_units * self.steps_per_unit_x
        delta_y_steps = delta_y_units * self.steps_per_unit_y

        if abs(delta_x_steps) < 0.5 and abs(delta_y_steps) < 0.5:
            print(f"""Warning: No significant movement requested
                  (dx={delta_x_units:.2f}, dy={delta_y_units:.2f}).
                  Performing delay.""")
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
        motor1_steps_calc = delta_x_steps + delta_y_steps
        motor2_steps_calc = delta_x_steps - delta_y_steps

        if not (MIN_INT_32 <= motor1_steps_calc <= MAX_INT_32 and
                \
                MIN_INT_32 <= motor2_steps_calc <= MAX_INT_32):
            print(f"""Error: Calculated internal motor steps
                  ({motor1_steps_calc:.0f}, {motor2_steps_calc:.0f}) """
                  f"""exceed 32-bit integer limits. Reduce movement distance
                  or steps/unit.""")
            return "ERROR"
        print(f"""Relative move: dx={delta_x_units:.2f}, dy={delta_y_units:.2f}
              units """
              f"@ {speed_units_per_sec:.2f} units/s. -> "
              f"""Steps: ({delta_x_steps:.0f}, {delta_y_steps:.0f}), Duration:
              {duration_ms}ms.""")
        response = self.xm_move(duration_ms, delta_x_steps, delta_y_steps)
        time.sleep(duration_ms / 1000.0 + 0.05)
        return response

    def absolute_move_xy(self, target_x_units, target_y_units,
                         speed_units_per_sec):
        if not (self.min_x <= target_x_units <= self.max_x and
                \
                self.min_y <= target_y_units <= self.max_y):
            print(f"""Warning: Target position ({target_x_units:.2f},
                  {target_y_units:.2f}) """
                  f"""is outside plotter bounds ({self.min_x}-{self.max_x},
                  {self.min_y}-{self.max_y}). """
                  f"Attempting move, but be cautious!")

        delta_x = target_x_units - self.current_x
        delta_y = target_y_units - self.current_y
        if abs(delta_x) < 0.01 and abs(delta_y) < 0.01:
            print(f"Already at target position ({target_x_units:.2f},'"
                  f"{target_y_units:.2f}). No move needed.")
            return "OK"

        print(f"""Absolute move: from ({self.current_x:.2f},
              {self.current_y:.2f}) to ({target_x_units:.2f},
              {target_y_units:.2f})""")
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
            print(f"Warning: Pen Down command response "
                  f"was not 'OK': {response}")
        time.sleep(0.5)

    def draw_l_shape(self, start_x, start_y, arm_length_vertical,
                     arm_length_horizontal, drawing_speed):
        print(
            f"\n--- Drawing 'L'shape starting at ({start_x:.2f},{start_y:.2f})"
            )
        self.pen_up()
        self.absolute_move_xy(start_x, start_y, drawing_speed * 2)

        self.pen_down()

        print("Drawing vertical arm...")
        corner_x = start_x
        corner_y = start_y + arm_length_vertical
        self.absolute_move_xy(corner_x, corner_y, drawing_speed)

        print("Drawing horizontal arm...")
        end_x = corner_x + arm_length_horizontal
        end_y = corner_y
        self.absolute_move_xy(end_x, end_y, drawing_speed)

        self.pen_up()
        print("Finished drawing 'L' shape.")


# --- Main execution ---
if __name__ == "__main__":
    plotter_port = 'COM4'
    plotter_baud_rate = 9600

    plotter = PlotterControl(plotter_port, plotter_baud_rate)
    # For 1/16 microstepping, 80 steps/mm is a common value.
    plotter.steps_per_unit_x = 80.0
    plotter.steps_per_unit_y = 80.0
    plotter.max_x = 220.0
    plotter.max_y = 160.0
    plotter.min_x = 0.0
    plotter.min_y = 0.0

    # These pen positions are critical and must be calibrated for your plotter.
    plotter.pen_up_position = 750    # Set to your calibrated 'pen up' value
    plotter.pen_down_position = 250  # Set to your calibrated 'pen down' value

    if plotter.connect():
        print("\n--- Plotter Drawing Program Started ---")

        # EM,1,1 sets 1/16 microstepping (default) and enables both motors.
        print("""Setting motor enable and microstep mode
              (EM,1,1 for 1/16 microstepping)...""")
        em_response = plotter.send_command("EM,1,1\r")
        if em_response != "OK":
            print(f"Warning: EM command response was not 'OK': {em_response}")
        time.sleep(0.5)

        # Using the updated home() which sends HM,5000\r
        plotter.home()

        # Define the L-shape parameters (in your chosen units, e.g., mm)
        center_x = plotter.max_x / 2
        center_y = plotter.max_y / 2
        vertical_arm_len = 40.0
        horizontal_arm_len = 30.0
        start_x_pos = center_x - (horizontal_arm_len / 2)
        start_y_pos = center_y - (vertical_arm_len / 2)
        drawing_speed = 60.0

        # Draw the L shape
        plotter.draw_l_shape(start_x_pos, start_y_pos, vertical_arm_len,
                             horizontal_arm_len, drawing_speed)

        # Optional: Move the plotter back to a safe home position after drawing
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
