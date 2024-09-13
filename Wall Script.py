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

from AppKit import NSFont, NSColor, NSAttributedString, NSImage, NSEvent, NSOpenPanel, NSScreen, NSEventMaskKeyDown, NSFileHandlingPanelOKButton, NSForegroundColorAttributeName, NSFontAttributeName, NSCalibratedRGBColorSpace, NSImageScaleProportionallyUpOrDown

SCRIPT_FILE = os.path.join(GlyphsApp.GSGlyphsInfo.applicationSupportPath(), "Wall Script.txt")
COLOR_FILE = os.path.join(GlyphsApp.GSGlyphsInfo.applicationSupportPath(), "Wall Script Colors.txt")

TOTAL_SUB_WINDOWS = 4
ROWS = 4
COLS = 4
BOX_HEIGHT = 90
BOX_WIDTH = 140
GRID_SPACING = 10
TITLE_BAR_HEIGHT = 45
FONT_SIZE = 12
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

# Place color window buttons without text in the center of the screen.
def make_color_window(color_options, callback):
    BUTTON_SIZE = 40
    BUTTONS_PER_ROW = 4
    GRID_SPACING = 20
    width = BUTTONS_PER_ROW * (BUTTON_SIZE + GRID_SPACING) + GRID_SPACING - 10
    height = (len(color_options) / BUTTONS_PER_ROW) * (BUTTON_SIZE + GRID_SPACING) + GRID_SPACING - 8

    # Create the window with default position
    w = vanilla.Window((width, height), "Select Color", closable=True)

    # Get the main screen's frame
    screen_frame = NSScreen.mainScreen().frame()
    
    # Calculate the position to center the window
    x_pos = (screen_frame.size.width - width) / 2
    y_pos = (screen_frame.size.height - height) / 2
    
    # Set the window's position
    w.setPosSize((x_pos, y_pos, width, height))

    for i, color in enumerate(color_options):
        row = i // BUTTONS_PER_ROW
        col = i % BUTTONS_PER_ROW
        x_pos = GRID_SPACING + col * (BUTTON_SIZE + GRID_SPACING) - 5
        y_pos = GRID_SPACING + row * (BUTTON_SIZE + GRID_SPACING) - 5

        # Create vanilla button with no title
        button = vanilla.Button((x_pos, y_pos, BUTTON_SIZE, BUTTON_SIZE), "", callback=callback)
        button.color = color
        
        # Get NSButton instance from vanilla button
        ns_button = button.getNSButton()
        ns_button.setWantsLayer_(True)
        ns_button.layer().setBackgroundColor_(color.CGColor())
        ns_button.layer().setCornerRadius_(5)
        ns_button.layer().setBorderWidth_(0)
        ns_button.setBordered_(False)
        ns_button.setImageScaling_(NSImageScaleProportionallyUpOrDown)
        
        setattr(w, f"button_{i}", button)
    
    return w

if 'CustomColorPickerWindowUnique' not in globals():
    class CustomColorPickerWindowUnique(vanilla.Window):
        def __init__(self, color_options, callback):
            self.callback = callback
            self.w = make_color_window(color_options, self.color_selected)
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

        # Get screen dimensions and center the window
        screen_frame = NSScreen.mainScreen().frame()
        window_width = BOX_WIDTH * COLS + GRID_SPACING * 2
        window_height = BOX_HEIGHT * ROWS + TITLE_BAR_HEIGHT + GRID_SPACING * 2
        window_x = (screen_frame.size.width - window_width) / 2
        window_y = (screen_frame.size.height - window_height) / 2

        # Main window initialization centered on the screen
        self.w = vanilla.Window((window_x, window_y, window_width, window_height), closable=True)
        self.current_sub_window = 0

        self.total_sub_windows = TOTAL_SUB_WINDOWS
# ==========================================================================================================
#       Top window color & title
        self.w.titleBackground = vanilla.Group((0, 0, window_width, TITLE_BAR_HEIGHT))
        self.w.titleBackground.getNSView().setWantsLayer_(True)
        self.w.titleBackground.getNSView().layer().setBackgroundColor_(NSColor.keyboardFocusIndicatorColor().CGColor())
        self.w.titleLabel = vanilla.TextBox((window_width / 2 - 165, 16, 330, 20), "Wall Script", alignment="center")
        self.w.titleLabel.getNSTextField().setFont_(NSFont.systemFontOfSize_(16))

        self.w.titleLabel2 = vanilla.TextBox((12 - 0, window_height - 12, 330, 20), "Wall Script - V.1 - By: Reza Bohloul", alignment="left")
        self.w.titleLabel2.getNSTextField().setFont_(NSFont.systemFontOfSize_(8))

        self.w.bar = vanilla.Group((0, TITLE_BAR_HEIGHT, window_width, 2))
        self.w.bar.getNSView().setWantsLayer_(True)
        self.w.bar.getNSView().layer().setBackgroundColor_(NSColor.darkGrayColor().CGColor())

