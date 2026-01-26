import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from workers.models import WorkerProfile
from users.models import User
from faker import Faker

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_worker_profiles():
    fake = Faker()
    users = []
    for _ in range(100):
        user = User.objects.create_user(
            username=fake.user_name(),
            password='testpassword'
        )
        users.append(user)
        WorkerProfile.objects.create(
            user=user,
            full_name=fake.name(),
            age=fake.random_int(min=18, max=60),
            region_of_origin=fake.city(),
            current_location=fake.city(),
            years_experience=fake.random_int(min=0, max=20),
            education_level='secondary',
            skills=[fake.word() for _ in range(3)],
            languages=[fake.language_name()]
        )
    return users

@pytest.mark.django_db
def test_advanced_worker_search_benchmark(benchmark, api_client, create_worker_profiles):
    user = create_worker_profiles[0]
    api_client.force_authenticate(user=user)
    
    def search():
        api_client.get(reverse('advanced_worker_search'))
        
    benchmark(search)
