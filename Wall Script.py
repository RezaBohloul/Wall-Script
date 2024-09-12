# MenuTitle: Wall Script
# -*- coding: utf-8 -*-
__doc__ = """
Pin your script to the wall and enjoy
"""

import vanilla
import os
import json
import textwrap
import GlyphsApp

from AppKit import NSFont, NSColor, NSAttributedString, NSEvent, NSOpenPanel, NSScreen, NSEventMaskKeyDown, NSFileHandlingPanelOKButton, NSForegroundColorAttributeName, NSFontAttributeName, NSCalibratedRGBColorSpace

SCRIPT_FILE = os.path.join(GlyphsApp.GSGlyphsInfo.applicationSupportPath(), "Wall Script.txt")
COLOR_FILE = os.path.join(GlyphsApp.GSGlyphsInfo.applicationSupportPath(), "Wall Script Colors.txt")

TOTAL_SUB_WINDOWS = 4
ROWS = 4
COLS = 6
BOX_HEIGHT = 10
BOX_WIDTH = 150
FONT_SIZE = 13
FONT_BOLD = NSFont.boldSystemFontOfSize_(FONT_SIZE)

PREDEFINED_COLORS = [
    NSColor.redColor(),
    NSColor.colorWithRed_green_blue_alpha_(0.0, 0.85, 0.0, 1.0),
    NSColor.blueColor(),
    NSColor.colorWithRed_green_blue_alpha_(1.0, 0.75, 0.0, 1.0),
    NSColor.orangeColor(),
    NSColor.colorWithRed_green_blue_alpha_(0.0, 0.5, 0.0, 1.0),
    NSColor.colorWithRed_green_blue_alpha_(0.0, 0.8, 0.8, 1.0),
    NSColor.magentaColor(),
    NSColor.colorWithRed_green_blue_alpha_(1.0, 0.0, 0.5, 1.0),
    NSColor.colorWithRed_green_blue_alpha_(0.5, 0.0, 0.25, 1.0),
    NSColor.colorWithRed_green_blue_alpha_(0.5, 0.0, 1.0, 1.0),
    NSColor.brownColor()
]


def nscolor_to_rgb(color):
    """Convert NSColor to an RGB tuple."""
    color = color.colorUsingColorSpaceName_(NSCalibratedRGBColorSpace)
    return (color.redComponent(), color.greenComponent(), color.blueComponent(), color.alphaComponent())


def rgb_to_nscolor(rgb):
    """Convert an RGB tuple to NSColor."""
    return NSColor.colorWithRed_green_blue_alpha_(rgb[0], rgb[1], rgb[2], rgb[3])


