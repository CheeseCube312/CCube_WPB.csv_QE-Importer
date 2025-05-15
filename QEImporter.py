import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os

def process_qe_csv():
    root = tk.Tk()
    root.withdraw()

    # Step 1: Select CSV file
    csv_path = filedialog.askopenfilename(
        title="Select QE CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not csv_path:
        messagebox.showinfo("Cancelled", "No file selected.")
        return

    # Step 2: Prompt for metadata
    brand = simpledialog.askstring("Camera Brand", "Enter Camera Brand:")
    model = simpledialog.askstring("Camera Model", "Enter Camera Model:")
    if not brand or not model:
        messagebox.showerror("Missing Info", "Brand and Model must be provided.")
        return

    try:
        # Step 3: Read CSV with no header; first 2 rows are headers
        df_raw = pd.read_csv(csv_path, header=None)

        if df_raw.shape[0] < 3:
            raise ValueError("File must contain at least 3 rows (2 headers + data).")

        # Fill missing colors (assume alternating X/Y)
        color_row = df_raw.iloc[0].copy()
        color_row = color_row.fillna(method='ffill')
        color_row = color_row.astype(str).str.strip()

        axis_row = df_raw.iloc[1].astype(str).str.strip().str.upper()

        new_columns = []
        for color, axis in zip(color_row, axis_row):
            if axis in {"X", "Y"}:
                new_columns.append((color, axis))
            else:
                new_columns.append(None)

        df = df_raw.iloc[2:].copy()
        df.columns = new_columns
        df = df.loc[:, df.columns.notnull()]

        # Identify valid channels
        all_columns = df.columns.tolist()
        channels = sorted(set(color for color, axis in all_columns if axis in {'X', 'Y'}))

        required_channels = {"Red", "Green", "Blue"}
        if not required_channels.issubset(set(channels)):
            messagebox.showerror("Missing Channels", f"CSV must contain Red, Green, and Blue data. Found: {channels}")
            return

        # Step 4: Interpolate each channel
        wl_target = np.arange(300, 1101, 5)
        results = {}

        for channel in channels:
            try:
                x = df[(channel, "X")].astype(float).values
                y = df[(channel, "Y")].astype(float).values
                interp = interp1d(x, y, kind='linear', bounds_error=False, fill_value=0.0)
                y_interp = np.clip(np.round(interp(wl_target), 3), 0.0, None)
                results[channel] = y_interp
            except Exception as e:
                print(f"Skipping channel {channel}: {e}")

        if not results:
            raise ValueError("No valid QE data could be interpolated. Check that X/Y data is numeric and aligned.")

        # Step 5: Combine into dataframe and clean
        out_df = pd.DataFrame(results, index=wl_target).T  # Channels x Wavelength
        out_df.columns.name = "Wavelength (nm)"
        out_df.index.name = "Channel"

        # Drop wavelengths where all values are zero
        out_df = out_df.loc[:, ~(out_df == 0).all(axis=0)]

        # Add brand/model metadata
        out_df.insert(0, "Camera Brand", brand)
        out_df.insert(1, "Camera Model", model)

        # Step 6: Save output
        output_filename = f"QE_{brand}_{model}.tsv".replace(" ", "_")
        out_df.to_csv(output_filename, sep='\t')
        messagebox.showinfo("Success", f"Interpolated QE data saved to:\n{output_filename}")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

if __name__ == "__main__":
    process_qe_csv()
