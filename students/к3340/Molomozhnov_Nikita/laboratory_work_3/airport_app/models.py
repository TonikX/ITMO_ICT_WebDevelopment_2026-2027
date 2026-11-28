from django.db import models


class CompanyType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    company_type = models.ForeignKey(
        CompanyType, on_delete=models.CASCADE, related_name="companies"
    )

    def __str__(self):
        return self.name


class AircraftType(models.Model):
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.manufacturer} {self.model}"


class Aircraft(models.Model):
    STATUS_CHOICES = (
        ("operational", "Operational"),
        ("repair", "In repair"),
    )
    register_number = models.CharField(max_length=20)
    aircraft_type = models.ForeignKey(
        AircraftType, on_delete=models.CASCADE, related_name="aircrafts"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="aircrafts"
    )
    seats = models.IntegerField()
    speed = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="operational"
    )

    def __str__(self):
        return self.register_number


class Airport(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Route(models.Model):
    departure_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routes"
    )
    destination_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.departure_airport.city} - {self.destination_airport.city}"


class Crew(models.Model):
    name = models.CharField(max_length=50)
    employees = models.ManyToManyField(
        'Employee', through='CrewMember', related_name='crews'
    )

    def __str__(self):
        return self.name


class Employee(models.Model):
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField()
    education = models.CharField(max_length=200)
    experience_years = models.IntegerField()
    passport_data = models.CharField(max_length=100)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="employees"
    )
    employment_status = models.CharField(max_length=20, default="working")
    hire_date = models.DateField()
    fire_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.full_name


class Flight(models.Model):
    flight_number = models.CharField(max_length=20)
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    aircraft = models.ForeignKey(
        Aircraft, on_delete=models.CASCADE, related_name="flights"
    )
    crew = models.ForeignKey(
        Crew, on_delete=models.CASCADE, related_name="flights"
    )
    departure_dt = models.DateTimeField()
    arrival_dt = models.DateTimeField()
    tickets_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.flight_number


class TransitStop(models.Model):
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="transit_stops"
    )
    airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="transit_stops"
    )
    arrival_dt = models.DateTimeField()
    departure_dt = models.DateTimeField()

    def __str__(self):
        return f"{self.flight} @ {self.airport}"


class CrewMember(models.Model):
    crew = models.ForeignKey(
        Crew, on_delete=models.CASCADE, related_name="members"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="crew_memberships"
    )
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.employee} ({self.role})"


class Admission(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="admissions"
    )
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="admissions"
    )
    is_allowed = models.BooleanField(default=True)
    issue_date = models.DateField()

    def __str__(self):
        return f"{self.employee} -> {self.flight}"
