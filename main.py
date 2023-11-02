# 010722931
from datetime import datetime, timedelta
import re

from hashtable import HashTable
from load_data_from_csv import LoadData
from save_to_csv import SaveData
from truck import Truck


# Function to calculate minutes traveled by using the truck object, and the distance location graph
# The function is used in the deliver_next_package function
# Time complexity O(1)
# Space complexity O(1)
def minutes_traveled(truck, location_id_from, location_id_to):
    from_address_id = int(location_id_from)
    to_address_id = int(location_id_to)
    distance_traveled = distance_matrix[from_address_id][to_address_id]
    minutes = distance_traveled / truck.avg_speed * 60  # minutes are calculated using distance traveled and truck speed
    truck.minutes_traveled += minutes  # minutes are added to the truck objects minutes attribute


# Update package and truck info when it's delivered
# Calls minutes_traveled to update the time and uses distance location graph for distance
# Time complexity O(1)
# Space complexity O(1)
def update_delivered_package(package_id, truck, shortest_distance):
    packageDataTable[package_id].delivery_status = "Delivered"
    minutes_traveled(truck, truck.current_location_id, int(distanceIndexMatch[packageDataTable[package_id].address]))
    truck.miles_traveled = truck.miles_traveled + shortest_distance
    packageDataTable[package_id].time_delivered = truck.start_delivery_time + timedelta(minutes=truck.minutes_traveled)
    truck.current_location_id = int(distanceIndexMatch[packageDataTable[package_id].address])


# The main goal of this function is to find the next package for delivery based on proximity.
# Greedy algorithm that iterates through the list of truck object packages
# it uses the truck object to look at the packages that are on the truck, filter out packages that are already delivered
# it uses the distance_matrix graph to find the distance and compare it to the other distances
# Once the shortest distance has been found, it marks the package as delivered, calculates the time traveled for truck,
# updates the time package was delivered in the Package object in the packages hash table
# Time complexity O(N)
# Space complexity O(1)
def shortest_path_algorithm(truck):
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
        update_delivered_package(shortest_distance_package_id, truck, shortest_distance)


# Function to find the earliest time that a truck can start delivering packages
# ime based on the latest time that a package on the truck becomes available
# It's used by the delivery_route function to set the start time for the deliveries
# Time complexity O(N)
# Space complexity O(1)
def start_delivery_route(truck):
    start_route_time = datetime.strptime("8:00 AM", "%I:%M %p")
    for item in truck.packages:
        # Iterates through Truck packages to find the latest time a package is available
        if packageDataTable[item].available > start_route_time:
            start_route_time = packageDataTable[item].available
    truck.start_delivery_time = start_route_time


# Sets the delivery start time and the delivers the packages for the truck
# uses the start_delivery_route to set the initial delivery start time for a truck.
# Then, it iterates through the packages on the truck and uses shortest_path_algorithm to deliver the packages.
# This ensures that packages are delivered based on the nearest neighbor approach and
# Time complexity O(N^2) since it calls the start_delivery_route(truck) function which is O(N)
# Space complexity O(1)
def delivery_route(truck):
    start_delivery_route(truck)
    for item in truck.packages:
        shortest_path_algorithm(truck)


# Function to change trucks since there are only two drivers and packages are loaded on all three trucks
# Responsible for managing the transition of packages and responsibilities from the current truck to the next truck.
# It ensures that packages are delivered efficiently and takes into account the availability of the next truck
#  and the time needed for the current truck to return to the hub.
# Time complexity O(N)
# Space complexity O(1)
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
        truck_next.driver = truck_current.driver  # sets the driver to the new truck
    # If not, it keeps the time the same and just sets the driver
    else:
        truck_next.driver = truck_current.driver


# This function calculates the time when a truck returns to the hub.
# It calculates the distance traveled to the hub from the current location of the truck using the distance_matrix.
# The time taken to return to the hub is calculated based on the distance traveled and the truck's average speed.
# The total time is calculated by adding the time already spent on the road (truck.minutes_traveled) to the return time.
# Time complexity O(1)
# Space complexity O(1)
def return_to_hub(truck):
    distance_traveled_to_hub = distance_matrix[int(truck.current_location_id)][0]
    # minutes are calculated using distance traveled and truck speed
    minutes_to_hub = distance_traveled_to_hub / truck.avg_speed * 60
    total_minutes = truck.minutes_traveled + minutes_to_hub
    time_returned = truck.start_delivery_time + timedelta(minutes=total_minutes)
    return f"{time_returned.strftime("%I:%M %p")}"


