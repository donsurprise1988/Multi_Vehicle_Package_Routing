# 010722931
import csv
from datetime import datetime, timedelta

from hashtable import HashTable
from package import Package
from truck import Truck


def print_all_rucks():
    print(f'truck: {truck1.truck_id} minutes: {truck1.minutes_traveled}')
    for item in truck1.packages:
        print(f'package: {item}')

    print(f'truck: {truck2.truck_id} minutes: {truck2.minutes_traveled}')
    for item in truck2.packages:
        print(f'package: {item}')

    print(f'truck: {truck3.truck_id} minutes: {truck3.minutes_traveled}')
    for item in truck3.packages:
        print(f'package: {item}')


def composite_key(a, b):
    return f'{a}-{b}'


def next_package(current_package_id):
    current_distance_id = 0
    index_of_current_package = distanceIndexMatch[packageDataTable[current_package_id].address]
    shortest_distance = float('inf')  # Initialize to positive infinity
    shortest_distance_package_id = None
    for key, value in packageDataTable.items():
        if key not in assigned_packages:
            index_of_next_package = distanceIndexMatch[packageDataTable[key].address]
            current_distance = distance_matrix[int(index_of_current_package)][int(index_of_next_package)]
            if current_distance <= shortest_distance and key not in assigned_packages:
                shortest_distance = current_distance
                shortest_distance_package_id = key
    return shortest_distance_package_id


def update_package(key, truck):
    assigned_packages[key] = truck
    packageDataTable[key].delivery_status = "On Truck"
    packageDataTable[key].truck = truck
    truck.packages.append(key)


