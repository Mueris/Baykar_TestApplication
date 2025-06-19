from rest_framework import serializers
from .models import Part, Aircraft, Team,Personel,AircraftParts,ProducedAircrafts

class PartSerializer(serializers.ModelSerializer):
    part_type = serializers.StringRelatedField()  # We are showing the name of the PartType

    class Meta:
        model = Part
        fields = ['id', 'name', 'part_type', 'stock_count', 'is_stock_available']

class AircraftPartsSerializer(serializers.ModelSerializer):
    aircraft_name = serializers.CharField(source='aircraft.name')  # Accessing aircraft name through the ForeignKey
    part = PartSerializer()  # Nested serializer to show part details

    class Meta:
        model = AircraftParts
        fields = ['id', 'aircraft_name', 'part', 'quantity']

class AircraftSerializer(serializers.ModelSerializer):
    aircraft_parts = AircraftPartsSerializer(many=True)  # Including all parts associated with the aircraft

    class Meta:
        model = Aircraft
        fields = ['id', 'name', 'aircraft_parts']

class TeamSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'parts']

class PersonelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=False)  # Removed write_only

    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())

    class Meta:
        model = Personel
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'team', 'is_active', 'is_admin']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        personel = Personel(**validated_data)
        if password:
            personel.set_password(password)
        personel.save()
        return personel


    

class ProducedAircraftSerializer(serializers.ModelSerializer):
    aircraftModel = AircraftSerializer(read_only=True)

    class Meta:
        model = ProducedAircrafts
        fields = ['id', 'aircraftModel', 'production_date']