# This function calculates the total distance traveled by a given truck by using the truck's miles traveled and adding
# the distances it takes for the truck to travel back from the last delivered package
# Time complexity O(1)
# Space complexity O(1)
def total_distance_traveled(truck):
    current_distance = truck.miles_traveled
    distance_traveled_to_hub = distance_matrix[int(truck.current_location_id)][0]
    return current_distance + distance_traveled_to_hub


# Displays the mileage by truck and total mileage for all trucks
# Time complexity O(1)
# Space complexity O(1)
def display_total_mileage():
    truck1_distance = round(total_distance_traveled(truck1), 2)
    truck2_distance = round(total_distance_traveled(truck2), 2)
    truck3_distance = round(total_distance_traveled(truck3), 2)
    total_distance = truck1_distance + truck2_distance + truck3_distance
    if total_distance < 140:
        print(f"\nTruck 1 has finished its route and returned to the hub at {return_to_hub(truck1)} with a total distance "
              f"traveled of {round(truck1_distance, 2)} miles")
        print(f"Truck 2 has finished its route and returned to the hub at {return_to_hub(truck2)} with a total distance "
              f"traveled of {round(truck2_distance, 2)} miles")
        print(f"Truck 3 has finished its route and returned to the hub at {return_to_hub(truck3)} with a total distance "
              f"traveled of {round(truck3_distance, 2)} miles")
        print(
            f"Total Distance Traveled for all Trucks: {round(total_distance, 2)} miles")
    else:
        # check to make sure total distance meets requirements
        print(f"Total distance of {total_distance} is greater thatn the 140 mile requirement!!!")


# Updates Package 9 information with the correct address information
# It's used in the display package status function to update the info if time constraint is met
# Time complexity O(1)
# Space complexity O(1)
def update_package_9():
    packageDataTable['9'].address = "410 S.StateSt."
    packageDataTable['9'].city = "Salt Lake City"
    packageDataTable['9'].state = "UT"
    packageDataTable['9'].zip = "84111"


# Function displays information about a single package by taking in the time and pakcage id as input
# compares the time entered by the user with the packages time of delivery and displays information based on this
# It updates package 9 if the user time is 10:20 AM or later
# It's used in the display package status for all packages function and in the menu function
# Time complexity O(1)
# Space complexity O(1)
def display_package_status(time_in, selected_package_id):
    id = selected_package_id
    time_input = datetime.strptime(time_in, "%I:%M %p")
    status = None
    truck = packageDataTable[selected_package_id].truck.truck_id
    if time_input >= datetime.strptime("10:20 AM", "%I:%M %p"):
        # update package 9 with correct address
        update_package_9()
    if time_input >= packageDataTable[id].time_delivered:
        status = "Delivered"
    elif ((truck == 1 and truck1.start_delivery_time < time_input)
          or (truck == 2 and truck2.start_delivery_time < time_input)
          or (truck == 3 and truck3.start_delivery_time < time_input)):
        status = "En Route"
    else:
        status = "At The Hub"
    if status == "Delivered":
        print(f"{packageDataTable[id].lookup_package()} {status} at {packageDataTable[id].time_delivered.strftime("%I:%M %p")} "
              f"on Truck {packageDataTable[id].truck.truck_id}")
    elif status == "En Route":
        print(f"{packageDataTable[id].lookup_package()} {status} as of {time_input.strftime("%I:%M %p")}"
              f" on Truck {packageDataTable[id].truck.truck_id}")
    else:
        print(f"{packageDataTable[id].lookup_package()} {status} as of {time_input.strftime("%I:%M %p")}")


