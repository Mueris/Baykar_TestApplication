
from rest_framework import viewsets
from .models import Part, Aircraft, Team, Personel,ProducedAircrafts,AircraftParts
from .serializers import PartSerializer, AircraftSerializer, TeamSerializer, PersonelSerializer,ProducedAircraftSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.decorators import permission_classes, api_view
from datetime import date
from django.contrib.auth import authenticate, login, logout

class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer

    def get_queryset(self):
        team_name = self.request.query_params.get('team')
        queryset = super().get_queryset()

        if team_name:
            queryset = queryset.filter(team__name=team_name)

        return queryset

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        # Here we can filter or modify the queryset if needed.
        return Team.objects.all()

class PersonelViewSet(viewsets.ModelViewSet):
    queryset = Personel.objects.all()
    serializer_class = PersonelSerializer

    def get_queryset(self):
        # Return all personnel for now, can be modified with filters if needed.
        return Personel.objects.all()
class ProducedAircraftViewSet(viewsets.ModelViewSet):
    queryset = ProducedAircrafts.objects.all().order_by('-production_date')  # En son üretilen en üstte
    serializer_class = ProducedAircraftSerializer

    def get_queryset(self):
        # Optionally, add filters to limit the list (e.g., filter by production date)
        return ProducedAircrafts.objects.all()
    
class RegisterPersonelView(APIView):
    def post(self, request):
        serializer = PersonelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def produce_aircraft(request):
    aircraft_id = request.data.get('aircraft_id')

    try:
        aircraft = Aircraft.objects.get(id=aircraft_id)
    except Aircraft.DoesNotExist:
        return Response({"error": "Aircraft not found"}, status=status.HTTP_404_NOT_FOUND)

    parts_required = AircraftParts.objects.filter(aircraft=aircraft)
    
    # Stok kontrolü
    for part_link in parts_required:
        if part_link.part.stock_count < part_link.quantity:
            return Response({
                "error": f"Not enough stock for part: {part_link.part.name}"
            }, status=status.HTTP_400_BAD_REQUEST)

    # Stok azaltma
    for part_link in parts_required:
        part = part_link.part
        part.stock_count -= part_link.quantity
        part.save()

    # Yeni uçak üretimi
    produced = ProducedAircrafts.objects.create(aircraftModel=aircraft, production_date=date.today())

    return Response({
        "message": "done",
        "produced_aircraft_id": produced.id
    }, status=status.HTTP_201_CREATED)
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        return token
class LoginView(APIView):

    def post(self, request):
        per=Personel
        username = request.data.get('username')
        password = request.data.get('password')
        user = per.auth(username=username, password=password) 

        if user:
            login(request, user) 
            serializer = PersonelSerializer(user)
            return Response({"message": "Login successful","user":serializer.data})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['GET'])
def get_personel_info(request):
    user = request.user  # Automatically populated if JWT or session is used
    data = {
        "username": user.username,
        "first_name": user.first_name,
        "team": user.team.name,
        "email": user.email,
    }
    return Response(data)

    

@api_view(['GET'])
def get_team_data(request):
    user = request.user
    team = user.team
    aircrafts = Aircraft.objects.filter(team=team)
    aircraft_data = [{"id": ac.id, "name": ac.name} for ac in aircrafts]

    return Response({
        "team_name": team.name,
        "aircrafts": aircraft_data
    })


@api_view(['GET'])
def get_aircraft_parts(request, aircraft_id):
    parts = AircraftParts.objects.filter(aircraft_id=aircraft_id)
    part_data = [{"id": p.part.id, "name": p.part.name} for p in parts]
    return Response(part_data)


@api_view(['POST'])
def create_team_part(request):
    team = request.user.team
    part_id = request.data.get("part_id")
    quantity = request.data.get("quantity")

    try:
        part = Part.objects.get(id=part_id)
        part.stock_count += int(quantity)
        part.save()
        return Response({"message": "Parça başarıyla üretildi."})
    except Part.DoesNotExist:
        return Response({"error": "Parça bulunamadı."}, status=400)

@api_view(['GET'])
def team_data(request):
    user = request.user
    team = user.team

    aircrafts = Aircraft.objects.filter(team=team)
    aircraft_data = [{"id": a.id, "name": a.name} for a in aircrafts]

    return Response({
        "team_id": team.id,
        "team_name": team.name,
        "aircrafts": aircraft_data
    })
@api_view(['GET'])
def team_detail(request, pk):
    try:
        team = Team.objects.get(pk=pk)
        return Response(TeamSerializer(team).data)
    except Team.DoesNotExist:
        return Response({"error": "Team not found"}, status=404)
    
@api_view(['GET'])
def get_aircraft_parts(request, pk):
    try:
        aircraft = Aircraft.objects.get(pk=pk)
        links = AircraftParts.objects.filter(aircraft=aircraft)
        parts = [link.part for link in links]
        serializer = PartSerializer(parts, many=True)
        return Response(serializer.data)
    except Aircraft.DoesNotExist:
        return Response({"error": "Aircraft not found"}, status=404)
@api_view(['POST'])
def produce_part(request):
    part_id = request.data.get('part_id')
    quantity = int(request.data.get('quantity', 1))

    try:
        part = Part.objects.get(id=part_id)
        part.stock_count += quantity  # Sayıyı arttır
        part.save()

        return Response({"message": f"{quantity} adet {part.name} parçası üretildi."})
    except Part.DoesNotExist:
        return Response({"error": "Parça bulunamadı."}, status=404)
@api_view(['GET'])
def get_team_parts(request, team_id):
    try:
        parts = Part.objects.filter(team__id=team_id)
        serializer = PartSerializer(parts, many=True)
        return Response(serializer.data)
    except:
        return Response({"error": "Takıma ait parçalar alınamadı."}, status=404)

    
def register_page(request):
    return render(request, 'aircraft_app/register.html')

def login_page(request):
    return render(request, 'aircraft_app/login.html')

def produce_page(request):
    return render(request, 'aircraft_app/produce.html')
def personelScreen_page(request):
    return render(request, 'aircraft_app/personelScreen.html')

    
def dashboard(request):
    return render(request, 'aircraft_app/index.html')