if 'CustomColorPickerWindowUnique' not in globals():
    class CustomColorPickerWindowUnique(vanilla.Window):
        def __init__(self, color_options, callback):
            self.callback = callback
            BUTTON_SIZE = 40
            GRID_SPACING = 10
            BUTTONS_PER_ROW = 4
            width = 240
            height = 170
            self.w = vanilla.Window((width, height), "Select Color", closable=True)
            self.w.color_buttons = vanilla.Group((5, 5, 250, 250))

            for i, color in enumerate(color_options):
                x_pos = (i % BUTTONS_PER_ROW) * (BUTTON_SIZE + GRID_SPACING + 10) + 10
                y_pos = (i // BUTTONS_PER_ROW) * (BUTTON_SIZE + GRID_SPACING + 7) + 10
                button = vanilla.Button((x_pos, y_pos, BUTTON_SIZE, BUTTON_SIZE), "", callback=self.color_selected)
                button.color = color
                button.getNSButton().setWantsLayer_(True)
                button.getNSButton().layer().setBackgroundColor_(color.CGColor())
                button.getNSButton().layer().setCornerRadius_(5)
                button.getNSButton().layer().setBorderWidth_(False)
                setattr(self.w.color_buttons, f"button_{i}", button)

            self.w.open()

        def color_selected(self, sender):
            self.callback(sender.color)
            self.w.close()


class ScriptGridWindow:
    def __init__(self):
        self.scripts = {}  # Initialize the scripts attribute
        self.load_scripts()
        self.load_colors()
        self.update_total_sub_windows()

        # Main window initialization
        self.w = vanilla.Window((1035.5, 540), closable=True)
        self.current_sub_window = 0
        self.sub_windows = []
        self.total_sub_windows = TOTAL_SUB_WINDOWS

        # Get screen dimensions and center the window
        screen_frame = NSScreen.mainScreen().frame()
        window_width = 1035.5
        window_height = 540
        window_x = (screen_frame.size.width - window_width) / 2
        window_y = (screen_frame.size.height - window_height) / 2

        # Main window initialization centered on the screen
        self.w = vanilla.Window((window_x, window_y, window_width, window_height), closable=True)
        self.current_sub_window = 0
        self.sub_windows = []
        self.total_sub_windows = TOTAL_SUB_WINDOWS
# ==========================================================================================================
#       Top window color & title
        self.w.titleBackground = vanilla.Group((0, 0, COLS * BOX_WIDTH + 150, 45))
        self.w.titleBackground.getNSView().setWantsLayer_(True)
        self.w.titleBackground.getNSView().layer().setBackgroundColor_(NSColor.keyboardFocusIndicatorColor().CGColor())
        self.w.titleLabel = vanilla.TextBox((1035.5 / 2 - 165, 16, 330, 20), "Wall Script", alignment="center")
        self.w.titleLabel.getNSTextField().setFont_(NSFont.systemFontOfSize_(16))

        self.w.titleLabel2 = vanilla.TextBox((12 - 0, 528, 330, 20), "Wall Script - V.1 - By: Reza Bohloul", alignment="left")
        self.w.titleLabel2.getNSTextField().setFont_(NSFont.systemFontOfSize_(8))

        self.w.titleBackground2 = vanilla.Group((0, 45, 1035.5, 3))
        self.w.titleBackground2.getNSView().setWantsLayer_(True)
        self.w.titleBackground2.getNSView().layer().setBackgroundColor_(NSColor.darkGrayColor().CGColor())

# ==========================================================================================================

        # Add and delete page buttons (+ and -)
        self.w.add_button = vanilla.Button((825, 15, 30, 20), "+", callback=self.add_page)
        self.w.delete_button = vanilla.Button((180, 15, 30, 20), "-", callback=self.delete_page)

        for i in range(self.total_sub_windows):
            self.sub_windows.append(self.create_sub_window(i))

        self.w.subview = vanilla.Group((10, 50, COLS * 200, ROWS * 200))
        self.update_subview(self.current_sub_window)

        # Navigation buttons
        self.w.right_button = vanilla.Button((861, 15, 164, 20), ">", callback=self.navigate_right)
        self.w.left_button = vanilla.Button((10.5, 15, 164, 20), "<", callback=self.navigate_left)

        self.add_key_event_monitor()
        self.w.bind("close", self.remove_key_event_monitor)
        self.w.open()

    def title_edited(self, sender):
        title = sender.get()
        if not title.strip():
            title = f"Wall Script {self.current_sub_window + 1}"
        self.w.titleLabel.set(title)

    def update_total_sub_windows(self):
        if os.path.exists(SCRIPT_FILE):
            with open(SCRIPT_FILE, 'r', encoding='utf-8') as file:
                first_line = file.readline().strip()
                if first_line.startswith("TOTAL_SUB_WINDOWS="):
                    global TOTAL_SUB_WINDOWS
                    TOTAL_SUB_WINDOWS = int(first_line.split('=')[1])
                    self.total_sub_windows = TOTAL_SUB_WINDOWS

    def update_subview(self, index):
        for name in dir(self.w.subview):
            if name.startswith("button_") or name.startswith("tiny_button_") or name.startswith("color_button_") or name.startswith("remove_button_"):
                delattr(self.w.subview, name)

        subview_content = self.sub_windows[index]
        for i, (button, tiny_button, color_button, remove_button) in enumerate(subview_content):
            setattr(self.w.subview, f"button_{i}", button)
            setattr(self.w.subview, f"tiny_button_{i}", tiny_button)
            setattr(self.w.subview, f"color_button_{i}", color_button)
            setattr(self.w.subview, f"remove_button_{i}", remove_button)

        current_title = self.w.titleLabel.get()
        if current_title.startswith("Wall Script"):
            self.w.titleLabel.set(f"Wall Script {index + 1}")

    def create_sub_window(self, index):
        sub_window = []
        gray_color = NSColor.systemGrayColor()
        blue_color = NSColor.systemBlueColor()
        for row in range(ROWS):
            for col in range(COLS):
                box_index = row * COLS + col + index * COLS * ROWS
                x_pos = col * 170
                y_pos = row * 120
                script_name = self.scripts.get(f"box_{box_index}", "No Script")
                display_name = os.path.basename(script_name) if script_name != "No Script" else script_name
                wrapped_name = "\n".join(textwrap.wrap(display_name, width=20))

                button = vanilla.Button((x_pos + 8, y_pos + 10, 150, 100), "", callback=self.run_script)
                button.box_index = box_index
                button.getNSButton().setWantsLayer_(True)
                button_layer = button.getNSButton().layer()
                button_layer.setCornerRadius_(5)
                button_layer.setShadowOpacity_(0)
                button.getNSButton().setBordered_(False)

                saved_color_rgb = self.button_colors.get(f"box_{box_index}", None)
                if saved_color_rgb:
                    color = rgb_to_nscolor(saved_color_rgb)
                    button_layer.setBackgroundColor_(color.CGColor())
                else:
                    button_layer.setBackgroundColor_(gray_color.CGColor() if script_name == "No Script" else blue_color.CGColor())

                attributed_title = NSAttributedString.alloc().initWithString_attributes_(
                    wrapped_name, {
                        NSForegroundColorAttributeName: NSColor.whiteColor(),
                        NSFontAttributeName: FONT_BOLD
                    }
                )
                button.getNSButton().setAttributedTitle_(attributed_title)

                tiny_button = vanilla.Button((x_pos + 1, y_pos + 83, 30, 48), "＋", callback=self.change_script)
                tiny_button.box_index = box_index

                color_button = vanilla.Button((x_pos + 68, y_pos + 83, 30, 48), "⌖", callback=self.show_color_picker)
                color_button.box_index = box_index

                remove_button = vanilla.Button((x_pos + 135, y_pos + 83, 30, 48), "∅", callback=self.remove_script)
                remove_button.box_index = box_index

                sub_window.append((button, tiny_button, color_button, remove_button))
        return sub_window

    def run_script(self, sender):
        script_path = self.scripts.get(f"box_{sender.box_index}", None)
        if script_path:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()
            try:
                exec(script_code, globals())
                self.w.close()  # Close the main window after executing the script

            except Exception as e:
                GlyphsApp.Message("Script Error", f"Error: {str(e)}")

    def change_script(self, sender):
        open_panel = NSOpenPanel.openPanel()
        open_panel.setTitle_("Choose Script")
        open_panel.setAllowedFileTypes_(["py"])
        if open_panel.runModal() == NSFileHandlingPanelOKButton:
            selected_file = open_panel.URL().path()
            self.scripts[f"box_{sender.box_index}"] = selected_file
            self.refresh_button_view(sender.box_index)
            self.save_scripts()

    def remove_script(self, sender):
        if f"box_{sender.box_index}" in self.scripts:
            del self.scripts[f"box_{sender.box_index}"]
            self.refresh_button_view(sender.box_index)
            self.save_scripts()

        if f"box_{sender.box_index}" in self.button_colors:
            del self.button_colors[f"box_{sender.box_index}"]
            self.refresh_button_view(sender.box_index)
            self.save_colors()

    def show_color_picker(self, sender):
        def color_selected_callback(selected_color):
            color_rgb = nscolor_to_rgb(selected_color)
            self.button_colors[f"box_{sender.box_index}"] = color_rgb
            self.refresh_button_view(sender.box_index)
            self.save_colors()

        CustomColorPickerWindowUnique(PREDEFINED_COLORS, color_selected_callback)

    def refresh_button_view(self, box_index):
        script_name = self.scripts.get(f"box_{box_index}", "No Script")
        display_name = os.path.basename(script_name) if script_name != "No Script" else script_name
        wrapped_name = "\n".join(textwrap.wrap(display_name, width=20))

        saved_color_rgb = self.button_colors.get(f"box_{box_index}", None)
        if saved_color_rgb:
            color = rgb_to_nscolor(saved_color_rgb)
        else:
            gray_color = NSColor.systemGrayColor()
            blue_color = NSColor.systemBlueColor()
            color = gray_color if script_name == "No Script" else blue_color

        button = getattr(self.w.subview, f"button_{box_index % (COLS * ROWS)}")
        button_layer = button.getNSButton().layer()
        button_layer.setBackgroundColor_(color.CGColor())

        attributed_title = NSAttributedString.alloc().initWithString_attributes_(
            wrapped_name, {
                NSForegroundColorAttributeName: NSColor.whiteColor(),
                NSFontAttributeName: FONT_BOLD
            }
        )
        button.getNSButton().setAttributedTitle_(attributed_title)

    def navigate_right(self, sender):
        if self.current_sub_window < self.total_sub_windows - 1:
            self.current_sub_window += 1
            self.update_subview(self.current_sub_window)

    def navigate_left(self, sender):
        if self.current_sub_window > 0:
            self.current_sub_window -= 1
            self.update_subview(self.current_sub_window)

    def add_page(self, sender):
        self.total_sub_windows += 1
        self.sub_windows.append(self.create_sub_window(self.total_sub_windows - 1))
        self.current_sub_window = self.total_sub_windows - 1
        self.update_subview(self.current_sub_window)
        self.save_total_sub_windows()

    def delete_page(self, sender):
        if self.total_sub_windows > 1:
            del self.sub_windows[-1]
            self.total_sub_windows -= 1
            self.current_sub_window = min(self.current_sub_window, self.total_sub_windows - 1)
            self.update_subview(self.current_sub_window)
            self.save_total_sub_windows()

    def save_total_sub_windows(self):
        with open(SCRIPT_FILE, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            file.seek(0)
            file.write(f"TOTAL_SUB_WINDOWS={self.total_sub_windows}\n")
            file.writelines(lines[1:])  # write the remaining lines

    def load_scripts(self):
        if os.path.exists(SCRIPT_FILE):
            with open(SCRIPT_FILE, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines[1:]:  # Skip the first line which is TOTAL_SUB_WINDOWS
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key.startswith("box_"):
                            self.scripts[key] = value
        else:
            self.scripts = {}

    def save_scripts(self):
        with open(SCRIPT_FILE, 'w', encoding='utf-8') as file:
            file.write(f"TOTAL_SUB_WINDOWS={self.total_sub_windows}\n")
            for key, value in self.scripts.items():
                file.write(f"{key}={value}\n")

    def load_colors(self):
        if os.path.exists(COLOR_FILE):
            with open(COLOR_FILE, 'r', encoding='utf-8') as file:
                self.button_colors = json.load(file)
        else:
            self.button_colors = {}

    def save_colors(self):
        with open(COLOR_FILE, 'w', encoding='utf-8') as file:
            json.dump(self.button_colors, file, indent=2)

    def add_key_event_monitor(self):
        self.key_event_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(NSEventMaskKeyDown, self.handle_key_event)

    def handle_key_event(self, event):
        key_code = event.keyCode()

        if key_code == 123:  # Left arrow key
            self.navigate_left(None)
            return None  # Prevent system beep
        elif key_code == 124:  # Right arrow key
            self.navigate_right(None)
            return None  # Prevent system beep
        elif key_code == 53:  # Escape key
            self.w.close()  # Close the window
            return None  # Prevent system beep
        return event  # Pass through unhandled keys

    def remove_key_event_monitor(self, sender):
        if self.key_event_monitor:
            NSEvent.removeMonitor_(self.key_event_monitor)
            self.key_event_monitor = None


# Initialize the window
ScriptGridWindow()
