# jobs.py

import csv
from nautobot.dcim.models import Location
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
        for location in locations:
            if len(location["state"]) == 2:
                state = state_expander[location["state"]]
            else:
                state = location["state"]
            Location.objects.create(
                name=location["name"],
                city=location["city"],
                state=state,
                status=active,
            )


register_jobs(CreateLocations)
