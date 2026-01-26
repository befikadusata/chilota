from django.core.management.base import BaseCommand
from workers.models import WorkerProfile
from faker import Faker

class Command(BaseCommand):
    help = 'Anonymizes worker profile data for analytics and testing.'

    def handle(self, *args, **kwargs):
        fake = Faker()
        profiles = WorkerProfile.objects.all()
        for profile in profiles:
            profile.full_name = fake.name()
            profile.fayda_id = fake.ssn()
            profile.place_of_birth = fake.city()
            profile.emergency_contact_name = fake.name()
            profile.emergency_contact_phone = fake.phone_number()
            profile.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully anonymized {len(profiles)} worker profiles.'))