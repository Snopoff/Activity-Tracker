'''
@Author: Paul Snopov
@Date: 26.08.2019

Activity Tracker

#TODO:
    - Get Chrome Tab name
    - Summarize daily data and plot it using plt.pie
'''

import subprocess as sp
import datetime as dt
import csv
import os.path as op
import re


def get_window_name(title):
    """Returns correct name of window"""
    pattern = r"b'(?P<title>.*)\\n'"  # pattern for searching the correct title
    correct_title = re.search(pattern, title).group(
        'title').split(' - ')
    name = correct_title[-1]  # get the name of app
    return re.sub(pattern, name, title)


def get_active_tab_name(title):
    """Return correct name of tab that is active in Google Chrome"""


def get_active_window_title():  # command is xdotool getwindowfocus getwindowname
    """Returns current active window."""
    command = "xdotool getwindowfocus getwindowname"
    title = sp.check_output(command.split())
    if 'Google Chrome' in title.__str__():  # if Google Chrome is opened
        return get_active_tab_name(title.__str__())
    else:
        return get_window_name(title.__str__())


def write_CSV(current_window, current_time):
    """Write information about window and time in CSV file."""
    file_name = current_time.date().__str__() + ".csv"  # path to file
    info = [current_window.__str__(), current_time.__str__()
            ]  # information to write

    if op.isfile(file_name):  # if file exists
        with open(file_name, "a") as f:
            writer = csv.writer(f)
            writer.writerow(info)
    else:
        with open(file_name, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["window", "start_time"])


if __name__ == "__main__":
    current_window = None
    while True:
        new_window = get_active_window_title()  # get new active window
        if new_window != current_window:  # if it differs of the current one
            current_window = new_window  # assign new current window
            current_time = dt.datetime.now()  # get current time
            write_CSV(current_window, current_time)
