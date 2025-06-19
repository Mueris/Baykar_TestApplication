from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import produce_aircraft, personelScreen_page, produce_page,LoginView,PartViewSet, AircraftViewSet, TeamViewSet,PersonelViewSet,ProducedAircraftViewSet,login_page,register_page,RegisterPersonelView
from .views import dashboard,team_data,team_detail,get_aircraft_parts,get_team_parts,produce_part,ProducedAircraftViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'parts', PartViewSet)
router.register(r'aircrafts', AircraftViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'personel', PersonelViewSet)
router.register(r'produced_aircrafts', ProducedAircraftViewSet)

urlpatterns = [
    path('app/', include(router.urls)),
    path('login/', login_page),  # Manually add the login URL here
    #path('register/', register_page, name='register-page'),                 # for rendering the form
    path('produce/', produce_page, name='produce-page'), 
    path('app/personelScreen/', personelScreen_page, name='personelScreen-page'), 
    path('app/login/', LoginView.as_view(), name='login'),
    path('app/team-data/', team_data, name='team-data'),
    path('app/team/<int:pk>/', team_detail),
    path('app/aircraft/<int:pk>/parts/', get_aircraft_parts),
    path('app/produce-part/', produce_part),
    path('app/produced_aircraft/', ProducedAircraftViewSet),
    path('app/produce-aircraft/', produce_aircraft),
    path('app/team/<int:team_id>/parts/', get_team_parts),
    path('', dashboard),
    
]
