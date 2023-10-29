# Read data from the CSV file
import csv
from datetime import datetime

from hashtable import HashTable
from package import Package


# Loads the data from the provide csv's using the csv library
# Instantiated and called in main.py

class LoadData:
    def __init__(self):
        pass

    # Time Complexity: O(N) + O(N) + O(N) = O(N)
    # Space Complexity: O(1)
    def load_data_csv(self, distanceIndexMatch=None, distance_matrix=None, packageDataTable=None, truck1=None,
                      truck2=None, truck3=None):
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
                ID, Address, City, State, Zip, Deadline, Weight, notes = row
                key_package = ID
                Available = "8:00 AM"
                value_package = Package(ID, Address, City, State, Zip, Deadline, Weight, notes, Available)
                # manually assign packages to trucks based on predetermined method
                if ID == '25' or ID == '6' or ID == '18' or ID == '3' or ID == '36' or ID == '38' or ID == '32' or ID == '28':
                    if ID == '25' or ID == '6' or ID == '32' or ID == '28':
                        value_package.available = datetime.strptime("9:05 AM", "%I:%M %p")
                    value_package.truck = truck2
                    value_package.delivery_status = "On Truck"
                    packageDataTable[key_package] = value_package
                    truck2.packages.append(key_package)
                elif (ID == '15' or ID == '15' or ID == '14' or ID == '20' or ID == '13' or ID == '16' or ID == '29'
                      or ID == '1' or ID == '34' or ID == '31' or ID == '30' or ID == '40' or ID == '37' or ID == '19'
                      or ID == '10' or ID == '5' or ID == '8'):
                    value_package.truck = truck1
                    value_package.delivery_status = "On Truck"
                    packageDataTable[key_package] = value_package
                    truck1.packages.append(key_package)
                elif ID == '9':
                    value_package.available = datetime.strptime("10:20 AM", "%I:%M %p")
                    value_package.truck = truck3
                    value_package.delivery_status = "On Truck"
                    packageDataTable[key_package] = value_package
                    truck3.packages.append(key_package)
                else:
                    value_package.truck = truck3
                    value_package.delivery_status = "On Truck"
                    packageDataTable[key_package] = value_package
                    truck3.packages.append(key_package)
