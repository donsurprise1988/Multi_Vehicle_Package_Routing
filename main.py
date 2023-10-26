# 010722931
from datetime import datetime, timedelta

from hashtable import HashTable
from load_data_from_csv import LoadData
from save_to_csv import SaveData
from truck import Truck


# The greedy function is used in the loading functions for each truck
# The function takes in the current package id and uses that to find the next optimal package based on the distance
# Package ID parameter is compared to all packages in the package hash table that have not yet been assigned to a truck
# Uses the distance matrix to look-up the distances between the packages
# return the package id of the next shortest distance package
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


# The function is used to update the package information when it is loaded on a truck
# Function is used in the load truck functions for each truck, everytime a package is selected to be loaded
def update_package(key, truck):
    assigned_packages[key] = truck  # adds the package id to the assigned_packages list
    packageDataTable[key].delivery_status = "On Truck"  # changes the package delivery status to "On Truck"
    packageDataTable[key].truck = truck  # assigns the truck to the package object on the package hash table
    truck.packages.append(key)  # adds the package id to the Truck objects packages list


# Function to load packages on Truck 1 based on the requirements from the WGUPS package file
# Truck 1 should include packages that can leave at 8AM and that must be delivered together and exclude truck 2 packages
# After including all those packages, it then uses the next_package function to pick the next greedy package to include
def load_truck1():
    if len(truck1.packages) >= truck1.max_packages or len(assigned_packages.items()) == len(packageDataTable.items()):
        return  # Terminates recursion if the truck package limit has been reached or if all packages have been assigned
    else:
        for key, value in packageDataTable.items():  # iterates through the Package id and objects
            if (value.delivery_status == "At The Hub"  # Filter for only packages that are At The Hub
                    and len(truck1.packages) < truck1.max_packages  # packages in truck must be lower than max allowed
                    # I did not want delayed packages to be included. I want truck 1 to leave at 8AM
                    and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am"):
                if value.notes == "Must be delivered with 13, 15" or value.notes == "Must be delivered with 15, 19":
                    update_package(key, truck1)  # loads packages that should be delivered together
                elif (value.deadline != datetime.strptime("5:00 PM", "%I:%M %p")
                      and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am"):
                    update_package(key, truck1)  # loads packages that are available at 8AM
                elif (value.notes != "Can only be on truck 2"
                      and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am"
                      and value.notes != "Wrong address listed"):
                    if value.address in truck1.packages:
                        # loads other packages that are not for truck 2, not delayed, or don't have wrong address
                        update_package(key, truck1)
                    elif truck1.packages and key not in assigned_packages:
                        next_package_truck1 = next_package(truck1.packages[-1])
                        if (packageDataTable[next_package_truck1].delivery_status == "At The Hub"
                                and value.notes != "Delayed on flight---will not arrive to depot until 9:05 am"):
                            # after loaded the preferred packages above
                            # it then uses the next closes package to load next package
                            update_package(next_package_truck1, truck1)


# Function to load packages on Truck 2 based on the requirements from the WGUPS package file
# Truck 2 should include packages that are delayed, must be on truck 2, but don't have the wrong address
# After including all those packages, it then uses the next_package function to pick the next greedy package to include
def load_truck2():
    if len(truck2.packages) >= truck2.max_packages or len(assigned_packages.items()) == len(packageDataTable.items()):
        return
    else:
        update_package('32', truck2) # include package 32 manually in truck 2
        for key, value in packageDataTable.items():  # iterates through the Package id and objects
            if (value.delivery_status == "At The Hub"  # Filter for only packages that are At The Hub
                    and len(truck2.packages) < truck2.max_packages # packages in truck must be lower than max allowed
                    and value.notes != "Wrong address listed"): # packages can't have wrong address
                if value.notes == "Can only be on truck 2":
                    update_package(key, truck2)  # load packages that are for truck 2
                elif value.notes == "Delayed on flight---will not arrive to depot until 9:05 am":
                    update_package(key, truck2)  # load packages that are delayed
                elif value.address in truck2.packages:
                    update_package(key, truck2)  # load packages that share the same address as those already loaded
                elif truck2.packages and key not in assigned_packages:
                    next_package_truck2 = next_package(truck2.packages[-1])
                    if packageDataTable[next_package_truck2].delivery_status == "At The Hub":
                        # after loaded the preferred packages above
                        # it then uses the next closes package to load next package
                        update_package(next_package_truck2, truck2)


# Function to load packages on Truck 3 based on the requirements from the WGUPS package file
# Truck 3 should include the rest of the available packages
def load_truck3():
    if len(truck3.packages) >= truck3.max_packages or len(assigned_packages.items()) == len(packageDataTable.items()):
        return
    else:
        for key, value in packageDataTable.items():  # iterates through the Package id and objects
            # filters for packages that are still unloaded and to make sure max capacity is not reached
            if value.delivery_status == "At The Hub" and len(truck3.packages) <= truck3.max_packages:
                if truck3.packages and key not in assigned_packages:
                    update_package(key, truck3)
                elif key not in assigned_packages and value.delivery_status == "At The Hub":
                    update_package(key, truck3)


# Function to calculate minutes traveled by using the truck object, and the indexes of the two location points
# The function is used in the deliver_next_package function
def minutes_traveled(truck, location_id_from, location_id_to):
    from_address_id = int(location_id_from)
    to_address_id = int(location_id_to)
    distance_traveled = distance_matrix[from_address_id][to_address_id]
    minutes = distance_traveled / truck.avg_speed * 60  # minutes are calculated using distance traveled and truck speed
    truck.minutes_traveled += minutes  # minutes are added to the truck objects minutes attribute


# Greedy algorithm that iterates through truck object packages to find the next shortest distance package to deliver
# it uses the truck object to look at the packages that are on the truck, filter out packages that are already delivered
# it uses the distance_matrix to find the distance and compare it to the other distances
# Once the shrotest distance has been found, it marks the package as delivered, calculates the time traveled for truck,
# updates the time pakage was delivered in the Package object in the packages hash table and returns the id of the pckg
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
                truck.start_delivery_time + timedelta(minutes=truck.minutes_traveled)
        )
        truck.current_location_id = int(distanceIndexMatch[packageDataTable[shortest_distance_package_id].address])
        return shortest_distance_package_id

# Function to set delivery start time based on the latest time that a package on the truck becomes available
# It's used by the delivery_route function to set the start time for the deliveries
def start_delivery_route(truck):
    start_route_time = datetime.strptime("8:00 AM", "%I:%M %p")
    for item in truck.packages:
        # Iterates through Truck packages to find the latest time a package is available
        if packageDataTable[item].available > start_route_time:
            start_route_time = packageDataTable[item].available
    truck.start_delivery_time = start_route_time


# Uses the start delivery route function to set the start time for the delivery
# iterates through Packages on the truck to deliver the packages based on the deliver_next_package algorithm
def delivery_route(truck):
    start_delivery_route(truck)
    for item in truck.packages:
        deliver_next_package(truck)


# Function to change trucks since there are only two drivers and packages are loaded on all three trucks
# It takes the truck that is returning and the truck being activated
def change_trucks(truck_current, truck_next):
    truck_current_last_package_delivered = '0'
    latest_delivery_time = datetime.strptime("8:00 AM", "%I:%M %p")
    for item in truck_current.packages:  # Iterates through current truck packages to find last delivery time
        if packageDataTable[item].time_delivered > latest_delivery_time:
            latest_delivery_time = packageDataTable[item].time_delivered
            truck_current_last_package_delivered = item
    # After finding the last item to be delivered, it then gets the distance between the last item delivered and the HUB
    truck_current_return_minutes = \
        distance_matrix[int(distanceIndexMatch[packageDataTable[truck_current_last_package_delivered].address])][0]
    # Then computes the minutes traveled to return to HUB
    truck_current_return_minutes = truck_current_return_minutes / truck_current.avg_speed * 60
    # Then adds the minutes to the time the last package was delivered to find the time the truck arrives at HUB
    truck_current_return_time = latest_delivery_time + timedelta(minutes=truck_current_return_minutes)
    # Checks if the earliest that the next truck can start delivering is before the current truck arrives
    if truck_next.start_delivery_time < truck_current_return_time:
        # If it is, it then sets the earliest that the next start can deliver to the time that the current truck arrives
        truck_next.start_delivery_time = truck_current_return_time
        truck_next.driver = truck_current.driver # sets the driver to the new truck
    # If not, it keeps the time the same and just sets the driver
    else:
        truck_next.driver = truck_current.driver


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

# Loads the csv data for packages and distances
data_loader = LoadData()
data_loader.load_data_csv(distanceIndexMatch, distance_matrix, packageDataTable)

load_truck1()
delivery_route(truck1)
load_truck2()
delivery_route(truck2)
change_trucks(truck1, truck3)
load_truck3()
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

for key, value in packageDataTable.items():
    if key is not None:
        print(
            f'truck: {value.truck.truck_id} package info: {key} status: {value.delivery_status} time: {value.time_delivered.strftime("%I:%M %p")}')
