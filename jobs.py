# jobs.py

import csv
from nautobot.dcim.models import Location, LocationType
from nautobot.extras.models import Status
from nautobot.apps.jobs import Job, register_jobs, TextVar


LOCATION_CSV = """name,city,state
Den-DC,Denver,Colorado
SanDiego-BR,San Diego,CA
Den-BR,Denver,Colorado
Ashburn-DC,Ashburn,VA
Ashburn-BR,Ashburn,Virginia
Newark-BR,Newark,NJ
Chicago-BR,Chicago,IL
"""
state_expander = {
    "CO": "Colorado",
    "CA": "California",
    "VA": "Virginia",
    "NJ": "New Jersey",
    "IL": "Illinois",
}


class CreateLocations(Job):

    location_csv = TextVar()

    class Meta:
        name = "Create Locations"
        description = "Create locations from CSV file"
        dryrun_default = False

    def run(self, location_csv):

        active = Status.objects.get(name="Active")

        locations = csv.DictReader(location_csv.splitlines())
        location_types = {
            "Datacenter": LocationType.objects.get(name="Datacenter"),
            "Branch": LocationType.objects.get(name="Branch"),
            "City": LocationType.objects.get(name="City"),
            "State": LocationType.objects.get(name="State"),
        }
        for location in locations:
            state = state_expander.get(location["state"], location["state"])
            state_location, site_created = Location.objects.get_or_create(
                name=state,
                status=active,
                location_type=location_types["State"],
            )
            city_location, city_created = Location.objects.get_or_create(
                name=location["city"],
                status=active,
                location_type=location_types["City"],
                parent=state_location,
            )
            if location["name"].endswith("-DC"):
                site_location, site_created = Location.objects.get_or_create(
                    name=location["name"],
                    status=active,
                    location_type=location_types["Datacenter"],
                    parent=city_location,
                )
            elif location["name"].endswith("-BR"):
                site_location, site_created = Location.objects.get_or_create(
                    name=location["name"],
                    status=active,
                    location_type=location_types["Branch"],
                    parent=city_location,
                )


register_jobs(CreateLocations)
