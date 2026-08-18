"""
Author: Wes Cratty
Created: 1/18/2023
File: tkinterface.py

Description: Handles all tk interface creation objects
"""
import json
import os
from tkinter import filedialog, ttk
import tkinter as tk
from helpers import filemanager


class SuperTk:
    """Extends tkinter (should be refactored to inherit)
    Supplies creation methods to simplify usage"""
    def __init__(self):
        self.opacity = 0
        self.bg = ''
        self.fg = ''

        if os.path.isfile('settings.json'):
            settings_dict = json.loads(filemanager.get_file_contents('settings.json'))
            self.set_theme(settings_dict["theme"])

        self.tk = tk
        self.ttk = ttk
        self.window = None
        self.scroll_area = None
        self.scrollbar = None
        self.canvas_frame = None
        self.canvas = None
        self.ask_directory = filedialog.askdirectory
        self.ask_file = filedialog.askopenfile
        self.ask_save_file = filedialog.asksaveasfile
        self.invoked = {}
        self.id_counter = 0
        self.END = "end"
        self.progressbar = None
        self.progressbar_max_val = 100
        self.progress_currentValue = 0
        self.str_var = None
        self.padx = 10
        self.pady = 5
        self.top = None

    def create(self):
        """Create canvas"""
        self.canvas_frame = self.canvas.create_window(0, 0, window=self.scroll_area, anchor=tk.NW,
                                                      tags="self.scroll_area")

    def _on_mousewheel(self, event):
        """Adds mouse wheel scrolling"""
        scroll_delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(scroll_delta, "units")

    def get_window(self, title='', geometry='500x1000', scroll=False):
        """Creates main window"""
        if not self.window:
            """Sets main window attributes"""
            window = self.tk.Tk()
            window.attributes('-alpha', self.opacity)
            window.title(title)
            window.config(bg=self.bg)
            window.geometry(geometry)

            if scroll:
                """If true, sets additional scrolling and adds scroll bars"""
                main_frame = tk.Frame(window, background=self.bg, highlightbackground=self.fg, highlightthickness=2)
                main_frame.pack(fill="x", expand=0, anchor='n')

                # ----------- Scroll bar --------------
                self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical")
                self.scrollbar.pack(side="right", fill="y")

                # ----------- Canvas --------------
                self.canvas = tk.Canvas(main_frame, background=self.bg, highlightbackground=self.bg, yscrollcommand=self.scrollbar.set)
                self.canvas.pack(side="left", fill="x", expand=1, anchor='n')
                style = ttk.Style()
                style.theme_use('clam')
                style.configure("Vertical.TScrollbar", gripcount=0,
                                background=self.bg, darkcolor=self.bg, lightcolor=self.fg,
                                troughcolor=self.bg, bordercolor=self.fg, arrowcolor=self.bg)
                self.scrollbar.config(command=self.canvas.yview)
                self.canvas.xview_moveto(0)
                self.canvas.yview_moveto(0)

                # ----------- Frame --------------
                self.scroll_area = tk.Frame(self.canvas, background=self.fg, highlightbackground=self.bg)

                # ----------- create_window --------------
                def _configure_interior(event):
                    # Update the scrollbars to match the size of the inner frame.
                    size = (self.scroll_area.winfo_reqwidth(), self.scroll_area.winfo_reqheight())
                    self.canvas.config(scrollregion="0 0 %s %s" % size)
                    if self.scroll_area.winfo_reqwidth() != self.canvas.winfo_width():
                        # Update the canvas's width to fit the inner frame.
                        self.canvas.config(width=self.scroll_area.winfo_reqwidth())

                self.scroll_area.bind('<Configure>', _configure_interior)
                self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

                def _configure_canvas(event):
                    if self.scroll_area.winfo_reqwidth() != self.canvas.winfo_width():
                        # Update the inner frame's width to fill the canvas.
                        self.canvas.itemconfigure(self.canvas_frame, width=self.canvas.winfo_width())

                self.canvas.bind('<Configure>', _configure_canvas)
                self.scroll_area.pack(fill="x", expand=1)
                self.scrollbar.update()
                self.scroll_area.update()
                self.create()
                self.window = window
                self.window.update()
                return {'window': self.window, 'scroll_area': self.scroll_area}

            else:
                self.window = window
                return self.window

    def get_label(self, text=None, bg=None, fg=None, width=None, append_to=None, str_var=None, side=None):
        """Creates a label
        Returns the text variable in which text can be added """
        if not append_to:  # append to default
            append_to = self.scroll_area

        if str_var is None:  # get new string var
            var_text = self.get_str_var()
        else:
            var_text = str_var

        var_text.set(text)
        bg = self.bg if bg is None else bg
        fg = self.fg if fg is None else fg

        # store in a dictionary in the event of needing to update this object
        self.store(
            self.tk.Label(append_to, textvariable=var_text, width=width, bg=bg, fg=fg, anchor=tk.W, justify='left')
            .pack(side=side, fill=self.tk.X))
        return var_text

    def get_str_var(self):
        """Creates tk.StringVar
        Returns the text variable in which text can be added """

        self.str_var = self.tk.StringVar()

        # store in a dictionary in the event of needing to update this object
        return self.store(self.str_var, "strvar")

    def get_text_box(self, append_to=None, height=1, width=30):
        """Creates tk.Text
        Returns the tk.Text """

        append_to = append_to if append_to else self.scroll_area
        tb = self.tk.Text(append_to, height=height, width=width, bg=self.bg, fg=self.fg)
        tb.config(insertbackground=self.fg)

        # store in a dictionary in the event of needing to update this object
        return self.store(tb, "textbox")

    def get_entry_box(self, append_to=None, height=1, width=30, validatecommand=None, str_var=None,  validate=None):
        """Creates tk.Entry
        Returns the tk.Entry """

        append_to = append_to if append_to else self.scroll_area
        tb = self.tk.Entry(append_to, width=width, bg=self.bg, fg=self.fg, validate=validate, textvariable=str_var,
                           validatecommand=validatecommand)
        tb.config(insertbackground=self.fg)

        # store in a dictionary in the event of needing to update this object
        return self.store(tb, "entrybox")

    def get_spin_box(self, append_to, str_var, call_back):
        """Creates tk.Spinbox
        Returns the tk.Spinbox """

        sb = self.tk.Spinbox(
            append_to,
            from_=1,
            to=100,
            textvariable=str_var,
            wrap=True,
            vcmd=call_back,
            fg=self.fg,
            bg=self.bg,
            command=lambda: call_back(str_var.get())  # Pass the StringVar value to the callback

        )

        return sb

    def get_label_frame(self, title, append_to):
        """Creates tk.LabelFrame
        Returns the tk.LabelFrame """

        append_to = append_to if append_to else self.window

        # store in a dictionary in the event of needing to update this object
        return self.store(self.tk.LabelFrame(append_to, text=title, bg=self.bg, fg=self.fg), "lableframe")

    def gen_list_box(self, _list, call_back, height=20, width=10):
        """Creates tk.Listbox
        Returns the tk.Listbox"""

        lb1_values = tk.Variable(value=_list)

        # store in a dictionary in the event of needing to update this object
        listbox = self.store(self.tk.Listbox(self.window, listvariable=lb1_values, height=height, width=width,
                                             bg=self.bg, fg=self.fg), "listbox")

        listbox.bind('<<ListboxSelect>>', call_back)
        return listbox

    def pack_in(self, item):
        """Pack tk objects to left"""
        item.pack(side=tk.LEFT, fill=tk.X, expand=tk.FALSE, pady=self.pady, padx=self.padx)

    def pack_stack(self, item):
        """Pack tk objects to top"""
        item.pack(side=tk.TOP, expand=tk.TRUE, pady=self.pady, padx=self.padx)

    def generate_path_file_chooser_frame(self, title, append_to, call_back):
        """Generates a label frame with a text entry field.

        call_back is accepted for API symmetry with other generate_* helpers
        but is currently unused (no button is attached to invoke it)."""
        ret_obj = {"lf": self.get_label_frame(title, append_to), "rb_list": list(), "var": self.get_str_var()}

        def pack():
            for _rb in ret_obj["rb_list"]:
                self.pack_in(_rb)

        ret_obj["pack"] = pack

        e_b = self.get_entry_box(append_to=ret_obj["lf"], str_var=ret_obj["var"], width=100)
        ret_obj["rb_list"].append(e_b)
        return ret_obj

    def generate_label_frame_of_buttons(self, title, b_names, call_back, append_to):
        """Generates a label frame of buttons"""

        ret_obj = {"lf": self.get_label_frame(title, append_to), "b_list": list(), "var": self.get_str_var()}
        ret_obj["var"].set(None)

        def pack():
            for _b in ret_obj["b_list"]:
                self.pack_in(_b)

        ret_obj["pack"] = pack

        val = 0
        for b in b_names:
            ret_obj["b_list"].append(self.get_button(ret_obj["lf"], b, lambda m=val: call_back(str(m)), width=9, height=4))
            val += 1
        return ret_obj

    def generate_label_frame_of_text_boxes(self, title, b_names, call_back, append_to):
        """Generates a label frame of buttons"""

        ret_obj = {"lf": self.get_label_frame(title, append_to), "b_list": list(), "var": self.get_str_var()}
        ret_obj["var"].set(None)

        def pack():
            for _b in ret_obj["b_list"]:
                self.pack_in(_b)

        ret_obj["pack"] = pack

        val = 0
        for b in b_names:
            ret_obj["b_list"].append(self.get_text_box(width=9, height=4, append_to=ret_obj["lf"]))
            val += 1
        return ret_obj

    def get_button(self, frame, name, func, width, height):
        """Returns tk.Button"""
        return self.store(self.tk.Button(
            frame,
            text=name,
            width=width,
            height=height,
            bg=self.bg,
            fg=self.fg,
            command=func
        ), "button")

    def get_radio_button(self, frame, text, var, value, command):
        """Returns tk.Radiobutton"""

        # store in a dictionary in the event of needing to update this object
        return self.store(self.tk.Radiobutton(frame, text=text, variable=var, selectcolor='black', background=self.bg,
                                              fg=self.fg, value=value, command=command), "radio")

    def get_check_box(self, frame, text, var, command):
        """Returns tk.Checkbutton"""

        # store in a dictionary in the event of needing to update this object
        return self.store(
            self.tk.Checkbutton(frame, text=text, variable=var, bg=self.bg, fg=self.fg, onvalue=1, offvalue=0,
                                command=command), "ckeckbox")

    def get_dir(self, start_path="C:", title="Select Directory", initialdir=None):
        """Use tk filedialog.askdirectory to prompt user to select a directory"""
        if not initialdir:
            initialdir = os.path.normpath(start_path)
        folder = self.ask_directory(initialdir=initialdir, title=title)
        if os.path.isdir(folder):
            return folder
        else:
            return False

    def get_file(self, start_path="C:", title="Select File", filetypes="yaml"):
        """Use tk filedialog.askfile to prompt user to select a file"""
        file = self.ask_file(initialdir=os.path.normpath(start_path),
                             title=title, filetypes=[("YAML files", f"*.{filetypes}",), ("All files", "*.*")])
        if hasattr(file, "name"):
            return file.name
        else:
            return None

    def save_file(self, start_path="C:", title="Name File", defaultextension=".yaml"):
        """Use tk filedialog.asksaveasfile to prompt user to select a file"""
        file = self.ask_save_file(initialdir=os.path.normpath(start_path),
                                  title=title, filetypes=[("All files", "*.*")], defaultextension=defaultextension)
        if hasattr(file, "name"):
            return file
        else:
            return None

    def get_new_id(self):
        self.id_counter += 1
        return "_id_" + str(self.id_counter)

    def store(self, obj, name=None):
        """Stores items for possible future access"""
        if name:
            name = name + self.get_new_id()
        else:
            name = self.get_new_id()
        self.invoked[name] = obj
        return obj

    def set_theme(self, theme=1):
        match theme:
            case 0:
                self.fg = 'black'
                self.bg = 'white'
                self.opacity = 1
            case 1:
                self.fg = 'lime'
                self.bg = 'black'
                self.opacity = 0.90
            case 2:
                self.fg = 'white'
                self.bg = 'black'
                self.opacity = 1
            case _:
                self.fg = 'firebrick'
                self.bg = 'black'
                self.opacity = 0.90

    def add_settings_menu(self):
        # Create a menu bar
        menubar = self.tk.Menu(self.window)
        self.window.config(menu=menubar)

        # Create a settings menu
        settings_menu = self.tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Add a theme submenu
        theme_menu = self.tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)

        # Add a General submenu
        general_menu = self.tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="General", menu=general_menu)

        return settings_menu, theme_menu, general_menu

    def large_text_dialog(self, initial_value, title="Edit Task Details:"):
        """Creates large sized text box and returns"""
        self.get_label(append_to=self.scroll_area, text=title)
        num_lines = initial_value.count('\n') + 1
        details_text = self.get_text_box(append_to=self.scroll_area, height=num_lines, width=100)
        details_text.pack()
        details_text.delete(1.0, tk.END)  # Clear existing text
        details_text.insert(tk.END, initial_value)

        return details_text
