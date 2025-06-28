# set_axidraw_heights.py

import os
import re
import inkex


class AxiDrawHeightSetter(inkex.EffectExtension):
    """
    An Inkscape extension to programmatically set AxiDraw pen up/down heights.
    """

    def effect(self):
        """
        Main function for the extension.
        Finds axidraw_conf.py and modifies the height settings.
        """
        # Get the path to the user's extensions directory from Inkscape
        extensions_path = self.app.user_extensions_path
        config_file_path = os.path.join(extensions_path, "axidraw_conf.py")

        if not os.path.exists(config_file_path):
            inkex.errormsg(
                """Error: 'axidraw_conf.py' not found in your
                           extensions folder.
                           Is AxiDraw installed correctly?"""
            )
            return

        try:
            # Read the original configuration file
            with open(config_file_path, "r") as f:
                content = f.read()

            # Define the new height values
            new_up_height = 75
            new_down_height = 35

            # Use regular expressions to safely replace the values.
            # This preserves comments, spacing, and other formatting.
            # Pattern for pen_height_up = VALUE
            up_pattern = re.compile(r"^(pen_height_up\s*=\s*)(\d+\.?\d*)",
                                    re.MULTILINE)
            content = up_pattern.sub(f"\\g<1>{new_up_height}", content)
            # Pattern for pen_height_down = VALUE
            down_pattern = re.compile(
                r"^(pen_height_down\s*=\s*)(\d+\.?\d*)", re.MULTILINE
            )
            content = down_pattern.sub(f"\\g<1>{new_down_height}", content)

            # Write the modified content back to the file
            with open(config_file_path, "w") as f:
                f.write(content)
            inkex.errormsg(
                f"""AxiDraw settings updated: Pen Up = {new_up_height}%,
                Pen Down = {new_down_height}%. Please restart Inkscape for
                changes to fully apply."""
            )

        except Exception as e:
            inkex.errormsg(f"An error occurred: {e}")


if __name__ == "__main__":
    AxiDrawHeightSetter().run()
