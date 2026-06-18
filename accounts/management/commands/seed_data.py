"""
Seeds the database with demo data so graders/reviewers can explore the
API immediately without manually creating accounts through Postman.

Usage:
    python manage.py seed_data
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from departments.models import Department
from doctors.models import Doctor
from patients.models import Patient
from medicines.models import Medicine
from appointments.models import Appointment
from prescriptions.models import Prescription, PrescriptionMedicine
from billing.models import Bill

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with demo users, departments, doctors, patients, medicines, etc."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # --- Superuser / Admin -------------------------------------------------
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@hospital.com",
                password="Admin@12345",
                first_name="System",
                last_name="Admin",
                role=User.Role.ADMIN,
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin.username} / Admin@12345"))

        # --- Receptionist --------------------------------------------------------
        if not User.objects.filter(username="receptionist1").exists():
            User.objects.create_user(
                username="receptionist1",
                email="receptionist1@hospital.com",
                password="Reception@123",
                first_name="Rita",
                last_name="Receptionist",
                role=User.Role.RECEPTIONIST,
            )
            self.stdout.write(self.style.SUCCESS("Created receptionist1 / Reception@123"))

        # --- Departments -----------------------------------------------------
        dept_names = [
            ("Cardiology", "Heart and cardiovascular care"),
            ("Neurology", "Brain and nervous system care"),
            ("Orthopedics", "Bones, joints, and muscles"),
            ("Pediatrics", "Medical care for children"),
        ]
        departments = {}
        for name, desc in dept_names:
            dept, _ = Department.objects.get_or_create(name=name, defaults={"description": desc})
            departments[name] = dept
        self.stdout.write(self.style.SUCCESS(f"Departments ready: {list(departments.keys())}"))

        # --- Doctors -----------------------------------------------------------
        doctor_specs = [
            ("dr_john", "john.doe@hospital.com", "John", "Doe", "Cardiology", "Cardiologist", 10),
            ("dr_jane", "jane.smith@hospital.com", "Jane", "Smith", "Neurology", "Neurologist", 7),
        ]
        for username, email, first, last, dept_name, spec, exp in doctor_specs:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="Doctor@123",
                    first_name=first,
                    last_name=last,
                    role=User.Role.DOCTOR,
                )
                Doctor.objects.create(
                    user=user,
                    department=departments[dept_name],
                    specialization=spec,
                    phone="01700000000",
                    experience=exp,
                    is_available=True,
                )
                self.stdout.write(self.style.SUCCESS(f"Created doctor: {username} / Doctor@123"))

        # --- Patients ------------------------------------------------------------
        patient_specs = [
            ("patient_mike", "mike@example.com", "Mike", "Johnson", 34, "male", "O+"),
            ("patient_amy", "amy@example.com", "Amy", "Lee", 28, "female", "A-"),
        ]
        for username, email, first, last, age, gender, blood in patient_specs:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="Patient@123",
                    first_name=first,
                    last_name=last,
                    role=User.Role.PATIENT,
                )
                Patient.objects.create(
                    user=user,
                    age=age,
                    gender=gender,
                    blood_group=blood,
                    address="123 Demo Street, Dhaka",
                    phone="01800000000",
                )
                self.stdout.write(self.style.SUCCESS(f"Created patient: {username} / Patient@123"))

        # --- Medicines ----------------------------------------------------------
        medicine_specs = [
            ("Paracetamol", "Pain reliever and fever reducer", "tablet"),
            ("Amoxicillin", "Antibiotic", "capsule"),
            ("Cetirizine", "Antihistamine for allergies", "tablet"),
        ]
        for name, desc, unit in medicine_specs:
            Medicine.objects.get_or_create(name=name, defaults={"description": desc, "unit": unit})
        self.stdout.write(self.style.SUCCESS("Medicines ready."))

        # --- Sample appointment, prescription, bill --------------------------
        doctor = Doctor.objects.filter(user__username="dr_john").first()
        patient = Patient.objects.filter(user__username="patient_mike").first()

        if doctor and patient and not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=timezone.now() + timedelta(days=1),
                status=Appointment.Status.APPROVED,
            )
            prescription = Prescription.objects.create(
                appointment=appointment,
                diagnosis="Common cold with mild fever",
                notes="Drink plenty of fluids and rest.",
            )
            paracetamol = Medicine.objects.get(name="Paracetamol")
            PrescriptionMedicine.objects.create(
                prescription=prescription,
                medicine=paracetamol,
                dosage="500mg, twice a day",
                duration="5 days",
            )
            Bill.objects.create(patient=patient, amount=1500.00, paid=False)
            self.stdout.write(self.style.SUCCESS("Created sample appointment, prescription, and bill."))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete! Demo credentials:"))
        self.stdout.write("  Admin:        admin / Admin@12345")
        self.stdout.write("  Receptionist: receptionist1 / Reception@123")
        self.stdout.write("  Doctor:       dr_john / Doctor@123")
        self.stdout.write("  Patient:      patient_mike / Patient@123")
