# CCube_WPB.csv_QE-mporter 
This tool lets you turn Quantum-Efficiency .csv files from WebPlotDigitizer tables into a format my plotting program can use

Installation:

To install the virtual environment, just run: WPD_csv.bat

How to Use:
1. Use WebPlotDigitizer to trace a QE graph.
2. Create one dataset for each color channel: Red, Green, Blue (you can include Monochrome too if it's there — it will be auto-detected).
3. Export all datasets into a single .csv file.
4. Run WPD_qe_csv.bat
5. Select your .csv file when prompted.
6. Enter the Camera Brand and Model.
7. The program will interpolate the data from 300–1100nm in 5nm steps, clean it up, and spit out a .tsv file in the right format.
8. Only wavelengths where at least one channel has data are kept
9. Copy + paste that file into your plotter's qe_data folder
