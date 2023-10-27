import csv


class SaveData:
    def __init__(self):
        pass

    def output_to_csv(self, packageDataTable=None):
        with open('output.csv', mode='w', newline='') as file:
            writer = csv.writer(file)

            # Define the header row with attribute names
            header = ["package_id", "address", "city", "state", "zip", "deadline", "weight", "notes", "available",
                      "delivery_status", "delivery_time", "truck", "truck_start_delivery_time"]
            writer.writerow(header)

            # Iterate through the objects in your HashTable
            for key, package in packageDataTable.items():
                # Extract the attributes you want to write
                truck_id = package.truck.truck_id if package.truck else None  # Get the truck_id or None if there's no truck
                truck_start_delivery_time = package.truck.start_delivery_time if package.truck else None
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
                    package.time_delivered,
                    truck_id,
                    truck_start_delivery_time
                ]

                # Write the data for the current package
                writer.writerow(row_data)
