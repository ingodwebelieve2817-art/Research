from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from customers.models import Customer
from projects.models import Project
from services.models import ServiceProvider, Review

User = get_user_model()


class ReviewAndRatingTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user_p1 = User.objects.create_user(username="p1@test.com", email="p1@test.com")
        self.user_p2 = User.objects.create_user(username="p2@test.com", email="p2@test.com")

        # Create providers
        self.provider1 = ServiceProvider.objects.create(
            user=self.user_p1,
            business_name="Super Plumber",
            category="plumber",
            city="Lagos",
            whatsapp_number="123456789"
        )
        self.provider2 = ServiceProvider.objects.create(
            user=self.user_p2,
            business_name="Expert Barber",
            category="barber",
            city="Lagos",
            whatsapp_number="987654321"
        )

        # Create customers
        self.customer1 = Customer.objects.create(name="Customer One", phone="0801111", city="Lagos")
        self.customer2 = Customer.objects.create(name="Customer Two", phone="0802222", city="Lagos")

        # Create projects
        self.proj_completed = Project.objects.create(
            provider=self.provider1,
            customer=self.customer1,
            name="Leak repair",
            status="completed"
        )
        self.proj_pending = Project.objects.create(
            provider=self.provider1,
            customer=self.customer1,
            name="Pipe installation",
            status="pending"
        )
        self.proj_provider2 = Project.objects.create(
            provider=self.provider2,
            customer=self.customer2,
            name="Haircut styling",
            status="completed"
        )

    def test_review_creation_flow(self):
        # 1. Accessing review submission page for completed project
        url = reverse("services:submit_review", args=[self.proj_completed.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 2. Accessing review submission for pending project should redirect
        url_pending = reverse("services:submit_review", args=[self.proj_pending.pk])
        res_pending = self.client.get(url_pending)
        self.assertEqual(res_pending.status_code, 302)

        # 3. Submit valid review
        post_data = {"rating": 5, "comment": "Amazing work!"}
        res_post = self.client.post(url, post_data)
        self.assertEqual(res_post.status_code, 302)
        
        # Verify Review is saved
        review = Review.objects.get(project=self.proj_completed)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Amazing work!")
        self.assertEqual(review.provider, self.provider1)
        self.assertEqual(review.customer, self.customer1)

        # 4. Duplicate submission for same project should redirect/fail
        res_dup = self.client.post(url, {"rating": 4, "comment": "Not double-counted"})
        self.assertEqual(res_dup.status_code, 302)
        self.assertEqual(Review.objects.filter(project=self.proj_completed).count(), 1)

    def test_rating_annotation_and_filtering(self):
        # Submit reviews for provider1
        Review.objects.create(
            provider=self.provider1, customer=self.customer1, project=self.proj_completed, rating=4, comment="Good"
        )
        # Create a new completed project for self.customer2 & review provider1 again
        proj_extra = Project.objects.create(
            provider=self.provider1, customer=self.customer2, name="Extra Fix", status="completed"
        )
        Review.objects.create(
            provider=self.provider1, customer=self.customer2, project=proj_extra, rating=5, comment="Excellent"
        )

        # Submit review for provider2
        Review.objects.create(
            provider=self.provider2, customer=self.customer2, project=self.proj_provider2, rating=2, comment="Fair"
        )

        # 1. Search & Rating annotation check
        url = reverse("services:provider_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        providers = list(res.context["providers"])
        p1_item = next(p for p in providers if p.pk == self.provider1.pk)
        p2_item = next(p for p in providers if p.pk == self.provider2.pk)

        # Average rating calculations
        self.assertEqual(p1_item.avg_rating, 4.5)  # (4 + 5) / 2
        self.assertEqual(p1_item.num_reviews, 2)
        self.assertEqual(p2_item.avg_rating, 2.0)
        self.assertEqual(p2_item.num_reviews, 1)

        # 2. Filter by minimum rating
        res_filter = self.client.get(url, {"min_rating": "4.0"})
        providers_filtered = list(res_filter.context["providers"])
        self.assertIn(p1_item, providers_filtered)
        self.assertNotIn(p2_item, providers_filtered)

        # 3. Sort by highest rated
        res_sort = self.client.get(url, {"sort_by": "highest_rated"})
        providers_sorted = list(res_sort.context["providers"])
        self.assertEqual(providers_sorted[0].pk, self.provider1.pk)
        self.assertEqual(providers_sorted[1].pk, self.provider2.pk)
