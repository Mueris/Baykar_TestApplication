from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class ProductionConfig(AppConfig):
    name = 'production'

    def ready(self):
        # Importing models inside the ready method to avoid circular import issues
        from .models import Part, Aircraft, Team, AircraftParts, PartType
        
        # Connect the load_initial_data function to post_migrate signal
        post_migrate.connect(load_initial_data, sender=self)

# This function will run after migrations are applied to ensure the fixed data exists
def load_initial_data(sender, **kwargs):
    # Importing models inside the function to avoid circular imports
    from .models import Part, Aircraft, Team, AircraftParts, PartType,Personel

    # Aircraft data
    aircraft_names = ["TB2", "TB3", "AKINCI", "KIZILELMA"]
    parts_names = ["Kanat", "Gövde", "Kuyruk", "Aviyonik"]
    stock_count = 1  # Default stock count for each part (You can adjust this value)
    quantity_per_aircraft = 1  # Default quantity of parts needed for each aircraft

    # Create PartTypes if they don't exist
    part_types = {}
    part_type_names = ["Kanat", "Gövde", "Kuyruk", "Aviyonik"]
    
    for part_type_name in part_type_names:
        part_types[part_type_name] = PartType.objects.get_or_create(name=part_type_name)[0]

    # Create Aircrafts if they don't exist
    aircrafts = {}
    for aircraft_name in aircraft_names:
        aircrafts[aircraft_name], created = Aircraft.objects.get_or_create(name=aircraft_name)
        
        # Create Parts for each aircraft if not exist
        for part_name in parts_names:
            part_type = part_types.get(part_name)  # Get the corresponding PartType for the part
            part = Part.objects.get_or_create(
                name=f"{aircraft_name} {part_name}",
                part_type=part_type,
                stock_count=stock_count,  # Set initial stock count
            )[0]
            
            # Associate the part with the aircraft and set the quantity
            AircraftParts.objects.get_or_create(
                aircraft=aircrafts[aircraft_name],
                part=part,
                quantity=quantity_per_aircraft
            )

        # Create Teams
    team_names = ["Kanat Takımı", "Gövde Takımı", "Kuyruk Takımı", "Aviyonik Takımı", "Montaj Takımı"]
    team_objects = {}
    for name in team_names:
        team, _ = Team.objects.get_or_create(name=name)
        team_objects[name] = team

    
    for index, (team_name, team) in enumerate(team_objects.items(), start=1):
        username = f"user{index}"
        email = f"user{index}@example.com"
        if not Personel.objects.filter(username=username).exists():
            Personel.objects.create_user(
                username=username,
                first_name=f"{team_name.split()[0]}",
                last_name="Personel",
                email=email,
                password="123",  
                team=team
            )
