"""
@author Martin Bienert
@date 21.08.2024

Created and tested with python 3.10
"""


# Libraries for data handling
import spc_spectra as spc
import pandas as pd

# Libraries for user interaction
from tkinter.filedialog import askopenfilenames, askopenfilename, askdirectory
from tkinter import Tk

# Libraries for path operations and control flow
import sys
import os

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")


# --------------------- #
# START USER SETTINGS   #
# May be modified       #
# --------------------- #
X_COLUMN_NAME = "x"

# True -> Only one file can be loaded; False -> Multiple files can be loaded
LOAD_SINGLE = True

# True -> One output-file per input-file; False -> Each subtime will be exported to individual output-file
TO_SINGLE = False
# ----------------- #
# END USER SETTINGS #
# ----------------- #


# ----------------- #
# USER INTERACTIONS #
# ----------------- #
def get_files() -> list[str]:
    root = Tk()
    _, filenames = askopenfilenames(title="Select spc files", filetypes=(("SPC files", "*.spc"), ))
    root.destroy()

    return filenames


def get_file() -> list[str]:
    root = Tk()
    filename = askopenfilename(title="Select spc file", filetypes=(("SPC files", "*.spc"), ))
    root.destroy()

    return [filename]


def get_target_dir() -> str:
    root = Tk()
    out_dir = askdirectory(title="Select output directory")
    root.destroy()

    return out_dir


# -------- #
# FILE I/O #
# -------- #
def read_spc(filename: str) -> pd.DataFrame:
    out = pd.DataFrame()

    f = spc.File(filename)  # Read file

    # Handle different data formats
    if f.dat_fmt.endswith('-xy'):
        for s in f.sub:
            x = s.x
            y = s.y

            out[X_COLUMN_NAME] = x
            out[str(round(s.subtime))] = y
    else:
        for s in f.sub:
            x = f.x
            y = s.y

            out[X_COLUMN_NAME] = x
            out[str(round(s.subtime))] = y

    return out


def load_file(filename: str) -> pd.DataFrame:
    print(f"Reading file {os.path.basename(filename)}")

    return read_spc(filename)


def export_csv_single(x: pd.Series, data: pd.Series, filename: str, out_dir: str) -> None:
    out_data = pd.DataFrame([x, data])

    # Construct output filename: Append subtime of current y-Dataset to filename and update file extension to ".csv"
    out_filename = os.path.join(
        out_dir,
        os.path.splitext(os.path.basename(filename))[0] + f"_{data.name}.csv"
    )

    print(f"Writing dataset {data.name} of {os.path.basename(filename)} to {os.path.basename(out_filename)}")

    # Transpose the dataframe and export it to csv format without index and header
    out_data = out_data.T
    out_data.to_csv(out_filename, index=False, header=False)


def export_csv_all(data: pd.DataFrame, filename: str, out_dir: str) -> None:
    out_filename = os.path.join(
        out_dir,
        os.path.splitext(os.path.basename(filename))[0] + f".csv"
    )

    print(f"Writing dataset {os.path.basename(filename)} to {os.path.basename(out_filename)}")

    # Export the dataframe to csv format without index and header
    data.to_csv(out_filename, index=False, header=False)


# --------------- #
# FILE PROCESSING #
# --------------- #
def process_files(filenames: list[str]) -> None:
    # Abort if no files selected
    if not filenames:
        print("No files selected. Aborting...")
        sys.exit(1)

    # Request output directory from user
    out_dir = get_target_dir()

    for filename in filenames:
        data = load_file(filename)

        if TO_SINGLE:
            # Export all subtimes to single csv file
            export_csv_all(data, filename, out_dir)
        else:
            # Export each subtime to individual csv file
            x_column = data[X_COLUMN_NAME]  # Save x-column

            # Iterate over all subtime-columns
            for y_column_name in data.columns[1:]:
                y_column = data[y_column_name]  # Get data for current subtime
                export_csv_single(x_column, y_column, filename, out_dir)  # Run export routine


# ---------------- #
# PROGRAM MAINLOOP #
# ---------------- #

def main():
    # Request file(s) from user
    if LOAD_SINGLE:
        filenames = get_file()
    else:
        filenames = get_files()

    process_files(filenames)


if __name__ == '__main__':
    main()
