from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# PartType model to store the type of each part (e.g., Wing, Body)
class PartType(models.Model):
    name = models.CharField(max_length=100)  # Part type (e.g., Wing, Body)

    def __str__(self):
        return self.name

# Part model to store each specific part (e.g., TB2 Wing)
class Part(models.Model):
    part_type = models.ForeignKey(PartType, on_delete=models.CASCADE)  # Type of part (e.g., Wing, Body)
    name = models.CharField(max_length=100)  # Name of the part (e.g., TB2 Wing)
    stock_count = models.IntegerField(default=0)  # How many units are available
    is_stock_available = models.BooleanField(default=False)  # Whether stock is available for this part

    def save(self, *args, **kwargs):
        # Update the is_stock_available field based on stock_count
        self.is_stock_available = self.stock_count > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Aircraft model to store different types of planes
class Aircraft(models.Model):
    name = models.CharField(max_length=100)  # Aircraft model name (e.g., TB2, TB3, AKINCI)
    
    def __str__(self):
        return self.name

# AircraftParts model to link Parts with Aircraft and keep track of quantity
class AircraftParts(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name='aircraft_parts')  # Aircraft
    part = models.ForeignKey(Part, on_delete=models.CASCADE)  # Part
    quantity = models.IntegerField(default=0)  # Quantity of this part in the aircraft

    class Meta:
        unique_together = ('aircraft', 'part')  # Ensures one part can only be associated once per aircraft

    def __str__(self):
        return f'{self.aircraft.name} - {self.part.name} ({self.quantity})'
    

class ProducedAircrafts(models.Model):
    # ForeignKey to Aircraft model (linking each produced aircraft to a specific aircraft model)
    aircraftModel = models.ForeignKey('Aircraft', on_delete=models.CASCADE, related_name='produced_aircrafts')  
    production_date = models.DateField()  # Track production date for each instance of the aircraft
    # No need for quantity, as each row represents one produced aircraft

    def __str__(self):
        return f"{self.aircraftModel.name} produced on {self.production_date}"


# Team model to store teams related to parts
class Team(models.Model):
    name = models.CharField(max_length=100)
    parts = models.ManyToManyField(Part)

    def __str__(self):
        return self.name
    
# Custom User Manager for creating users
class PersonelManager(BaseUserManager):
    def create_user(self,username, first_name,last_name, email, password=None, team=None):
        if not username:
            raise ValueError('The username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, first_name=first_name, last_name=last_name, email=email, team=team)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

# Personel model with custom user management
class Personel(AbstractBaseUser):
    username=models.CharField(max_length=100,unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    #password = models.CharField(max_length=128)  # Password is automatically hashed
    team = models.ForeignKey(Team, related_name='personnel', on_delete=models.CASCADE)  # One-to-many relationship (many personnel can belong to one team)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = PersonelManager()  # Link to the custom user manager

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'team']  # Team is now required when creating a user

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
    def auth(username,password):
        try:
            user = Personel.objects.get(username=username)
            if password=='123':
                return user
            else:
                return None
        except Personel.DoesNotExist:
            return None
