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
    debug = True
    location_csv = TextVar()

    class Meta:
        name = "Create Locations"
        description = "Create locations from CSV file"
        dryrun_default = False

    def run(self, location_csv):

        active = Status.objects.get(name="Active")

        locations = csv.DictReader(location_csv.splitlines())
        try:
            LocationType.objects.get(name="Datacenter")
        except LocationType.DoesNotExist:
            self.logger.failure("Datacenter location type does not exist")
        try:
            LocationType.objects.get(name="Branch")
        except LocationType.DoesNotExist:
            self.logger.failure("Branch location type does not exist")
        try:
            LocationType.objects.get(name="City")
        except LocationType.DoesNotExist:
            self.logger.failure("City location type does not exist")
        try:
            LocationType.objects.get(name="State")
        except LocationType.DoesNotExist:
            self.logger.failure("State location type does not exist")
        try:
            LocationType.objects.get(name="Site")
        except LocationType.DoesNotExist:
            self.logger.failure("Site location type does not exist")

        for location in locations:
            state = state_expander.get(location["state"], location["state"])
            state_location, state_created = Location.objects.get_or_create(
                name=state,
                status=active,
                location_type=LocationType.objects.get(name="State"),
            )
            city_location, city_created = Location.objects.get_or_create(
                name=location["city"],
                status=active,
                location_type=LocationType.objects.get(name="City"),
                parent=state_location,
            )
            site_location, site_created = Location.objects.get_or_create(
                name=location["city"],
                status=active,
                location_type=LocationType.objects.get(name="Site"),
                parent=city_location,
            )
            if location["name"].endswith("-DC"):
                datacenter_location, datacenter_created = (
                    Location.objects.get_or_create(
                        name=location["name"],
                        status=active,
                        location_type=LocationType.objects.get(name="Datacenter"),
                        parent=site_location,
                    )
                )
            elif location["name"].endswith("-BR"):
                branch_location, branch_created = Location.objects.get_or_create(
                    name=location["name"],
                    status=active,
                    location_type=LocationType.objects.get(name="Branch"),
                    parent=site_location,
                )


register_jobs(CreateLocations)
