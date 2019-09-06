'''
@Author: Paul Snopov
@Date: 26.08.2019

Activity Tracker

# TODO:
    - Format plotting
    - Use telegram bot to send plots
'''

import subprocess as sp
import datetime as dt
import csv
import os.path as op
import re
from time import sleep
import pandas as pd


def get_window_name(title):
    """Returns correct name of window"""
    pattern = r"b'(?P<title>.*)\\n'"  # pattern for searching the correct title
    correct_title = re.search(pattern, title).group(
        'title').split(' - ')
    name = correct_title[-1]  # get the name of app
    return re.sub(pattern, name, title)


def get_active_tab_name(title):
    """Return correct name of tab that is active in Google Chrome"""
    pattern = r"b'(?P<title>.*)\\n'"  # pattern for searching the correct title

    try:
        correct_title = re.search(pattern, title).group(
            'title').split(' - ')  # if there's a backslash -- remove it
    except AttributeError:
        print("Error happened with this title:\n{}".format(title))
        name = title

    try:  # try get 3rd element from the end
        name = "'{name}' on {resourse}".format(
            name=correct_title[-3], resourse=correct_title[-2])
    except IndexError:
        name = correct_title[-2]

    # in case there are substrs like '\xd8'
    # it still can have symbols like '/' or '"'
    name = re.sub(r"[^a-zA-Z0-9_ ]", "", re.sub(
        r"\\x([a-z]|\d){2}", '', name))
    name = "Website" if name.isspace() else name
    return re.sub(pattern, name, title)


def get_active_window_title():  # command is xdotool getwindowfocus getwindowname
    """Returns current active window."""
    command = "xdotool getwindowfocus getwindowname"
    title = sp.check_output(command.split()).__str__()
    if 'Google Chrome' in title:  # if Google Chrome is opened
        return get_active_tab_name(title)
    else:
        return get_window_name(title)


def write_CSV(current_window, current_time):
    """Write information about window and time in CSV file."""
    file_name = "Data/" + current_time.date().__str__() + ".csv"  # path to file
    info = [current_window.__str__(), current_time.time().replace(microsecond=0).__str__()
            ]  # information to write

    if op.isfile(file_name):  # if file exists
        with open(file_name, "a") as f:
            writer = csv.writer(f)
            writer.writerow(info)
    else:
        with open(file_name, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["window", "start_time"])


def plot_activity(file_name):
    """Plot daily activity"""
    df = pd.read_csv("Data/"+file_name+".csv")
    df = df[df.window != 'Untitled']
    time = []
    for i in range(len(df)-1):
        # str to datetime object
        end = dt.datetime.strptime(df.iloc[i+1].loc['start_time'], '%H:%M:%S')
        start = dt.datetime.strptime(df.iloc[i].loc['start_time'], '%H:%M:%S')
        # get timedelta and append it to the list
        time.append((end - start).total_seconds())
    # get the timedelta of last activity
    time.append((dt.datetime.strptime('23:59:59', '%H:%M:%S') -
                 dt.datetime.strptime(df.iloc[-1].loc['start_time'], '%H:%M:%S')).total_seconds())

    df = pd.concat([df, pd.Series(time, name='spent_time')],
                   axis=1, join='inner')  # add 'time' list to dataframe
    # delete 'start_time' column
    df.drop(['start_time'], axis=1, inplace=True)
    df.index = df['window']  # set index as 'window' due to plotting
    fig = df.plot.pie(y='spent_time', legend=False,  # get figure
                      label="").get_figure()  # label = "" in order to remove column name
    pict_name = 'Plots/' + file_name + ".pdf"
    fig.savefig(pict_name)  # save it


if __name__ == "__main__":
    current_window = None
    while True:
        new_window = get_active_window_title()  # get new active window
        new_time = dt.datetime.now()  # get current time
        if new_window != current_window:  # if it differs of the current one
            current_window = new_window  # assign new current window
            current_time = new_time
            write_CSV(current_window, current_time)
        if current_time.date() != new_time.date():  # if a new day started
            # plot prev day activity
            plot_activity(current_time.date().__str__())

        sleep(0.2)