def load_truck1():
    if len(truck1.packages) >= truck1.max_packages or len(assigned_packages.items()) == len(packageDataTable.items()):
        return
    else:
        for key, value in packageDataTable.items():
            if value.delivery_status == "At The Hub" and len(truck1.packages) < truck1.max_packages and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am":
                if value.notes == "Must be delivered with 13, 15" or value.notes == "Must be delivered with 15, 19":
                    update_package(key, truck1)
                elif (value.deadline != datetime.strptime("5:00 PM", "%I:%M %p")
                      and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am"):
                    update_package(key, truck1)
                elif (value.notes != "Can only be on truck 2"
                      and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am"
                      and value.notes != "Wrong address listed"):
                    if value.address in truck1.packages:
                        update_package(key, truck1)
                    elif truck1.packages and key not in assigned_packages:
                        next_package_truck1 = next_package(truck1.packages[-1])
                        if packageDataTable[next_package_truck1].delivery_status == "At The Hub":
                            update_package(next_package_truck1, truck1)


def load_truck2():
    if len(truck2.packages) >= truck2.max_packages or len(assigned_packages.items()) == len(packageDataTable.items()):
        return
    else:
        for key, value in packageDataTable.items():
            if (value.delivery_status == "At The Hub"
                    and len(truck2.packages) < truck2.max_packages and value.notes != "Wrong address listed"):
                if value.notes == "Can only be on truck 2":
                    update_package(key, truck2)
                elif value.notes == "Delayed on flight---will not arrive to depot until 9:05 am":
                    update_package(key, truck2)
                elif value.address in truck2.packages:
                    update_package(key, truck2)
                elif truck2.packages and key not in assigned_packages:
                    next_package_truck2 = next_package(truck2.packages[-1])
                    if packageDataTable[next_package_truck2].delivery_status == "At The Hub":
                        update_package(next_package_truck2, truck2)


def load_truck3():
    if len(truck3.packages) >= truck3.max_packages or len(assigned_packages.items()) == len(packageDataTable.items()):
        return
    else:
        for key, value in packageDataTable.items():
            if value.delivery_status == "At The Hub" and len(truck3.packages) < truck3.max_packages:
                if truck3.packages and key not in assigned_packages:
                    update_package(key, truck3)
                elif key not in assigned_packages and value.delivery_status == "At The Hub":
                    update_package(key, truck3)


def minutes_traveled(truck, location_id_from, location_id_to):
    from_address_id = int(location_id_from)
    to_address_id = int(location_id_to)
    distance_traveled = distance_matrix[from_address_id][to_address_id]
    minutes = distance_traveled / truck.avg_speed * 60
    truck.minutes_traveled += minutes


# iterates through truck packages to find the next shortest distance package
def deliver_next_package(truck):
    shortest_distance = float('inf')  # Initialize to positive infinity
    shortest_distance_package_id = None
    for package_id in truck.packages:
        next_location_id = distanceIndexMatch[packageDataTable[package_id].address]  #Distance Index
        distance_for_this_trip = distance_matrix[truck.current_location_id][int(next_location_id)]
        if (distance_for_this_trip < shortest_distance
                and packageDataTable[package_id].delivery_status != "Delivered"):
            shortest_distance = distance_for_this_trip
            shortest_distance_package_id = package_id
    if shortest_distance_package_id is not None:
        packageDataTable[shortest_distance_package_id].delivery_status = "Delivered"
        minutes_traveled(truck, truck.current_location_id, int(distanceIndexMatch[packageDataTable[shortest_distance_package_id].address]))
        truck.miles_traveled = truck.miles_traveled + shortest_distance
        packageDataTable[shortest_distance_package_id].time_delivered = (
                datetime.strptime("8:00 AM", "%I:%M %p") + timedelta(minutes=truck.minutes_traveled)
        )
        truck.current_location_id = int(distanceIndexMatch[packageDataTable[shortest_distance_package_id].address])
        return shortest_distance_package_id


def delivery_route(truck):
    for item in truck.packages:
        deliver_next_package(truck)


# set global variable for the maximum travel distance allowed and the number of packages that need to be delivered
max_mileage = 140
goal_packages_delivered = 40

# created a list of packages that have to be delivered together based on the requirements
packages_delivered_together = ['13', '14', '15', '16', '19', '20']

# create hashtable for storing the distance between addresses. Create it with 702 records so that the table is O(1)
distanceDataTable = HashTable(702)

# create hashtable for storing the packages. Since it is known that there are 40 packages, the table will be created
# with 40 records so that it's O(1)
packageDataTable = HashTable(40)

# Create Index hash table for addresses to use for lookups
distanceIndexMatch = HashTable(27)

# Hash table to keep track of the packages that get assigned
assigned_packages = HashTable(40)

# Create an empty list to store the distance matrix
distance_matrix = []

# Instantiate the three trucks. Assign the two drivers to truck 1 and truck 2
truck1 = Truck(1, "A")
truck2 = Truck(2, "B")
truck3 = Truck(3, None)

# Read data from the CSV file
with open('Distance.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header

    for row in csv_reader:
        Address1, City1, State1, Zip1, Address2, City2, State2, Zip2, distance, Index1, Index2 = row
        composite_key_reader = composite_key(Index1, Index2)  # create composite key to use as key for hashtable
        distance = float(distance)  # Convert distance to a float
        distanceDataTable.set(composite_key_reader,
                              distance)  # Store the distance in the hash table using the composite key
        if Address2 not in distanceIndexMatch:
            distanceIndexMatch.set(Address2, Index2)

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

for _ in packageDataTable:
    load_truck1()
    load_truck2()
    load_truck3()
delivery_route(truck1)
delivery_route(truck2)
delivery_route(truck3)

with open('output2.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    # Define the header row with attribute names
    header = ["package_id", "address", "city", "state", "zip", "deadline", "weight", "notes", "available",
              "delivery_status", "truck"]
    writer.writerow(header)

    # Iterate through the objects in your HashTable
    for key, package in packageDataTable.items():
        # Extract the attributes you want to write
        truck_id = package.truck.truck_id if package.truck else None  # Get the truck_id or None if there's no truck
        row_data = [
            package.package_id,
            package.address,
            package.city,
            package.state,
            package.zip,
            package.deadline.strftime("%I:%M %p"),
            package.weight,
            package.notes,
            package.available.strftime("%I:%M %p"),
            package.delivery_status,
            truck_id
        ]

        # Write the data for the current package
        writer.writerow(row_data)

print("Truck 1 Info:")
print(f"Number of items in the truck1.packages list: {len(truck1.packages)} minutes: {truck1.minutes_traveled} miles: {truck1.miles_traveled}")
for items in truck1.packages:
    print(f'package info: {items} id: {packageDataTable[items].delivery_status} time: {packageDataTable[items].time_delivered.strftime("%I:%M %p")}')

print("Truck 2 Info:")
print(f"Number of items in the truck2.packages list: {len(truck2.packages)} minutes: {truck2.minutes_traveled} miles: {truck2.miles_traveled}")
for items in truck2.packages:
    print(f'package info: {items} id: {packageDataTable[items].delivery_status}')

print("Truck 3 Info:")
print(f"Number of items in the truck3.packages list: {len(truck3.packages)} minutes: {truck3.minutes_traveled} miles: {truck3.miles_traveled}")
for items in truck3.packages:
    print(f'package info: {items} id: {packageDataTable[items].delivery_status}')

