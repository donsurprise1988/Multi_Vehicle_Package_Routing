# Read data from the CSV file
import csv

from package import Package


class LoadData:
    def __init__(self):
        pass
    def load_data_csv(self, distanceIndexMatch=None, distance_matrix=None, packageDataTable=None):
        with open('Distance.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header

            for row in csv_reader:
                Address, Index = row
                distanceIndexMatch.set(Address, Index)

        # Open the CSV file for reading
        with open('distance_matrix.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row

            for row in csv_reader:
                # Extract the distance values from each row and convert them to floats
                distance_values = [float(value) for value in row[2:]]
                distance_matrix.append(distance_values)

        # Read data from the package CSV file
        with open('packages.csv', 'r') as csv_file_packages:
            csv_reader_packages = csv.reader(csv_file_packages)
            next(csv_reader_packages)  # Skip the header

            for row in csv_reader_packages:
                ID, Address, City, State, Zip, Deadline, Weight, Available, notes = row
                key = ID
                value = Package(ID, Address, City, State, Zip, Deadline, Weight, notes, Available)
                packageDataTable.set(key, value)  # Store the id as the key and the package object as the value