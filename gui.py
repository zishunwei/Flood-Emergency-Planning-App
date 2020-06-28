import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

from t1_user_input import check_coordinate, coordinate_transform
from t2_highest_point import identify_highest_point
from t3_nearest_itn import get_nearest_itn_node
from t4_shortest_path import shortest_path
from t5_map_plotting import map_plot


def get_input_gui(input_crs, x_entry, y_entry):
    """Get user's location input from GUI and check the validity of coordinates.
    when coordinates are legal then return a coordinate pair in CRS of British National Grid, otherwise, return None.

    :param input_crs: string
    :param x_entry: instance of entry widget
    :param y_entry: instance of entry widget
    :return: tuple(x, y) or None
    """
    user_location = (float(x_entry.get()), float(y_entry.get()))
    user_location = coordinate_transform(input_crs, user_location)
    if check_coordinate(user_location):
        print("This coordinate is valid!")
        return user_location
    else:
        print("This coordinate is invalid! quit this application...")
        return None


def run(input_crs, x_entry, y_entry, clip_mode, pb_window, progress_bar, progress_var):
    """This is the main body of software which combine tasks together and can be called by click the button.
    The progress of running the program can be shown by the progress bar.

    :param input_crs: tkinter::StringVar
    :param x_entry: instance of entry widget
    :param y_entry: instance of entry widget
    :param clip_mode: tkinter::StringVar
    :param pb_window: tkinter::Toplevel
    :param progress_bar: instance of progressbar widget
    :param progress_var: tkinter::StringVar
    :return:
    """
    # Show progress window
    pb_window.update()
    pb_window.deiconify()

    # Get the location from entry box
    print("Get user's input...")
    progress_bar['value'] = 0
    progress_var.set("(1/5) Get user's input...")
    progress_bar.update()
    user_location = get_input_gui(input_crs.get(), x_entry, y_entry)
    if user_location is None:
        tkinter.messagebox.showwarning(title='Warning',
                                       message='Please input valid coordinates on the Isle of Wight '
                                               'and click run button again')
        return

    # Identify the highest point within a 5km radius from the user location
    print('Identifying the highest point...')
    progress_bar['value'] = 1
    progress_var.set("(2/5) Identifying the highest point...")
    progress_bar.update()
    radius = 5000
    result = identify_highest_point(user_location, radius)
    highest_point = [result[0], result[1]]
    local_elevation_array = result[2]
    out_transform = result[3]

    # Identify the nearest ITN node to the user and the nearest ITN node to the highest point
    print('Identifying the nearest ITN node...')
    progress_bar['value'] = 2
    progress_var.set("(3/5) Identifying the nearest ITN node...")
    progress_bar.update()

    start_node = get_nearest_itn_node(user_location)
    end_node = get_nearest_itn_node(highest_point)

    # Identify the shortest path
    print('Identifying the shortest path...')
    progress_bar['value'] = 3
    progress_var.set("(4/5) Identifying the shortest path...")
    progress_bar.update()
    path = shortest_path(start_node, end_node)

    # Plot a map
    print('Drawing the map...')
    progress_bar['value'] = 5
    progress_var.set("(5/5) Drawing the map...")
    progress_bar.update()
    map_plot(user_location, highest_point, path, local_elevation_array, out_transform, clip_mode.get())
    pb_window.withdraw()


def change_input_crs(input_crs, x_label, y_label):
    """Change the label when user switch crs of input.

    :param input_crs: tkinter::StringVar
    :param x_label: instance of Label widget
    :param y_label: instance of Label widget
    :return:
    """
    if input_crs.get() == 'WGS84':
        x_label.config(text='Latitude:')
        y_label.config(text='Longitude:')
    elif input_crs.get() == 'BNG':
        x_label.config(text='X(Easting):')
        y_label.config(text='Y(Northing):')


def init_gui():
    """Construct and initialize the body of GUI
    """
    print('Initialize gui')
    # Create main window
    window = tk.Tk()
    window.title('Flood Emergency Planning')
    window.geometry('680x330+580+330')

    # Variable for widgets'use
    input_crs = tk.StringVar()
    clip_mode = tk.IntVar()

    # Create widgets
    # Label
    input_label = tk.Label(window, text='Please input your location:', anchor='w',
                           font=('Arial', 11), width=30, height=2)
    x_label = tk.Label(window, text='X(Easting):', anchor='e',
                       font=('Arial', 11), width=20, height=2)
    y_label = tk.Label(window, text='Y(Northing):', anchor='e',
                       font=('Arial', 11), width=20, height=1)
    crs_label = tk.Label(window, text='Choose the CRS of input:', anchor='w',
                         font=('Arial', 11), width=20, height=3)
    clip_label = tk.Label(window, text='Map clipping option:', anchor='w',
                          font=('Arial', 11), width=20, height=1)
    # Entry
    x_entry = tk.Entry(window, width=30, font=('Arial', 11))
    y_entry = tk.Entry(window, width=30, font=('Arial', 11))
    x_entry.insert(index=0, string='439619')
    y_entry.insert(index=0, string='85800')

    # Button
    run_button = tk.Button(window, text='Run', font=('Arial', 11), width=30, height=2,
                           command=lambda: run(input_crs, x_entry, y_entry, clip_mode,
                                               pb_window, progress_bar, progress_var))

    # Radio
    crs_bng_radio = tk.Radiobutton(window, text='British National Grid', font=('Arial', 11),
                                   variable=input_crs, value='BNG', width=15, height=2,
                                   command=lambda: change_input_crs(input_crs, x_label, y_label))
    crs_wgs84_radio = tk.Radiobutton(window, text='WGS84', font=('Arial', 11),
                                     variable=input_crs, value='WGS84', width=15, height=2,
                                     command=lambda: change_input_crs(input_crs, x_label, y_label))
    crs_bng_radio.select()    # Default selection

    # Checkbutton
    map_clip_check = tk.Checkbutton(window, text='Clip the map by the range of background', font=('Arial', 11),
                                    height=1, variable=clip_mode, onvalue=1, offvalue=0)

    # Create Progressbar and label in a new window
    pb_window = tk.Toplevel(window)
    pb_window.geometry('470x100+700+450')
    pb_window.title('Running progress')
    progress_var = tk.StringVar()  # The variable used by label
    progress_label = tk.Label(pb_window, textvariable=progress_var, anchor='w',
                              font=('Arial', 10), width=30, height=2)
    progress_bar = ttk.Progressbar(pb_window, orient="horizontal", length=400, mode="determinate")
    progress_bar['maximum'] = 5
    progress_bar['value'] = 0
    progress_label.grid(row=1, sticky='W', padx=30)
    progress_bar.grid(row=2, sticky='W', padx=30)
    pb_window.withdraw()  # Hide the progress window

    # Place widgets by grids in main window
    # Row 1
    input_label.grid(row=1, column=1, columnspan=2, sticky='W', padx=30)
    # Row 2
    x_label.grid(row=2, column=1, padx=30)
    x_entry.grid(row=2, column=2, columnspan=2, sticky='W')
    # Row 3
    y_label.grid(row=3, column=1, padx=30)
    y_entry.grid(row=3, column=2, columnspan=2, sticky='W')
    # Row 4
    crs_label.grid(row=4, column=1)
    crs_bng_radio.grid(row=4, column=2, sticky='W')
    crs_wgs84_radio.grid(row=4, column=3, sticky='W')
    # Row 5
    clip_label.grid(row=5, column=1)
    map_clip_check.grid(row=5, column=2, columnspan=2, sticky='W')
    # Row 6
    run_button.grid(row=6, column=1, columnspan=3, pady=20)

    return window
