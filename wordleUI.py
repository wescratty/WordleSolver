"""
Author: Wes Cratty
Created: 1/8/2024
File: wordleUI.py

Description: Tkinter UI for the Wordle solver. Lets the user mark known
letters (green), letters known to be present but misplaced (yellow), and
letters known to be absent (gray) via buttons and a letter list, then
shows ranked candidate words from wordle.Words.find().
"""

import json
import os
from helpers import tkinterface
from helpers import filemanager
from helpers import utility as ut
import wordle


class WordleUI:
    """Creates tkinter UI"""

    def __init__(self):
        """Initialize"""
        self.wordle = wordle.Words()
        self.list_box = None
        self.task_frame = None
        self.selected_task_index = None
        self.context_menu = None
        self.current_button = None
        self.button_not_list = [[], [], [], [], []]
        self.current_button_id = None
        self.unused_letter = None
        self.wild_list = list()
        self.tk = tkinterface.SuperTk()

        self.settings = dict()  # Holds settings loaded from settings.json (currently just theme)
        self.read_in_settings()  # Read in settings or create file. Instantiate related objects
        self.tk.set_theme(self.settings['theme'])

        win_obj = self.tk.get_window(title='Wordle Solver 2o',
                                     geometry='720x750', scroll=True)  # Create main window
        self.window = win_obj['window']
        self.scroll_area = win_obj['scroll_area']

        self.add_settings_menu()  # Create settings menu (top left ui) to allow selecting color theme

        self.severity = ["lime", "white", "yellow", "red", "red"]  # Logging message color
        self.button_inactive = "gray"
        self.button_identified = "black"
        self.button_active = "red"
        self.checkbox_repeat_var = self.tk.tk.BooleanVar()
        self.checkbox_hide_fa_var = self.tk.tk.BooleanVar()

    def set_unused_letter(self):
        """Callback placeholder passed to the path/text chooser frame; currently unused."""
        pass

    def toggle_button_shade(self, b_id):
        """Toggle button color: If button_inactive then button_active, if button_active then button_inactive"""
        # NOTE: this compares against the literal string "self.button_inactive"
        # rather than the self.button_inactive attribute, so it never matches and
        # this always falls through to the "activate" branch. Left as-is to avoid
        # changing existing UI behavior.
        if self.get_button_shade(b_id) == "self.button_inactive":
            self.task_frame['b_list'][int(b_id)].configure(bg=self.button_inactive)
        else:
            self.task_frame['b_list'][int(b_id)].configure(bg=self.button_active)

    def init_button_shade(self):
        """Set all buttons to button_inactive"""
        for b in self.task_frame['b_list']:
            b.configure(bg=self.button_inactive)

    def get_button_shade(self, b_id):
        """Return button color"""
        return self.task_frame['b_list'][int(b_id)].cget("bg")

    def check_active_button(self, b_id):
        """Return if this button or thread is active"""
        color = self.get_button_shade(b_id)
        if color == self.button_active:
            return True
        else:
            return False

    def clear_ui(self, force=False):
        """Reset UI to starting state"""
        if force or not self.check_active_button("0") and not self.check_active_button("1"):  # Clear dropdown menu
            if self.list_box is not None:
                self.list_box.destroy()
            self.init_button_shade()

        self.scroll_bottom()

    # ==============================
    #     Logging / settings
    # ==============================
    def log(self, message, priority):
        """Display message in UI"""
        # Create new label
        var_text = self.tk.get_label(message, fg=self.severity[priority.value], bg='black', width=80)
        self.scroll_bottom()
        return var_text  # Returns the last var_text which can be set directly from receiver.
        # This is for reusing the same line and updating, no new line

    def read_in_settings(self):
        """Load settings.json (currently just the color theme) if present."""
        if os.path.isfile('settings.json'):
            self.settings = json.loads(filemanager.get_file_contents('settings.json'))

    def write_out_settings(self):
        """Persist the current settings to settings.json."""
        filemanager.write_file(json.dumps(self.settings), os.path.join(os.getcwd(), 'settings.json'))

    def set_theme(self, theme):
        """Set user color theme choice"""
        self.settings["theme"] = theme.value
        self.write_out_settings()
        self.log(f"Theme will take effect on next startup, set to {theme.name}", ut.LogType.info)

    def add_settings_menu(self):
        """Add a menu which allows users to select a color theme for the UI"""
        settings_menu, theme_menu, general_menu = self.tk.add_settings_menu()

        # Add theme options
        theme_menu.add_command(label=ut.Theme.newspaper.name, command=lambda: self.set_theme(ut.Theme.newspaper))
        theme_menu.add_command(label=ut.Theme.retroMac.name, command=lambda: self.set_theme(ut.Theme.retroMac))
        theme_menu.add_command(label=ut.Theme.inverse_newspaper.name,
                               command=lambda: self.set_theme(ut.Theme.inverse_newspaper))
        theme_menu.add_command(label=ut.Theme.dungeon.name, command=lambda: self.set_theme(ut.Theme.dungeon))

    # ==============================
    #     UI drop down management
    # ==============================
    def on_list_box_select(self, event):
        """Handles dropdown selection, runs selected task"""
        if self.selected_task_index:
            selected_task = self.list_box.get(self.selected_task_index)  # Get user selection from dropdown

            self.current_button['text'] = selected_task  # Display the name of the task

    def create_list_box(self):
        """Creates the A-Z letter selection list box."""
        keys = list(self.wordle.letters.keys())  # Get keys
        self.list_box = self.tk.gen_list_box(keys, self.on_list_box_select)
        self.list_box.pack(fill=self.tk.tk.X)  # add to UI
        self.list_box.bind("<Double-Button-1>", self.on_list_box_select)  # Make dropdown choice a double click
        self.list_box.bind("<<ListboxSelect>>", self.on_listbox_select)
        self.scroll_bottom()

        # Only add context menu to Select Task dropdown
        self.list_box.bind("<Button-3>", self.on_right_click)

    def on_listbox_select(self, event):  # Requires sending in event even though it is not used
        selection = self.list_box.curselection()
        if selection:  # Only set if selection has data
            self.selected_task_index = selection

    def scroll_bottom(self):
        """Scrolls view to last added post to UI console view"""
        self.tk.window.update()
        self.tk.canvas.yview_moveto(1)

    def on_right_click(self, event):
        """Only available when Select Task button was pressed"""
        self.context_menu.post(event.x_root, event.y_root)

    def is_task(self):
        """Set the currently selected letter as the confirmed (green) letter for
        the active position button."""
        if self.selected_task_index:
            selected_task = self.list_box.get(self.selected_task_index)  # Gets selection
            self.current_button['text'] = selected_task
            self.current_button['bg'] = self.button_identified
        else:
            self.log("Please select a task before editing.", ut.LogType.info)

    def not_task(self):
        """Mark the currently selected letter as present but not at the active
        position (yellow), via the right-click context menu."""
        if self.selected_task_index:
            selected_task = self.list_box.get(self.selected_task_index)  # Gets selection

            self.button_not_list[self.current_button_id].append(selected_task)
            self.wild_list.append(selected_task)
        else:
            self.log("Please select a task before editing.", ut.LogType.info)

    def clear_task(self):
        """Clear the confirmed letter on the currently active position button."""
        self.current_button['text'] = ''

    def clear_nots(self):
        """Clear the 'not at this position' letters for the currently active button."""
        self.button_not_list[int(self.current_button_id)] = list()

    def reset(self):
        """Reset all position buttons and letter constraints to their initial state."""
        for b in self.task_frame['b_list']:
            b['text'] = ''
        self.unused_letter.set('')
        self.button_not_list = [[], [], [], [], []]
        self.wild_list = list()

        self.unused_letter.set('')

    def go(self):
        """Run the solver against the current button state and constraints,
        then log the ranked candidate words to the UI."""
        b_list = list()
        for b in self.task_frame['b_list']:
            b_list.append(b['text'])

        repeats = self.checkbox_repeat_var.get()
        hide = self.checkbox_hide_fa_var.get()  # "Hide Fa": hide unscored (non-answer-list) words

        self.wordle.find(word_list=b_list, bad_list=list(self.unused_letter.get().upper()),
                         not_list=self.button_not_list, wild_list=list(self.wild_list), repeats=repeats)

        self.log(f'================== {len(self.wordle.map)} ==================', ut.LogType.info)

        # List candidates, highest-scored first.
        for word, score in sorted(self.wordle.map.items(), key=lambda item: round(item[1]), reverse=True):
            if hide:
                if score > 0:
                    rounded_score = round(score)
                    self.log(f'{word}: {rounded_score}', ut.LogType.task)
            else:
                self.log(f'{word}', ut.LogType.task)

    def on_radio_select(self):
        """Checkbox change callback; no action needed since go() reads the
        checkbox state directly."""
        pass

    def select_task(self, b_id):
        """ On button click, UI Button Selector"""
        self.clear_ui(True)  # Re set
        self.toggle_button_shade(b_id)  # Set shade to button_active if not active
        self.create_list_box()
        self.current_button = self.task_frame['b_list'][int(b_id)]
        self.current_button_id = int(b_id)

    def main(self):
        """Creates UI Buttons App Start"""

        lf = self.tk.get_label_frame('Control', self.tk.window)
        # Create button
        self.tk.get_button(lf, "Go", self.go, height=4, width=9, ) \
            .pack(side=self.tk.tk.LEFT, fill=self.tk.tk.X, expand=self.tk.tk.FALSE, pady=self.tk.pady, padx=self.tk.padx)

        self.tk.get_check_box(lf, text="Allow Repeats", var=self.checkbox_repeat_var,
                              command=self.on_radio_select)\
            .pack(side=self.tk.tk.LEFT, fill=self.tk.tk.X, expand=self.tk.tk.FALSE, pady=self.tk.pady, padx=self.tk.padx)

        self.tk.get_check_box(lf, text="Hide Fa", var=self.checkbox_hide_fa_var,
                              command=self.on_radio_select)\
            .pack(side=self.tk.tk.LEFT, fill=self.tk.tk.X, expand=self.tk.tk.FALSE, pady=self.tk.pady, padx=self.tk.padx)

        self.tk.get_button(lf, "Reset", self.reset, height=4, width=9, ) \
            .pack(side=self.tk.tk.LEFT, fill=self.tk.tk.X, expand=self.tk.tk.FALSE, pady=self.tk.pady, padx=self.tk.padx)

        lf.pack(side=self.tk.tk.TOP, pady=self.tk.pady, padx=self.tk.padx)

        self.checkbox_repeat_var.set(False)
        self.checkbox_hide_fa_var.set(True)
        # Text entry for letters known to not be in the word
        path_to_config_frame = self.tk.generate_path_file_chooser_frame('Letters Not Used:', self.tk.window,
                                                                        self.set_unused_letter)
        path_to_config_frame["pack"]()
        self.unused_letter = path_to_config_frame["var"]
        path_to_config_frame["lf"].pack()

        # Create field set with button list
        self.task_frame = self.tk.generate_label_frame_of_buttons("Letters", ["", "", "", "", "", ],
                                                                  self.select_task, self.tk.window)

        self.task_frame["pack"]()
        self.task_frame["lf"].pack()
        self.init_button_shade()

        # Create context menu
        self.context_menu = self.tk.tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Not", command=self.not_task)
        self.context_menu.add_command(label="Clear", command=self.clear_task)
        self.context_menu.add_command(label="Clear Nots", command=self.clear_nots)

        self.log(f'Good starters', ut.LogType.task)

        for i in range(0, len(self.wordle.starters), 3):
            self.log(f'{self.wordle.starters[i]}\t{self.wordle.starters[i + 1]}\t{self.wordle.starters[i + 2]}',
                     ut.LogType.task)
        self.window.mainloop()


def main():
    wordle_man = WordleUI()
    wordle_man.main()


if __name__ == "__main__":
    main()
