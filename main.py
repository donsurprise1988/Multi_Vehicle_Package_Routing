# 010722931
from datetime import datetime, timedelta

from hashtable import HashTable
from load_data_from_csv import LoadData
from package import Package
from save_to_csv import SaveData
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
            if value.delivery_status == "At The Hub" and len(
                    truck1.packages) < truck1.max_packages and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am":
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
            if value.delivery_status == "At The Hub" and len(truck3.packages) <= truck3.max_packages:
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
        next_location_id = distanceIndexMatch[packageDataTable[package_id].address]  # Distance Index
        distance_for_this_trip = distance_matrix[truck.current_location_id][int(next_location_id)]
        if (distance_for_this_trip < shortest_distance
                and packageDataTable[package_id].delivery_status != "Delivered"):
            shortest_distance = distance_for_this_trip
            shortest_distance_package_id = package_id
    if shortest_distance_package_id is not None:
        packageDataTable[shortest_distance_package_id].delivery_status = "Delivered"
        minutes_traveled(truck, truck.current_location_id,
                         int(distanceIndexMatch[packageDataTable[shortest_distance_package_id].address]))
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

data_loader = LoadData()
data_loader.load_data_csv(distanceIndexMatch, distance_matrix, packageDataTable)

for _ in packageDataTable:
    load_truck1()
    load_truck2()
    load_truck3()
delivery_route(truck1)
delivery_route(truck2)
delivery_route(truck3)

data_saver = SaveData()
data_saver.output_to_csv(packageDataTable)

print("Truck 1 Info:")
print(
    f"Number of items in the truck1.packages list: {len(truck1.packages)} minutes: {truck1.minutes_traveled} miles: {truck1.miles_traveled}")
for items in truck1.packages:
    print(
        f'package info: {items} id: {packageDataTable[items].delivery_status} time: {packageDataTable[items].time_delivered.strftime("%I:%M %p")}')

print("Truck 2 Info:")
print(
    f"Number of items in the truck2.packages list: {len(truck2.packages)} minutes: {truck2.minutes_traveled} miles: {truck2.miles_traveled}")
for items in truck2.packages:
    print(f'package info: {items} id: {packageDataTable[items].delivery_status}')

print("Truck 3 Info:")
print(
    f"Number of items in the truck3.packages list: {len(truck3.packages)} minutes: {truck3.minutes_traveled} miles: {truck3.miles_traveled}")
for items in truck3.packages:
    print(f'package info: {items} id: {packageDataTable[items].delivery_status}')
