# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 18:28:32 2015

@author: z0034yaz
"""

# -*- coding: utf-8 -*-
# Find the time and value of max load for each of the regions
# COAST, EAST, FAR_WEST, NORTH, NORTH_C, SOUTHERN, SOUTH_C, WEST
# and write the result out in a csv file, using pipe character | as the delimiter.
# An example output can be seen in the "example.csv" file.

import xlrd
import os
import csv
from zipfile import ZipFile

datafile = "2013_ERCOT_Hourly_Load_Data.xls"
outfile = "2013_Max_Loads.csv"


def open_zip(datafile):
    with ZipFile('{0}.zip'.format(datafile), 'r') as myzip:
        myzip.extractall()


def parse_file(datafile):
    workbook = xlrd.open_workbook(datafile)
    sheet = workbook.sheet_by_index(0)
    stations = [sheet.cell_value(0, col) for col in range(sheet.ncols) if col > 0 and col < 9]
    
    vals = [[sheet.cell_value(row, col) for row in range(sheet.nrows) for col in range(sheet.ncols) if row > 0 and col == idx] for idx in range(1, 9)]
    max_vals = [[max(a), a.index(max(a)), stations[vals.index(a)]] for a in vals]
    max_with_time = [[m[2], m[0], xlrd.xldate_as_tuple(sheet.cell_value(m[1] + 1, 0), 0)] for m in max_vals]
    data = [[m[0], m[2][0], m[2][1], m[2][2], m[2][3], m[1]] for m in max_with_time]
 
    # YOUR CODE HERE
    # Remember that you can use xlrd.xldate_as_tuple(sometime, 0) to convert
    # Excel date to Python tuple of (year, month, day, hour, minute, second)
    return data

def save_file(data, filename):
    fieldnames = ['Station', 'Year', 'Month', 'Day', 'Hour', 'Max Load']
    with open(outfile, 'wt') as csvfile:
        w = csv.writer(csvfile, delimiter='|')
        w.writerows([fieldnames] + data)
    
    
def test():
    # open_zip(datafile)
    data = parse_file(datafile)
    save_file(data, outfile)

    number_of_rows = 0
    stations = []

    ans = {'FAR_WEST': {'Max Load': '2281.2722140000024',
                        'Year': '2013',
                        'Month': '6',
                        'Day': '26',
                        'Hour': '17'}}
    correct_stations = ['COAST', 'EAST', 'FAR_WEST', 'NORTH',
                        'NORTH_C', 'SOUTHERN', 'SOUTH_C', 'WEST']
    fields = ['Year', 'Month', 'Day', 'Hour', 'Max Load']

    with open(outfile) as of:
        csvfile = csv.DictReader(of, delimiter="|")
        for line in csvfile:
            station = line['Station']
            if station == 'FAR_WEST':
                for field in fields:
                    # Check if 'Max Load' is within .1 of answer
                    if field == 'Max Load':
                        max_answer = round(float(ans[station][field]), 1)
                        max_line = round(float(line[field]), 1)
                        assert max_answer == max_line

                    # Otherwise check for equality
                    else:
                        assert ans[station][field] == line[field]

            number_of_rows += 1
            stations.append(station)

        # Output should be 8 lines not including header
        assert number_of_rows == 8

        # Check Station Names
        assert set(stations) == set(correct_stations)

        
if __name__ == "__main__":
    test()