# Look-up function displays information on all packages on all trucks by taking the truck and time as input
# use the display_package_status function above to display package information as it iterates through all packages
# Time complexity O(N)
# Space complexity O(1)
def display_package_status_for_all_packages(time_in):
    time_input = datetime.strptime(time_in, "%I:%M %p")
    print(f"\nInformation for ALL packages as of {time_input.strftime("%I:%M %p")}")
    for key, value in packageDataTable.items():
        display_package_status(time_in, key)


# Provide an intuitive interface for the user to view the delivery status (including the delivery time) of any package
# at any time and the total mileage traveled by all trucks. (The delivery status reports the package as
# at the hub, en route, or delivered. Delivery status must include the time.)
# The function continues to loop until it is exited by user
# Time complexity - difficult to determine due to user input and recursive nature of the menu
# Space complexity O(1)
def menu():
    time_input = None
    selected_package_id = None
    # Prints all the total distance traveled for all trucks
    # check to make sure all packages are delivered within deadline requirements
    for key, value in packageDataTable.items():
        if value.deadline != "EOD" and value.deadline < value.time_delivered:
            print(f"Package {key} is late!!! Deadline was {value.deadline} delivered at {value.time_delivered}")
    display_total_mileage()
    while True:
        print("\nMenu")
        print("1. View Package Delivery Status for a Specific Package or All Packages")
        print("2. View Total Mileage Traveled by All Trucks")
        print("3. Exit")
        menu_choice = input("\nPlease enter your choice as 1, 2, or 3:")
        if menu_choice == "1":
            while True:
                time_input = input("Please enter a time in the following format \"HH:MM AM\" or \"HH:MM PM\":")
                # Use regular expression to validate the input
                if re.match(r'^\d{1,2}:\d{2} (AM|PM)$', time_input):
                    try:
                        # Parse the input into a datetime object
                        time = datetime.strptime(time_input, "%I:%M %p")
                        break
                    except ValueError:
                        print("Invalid time format. Please try again.")
                else:
                    print("Invalid time format. Please use \"HH:MM AM\" or \"HH:MM PM\" format.")
            while True:
                print("\nPackage Delivery Status Menu")
                print("1. View Package Delivery Status for a single package")
                print("2. View Package Delivery Status for ALL Packages")
                print("3. Return to Main Menu")
                sub_menu_choice = input("\nPlease enter your choice as 1, 2, or 3:")
                if sub_menu_choice == "1":
                    selected_package_id = str(input("Please enter the package id:"))
                    if packageDataTable[selected_package_id] is not None:
                        print(f"\nInformation regarding your selected package as of "
                              f"{datetime.strptime(time_input, "%I:%M %p").strftime("%I:%M %p")}:")
                        display_package_status(time_input, selected_package_id)
                    else:
                        print("Package id doesn't exists. Please try again")
                elif sub_menu_choice == '2':
                    display_package_status_for_all_packages(time_input)
                elif sub_menu_choice == "3":
                    break  # Return to main menu
                else:
                    print("Invalid choice. Please enter your choice as 1, 2, or 3.")
        elif menu_choice == "2":
            display_total_mileage()
        elif menu_choice == "3":
            print("Exiting the program.")
            exit()
        else:
            print("Invalid choice. Please enter your choice as 1, 2, or 3.")


# create hashtable for storing the packages
packageDataTable = HashTable(101)

# Create Index hash table for addresses to use for lookups
distanceIndexMatch = HashTable(1)

# Create an empty list to store the distance matrix
distance_matrix = []

# Create a hash table to store the packages remaining at the hub.
# Will be used for reporting package information at specific times
packages_remaining_at_the_hub = HashTable(40)

# Instantiate the three trucks. Assign the two drivers to truck 1 and truck 2
truck1 = Truck(1, "A")
truck2 = Truck(2, "B")
truck3 = Truck(3, None)

# Loads the csv data for packages and distances
data_loader = LoadData()
data_loader.load_data_csv(distanceIndexMatch, distance_matrix, packageDataTable, truck1, truck2, truck3)

# The program starts by calling the delivery function for Truck 1 and 2, changing trucks, and then deliverying truck3
delivery_route(truck1)
delivery_route(truck2)
change_trucks(truck1, truck3)
delivery_route(truck3)
menu()
