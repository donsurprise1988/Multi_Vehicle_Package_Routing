from datetime import datetime

import hashtable

from hashtable import HashTable


# Class for the Truck object to keep track of the driver, max packages, average speed, minutes traveled,
# and hash table of packages on the truck
class Truck:
    def __init__(self, truck_id, driver, max_packages=16, avg_speed=18, minutes_traveled=0, current_location_id=0,
                 miles_traveled=0, start_delivery_time=datetime.strptime("8:00 AM", "%I:%M %p")):
        self.truck_id = truck_id
        self.driver = driver
        self.max_packages = max_packages
        self.avg_speed = avg_speed
        self.minutes_traveled = minutes_traveled
        self.packages = []
        self.current_location_id = current_location_id
        self.miles_traveled = miles_traveled
        self.start_delivery_time = start_delivery_time