# ==========================================================================================================

        # Add and delete page buttons (+ and -)
        self.w.add_button = vanilla.Button((window_width - 64, 15, 12, 12), "", callback=self.add_page)
        self.w.add_button.getNSButton().setImage_(NSImage.imageNamed_("NSAddTemplate"))
        self.w.add_button.getNSButton().setBordered_(False)
        self.w.add_button.getNSButton().setImageScaling_(NSImageScaleProportionallyUpOrDown)

        self.w.delete_button = vanilla.Button((48, 15, 12, 12), "", callback=self.delete_page)
        self.w.delete_button.getNSButton().setImage_(NSImage.imageNamed_("NSRemoveTemplate"))
        self.w.delete_button.getNSButton().setBordered_(False)
        self.w.delete_button.getNSButton().setImageScaling_(NSImageScaleProportionallyUpOrDown)

        self.w.subview = vanilla.Group((GRID_SPACING, TITLE_BAR_HEIGHT + GRID_SPACING, window_width, BOX_HEIGHT * ROWS))
        self.update_subview(self.current_sub_window)

        # Navigation buttons
        self.w.right_button = vanilla.Button((window_width - 32, 12, 14, 20), "", callback=self.navigate_right)
        self.w.right_button.getNSButton().setImage_(NSImage.imageNamed_("NSTouchBarGoForwardTemplate"))
        self.w.right_button.getNSButton().setBordered_(False)
        self.w.right_button.getNSButton().setImageScaling_(NSImageScaleProportionallyUpOrDown)
        self.w.left_button = vanilla.Button((14, 12, 14, 20), "", callback=self.navigate_left)
        self.w.left_button.getNSButton().setImage_(NSImage.imageNamed_("NSTouchBarGoBackTemplate"))
        self.w.left_button.getNSButton().setBordered_(False)
        self.w.left_button.getNSButton().setImageScaling_(NSImageScaleProportionallyUpOrDown)

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

        self.create_sub_window(index)

        current_title = self.w.titleLabel.get()
        if current_title.startswith("Wall Script"):
            self.w.titleLabel.set(f"Wall Script {index + 1}")

    def create_sub_window(self, index):
        gray_color = NSColor.systemGrayColor()
        blue_color = NSColor.systemBlueColor()
        idx = 0
        for row in range(ROWS):
            for col in range(COLS):
                box_index = row * COLS + col + index * COLS * ROWS
                x_pos = col * BOX_WIDTH
                y_pos = row * BOX_HEIGHT
                script_name = self.scripts.get(f"box_{box_index}", "No Script")
                display_name = os.path.basename(script_name) if script_name != "No Script" else script_name
                wrapped_name = "\n".join(textwrap.wrap(display_name, width=19))

                button = vanilla.Button((x_pos + 8, y_pos + 6, BOX_WIDTH - GRID_SPACING - 6, BOX_HEIGHT - GRID_SPACING - 6), "", callback=self.run_script)
                setattr(self.w.subview, f"button_{idx}", button)
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

                tiny_button = vanilla.Button((x_pos + 2, y_pos + BOX_HEIGHT - 24, 22, 22), "", callback=self.change_script)
                setattr(self.w.subview, f"tiny_button_{idx}", tiny_button)
                tiny_button.getNSButton().setImage_(NSImage.imageNamed_("NSAddTemplate"))
                tiny_button.getNSButton().setBordered_(False)
                tiny_button.box_index = box_index

                color_button = vanilla.Button((x_pos + (BOX_WIDTH / 2) - 12, y_pos + BOX_HEIGHT - 24, 22, 22), "", callback=self.show_color_picker)
                setattr(self.w.subview, f"color_button_{idx}", color_button)
                color_button.getNSButton().setImage_(NSImage.imageNamed_("NSActionTemplate"))
                color_button.getNSButton().setBordered_(False)
                color_button.box_index = box_index

                remove_button = vanilla.Button((x_pos + BOX_WIDTH - 24, y_pos + BOX_HEIGHT - 24, 22, 22), "", callback=self.remove_script)
                setattr(self.w.subview, f"remove_button_{idx}", remove_button)
                remove_button.getNSButton().setImage_(NSImage.imageNamed_("GSDisabledTemplate"))
                remove_button.getNSButton().setBordered_(False)
                remove_button.box_index = box_index

                idx += 1

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
        wrapped_name = "\n".join(textwrap.wrap(display_name, width=19))

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
        self.current_sub_window = self.total_sub_windows - 1
        self.update_subview(self.current_sub_window)
        self.save_total_sub_windows()

    def delete_page(self, sender):
        if self.total_sub_windows > 1:
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
