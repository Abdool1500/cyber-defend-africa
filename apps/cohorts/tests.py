from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User

from .models import Cohort, CohortMembership


class CohortMembershipModelTests(TestCase):
    def test_cannot_add_same_student_to_cohort_twice(self):
        student = User.objects.create_user(
            email="cohortstudent@example.com", password="pass1234", full_name="Cohort Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        cohort = Cohort.objects.create(name="January 2026")
        CohortMembership.objects.create(cohort=cohort, student=student)
        with self.assertRaises(Exception):
            CohortMembership.objects.create(cohort=cohort, student=student)

    def test_student_can_belong_to_multiple_cohorts(self):
        student = User.objects.create_user(
            email="multicohort@example.com", password="pass1234", full_name="Multi Cohort",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        cohort1 = Cohort.objects.create(name="January 2026")
        cohort2 = Cohort.objects.create(name="Women in Cybersecurity")
        CohortMembership.objects.create(cohort=cohort1, student=student)
        CohortMembership.objects.create(cohort=cohort2, student=student)  # should not raise
        self.assertEqual(student.cohort_memberships.count(), 2)


class CohortManagementViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="cohortadmin@example.com", password="pass1234", full_name="Cohort Admin",
            role=User.Role.ADMIN, status=User.Status.ACTIVE, is_staff=True,
        )
        self.student = User.objects.create_user(
            email="cohortstudent2@example.com", password="pass1234", full_name="Cohort Student 2",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.cohort = Cohort.objects.create(name="March 2026")
        CohortMembership.objects.create(cohort=self.cohort, student=self.student)
        self.client.login(username="cohortadmin@example.com", password="pass1234")

    def test_cohort_list_shows_computed_stats(self):
        response = self.client.get(reverse("management_cohorts:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "March 2026")
        self.assertContains(response, "1")  # member_count

    def test_cohort_detail_shows_members(self):
        response = self.client.get(reverse("management_cohorts:detail", args=[self.cohort.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cohort Student 2")
        self.assertContains(response, "cohortstudent2@example.com")

    def test_student_cannot_access_cohort_management(self):
        self.client.logout()
        self.client.login(username="cohortstudent2@example.com", password="pass1234")
        response = self.client.get(reverse("management_cohorts:list"))
        self.assertEqual(response.status_code, 403)

    def test_instructor_cannot_access_cohort_management(self):
        instructor = User.objects.create_user(
            email="cohortinstructor@example.com", password="pass1234", full_name="Cohort Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.client.logout()
        self.client.login(username="cohortinstructor@example.com", password="pass1234")
        response = self.client.get(reverse("management_cohorts:list"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("management_cohorts:list"))
        self.assertEqual(response.status_code, 302)


class CohortAPITests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="cohortapiadmin@example.com", password="pass1234", full_name="Cohort API Admin",
            role=User.Role.ADMIN, status=User.Status.ACTIVE, is_staff=True,
        )
        self.student = User.objects.create_user(
            email="cohortapistudent@example.com", password="pass1234", full_name="Cohort API Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.cohort = Cohort.objects.create(name="API Test Cohort")
        CohortMembership.objects.create(cohort=self.cohort, student=self.student)

    def test_admin_can_list_cohorts_with_nested_stats(self):
        self.client.login(username="cohortapiadmin@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-cohort-list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        cohort_row = next(r for r in data["results"] if r["name"] == "API Test Cohort")
        self.assertEqual(cohort_row["stats"]["member_count"], 1)

    def test_student_cannot_access_cohort_api(self):
        self.client.login(username="cohortapistudent@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-cohort-list"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_access_cohort_api(self):
        response = self.client.get(reverse("api-v1:api-cohort-list"))
        self.assertEqual(response.status_code, 403)
