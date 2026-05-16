from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import (
    Department, Event, EventRegistration, Fee, FeeAssignment, Membership,
    MembershipRequest, Notification, Organization, Payment, Program
)


User = get_user_model()


class BackendSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(name='Computer Science', initials='CS')
        self.program = Program.objects.create(name='BSCS', department=self.department)
        self.student = User.objects.create_user(
            email='student@example.com',
            password='password123',
            first_name='Student',
            last_name='One',
            program=self.program,
        )
        self.leader = User.objects.create_user(
            email='leader@example.com',
            password='password123',
            first_name='Leader',
            last_name='One',
            program=self.program,
        )
        self.other = User.objects.create_user(
            email='other@example.com',
            password='password123',
            first_name='Other',
            last_name='User',
            program=self.program,
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            first_name='Admin',
            last_name='User',
        )
        self.organization = Organization.objects.create(
            name='Coding Club',
            acronym='CC',
            leader=self.leader,
            status='active',
        )
        Membership.objects.create(
            user=self.leader,
            organization=self.organization,
            role='officer',
            position='President',
        )

    def test_registration_cannot_set_staff_flags(self):
        response = self.client.post('/api/register/', {
            'email': 'new@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'is_staff': True,
            'is_active': False,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='new@example.com')
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_non_officer_cannot_create_event(self):
        self.client.force_authenticate(self.student)
        response = self.client.post('/api/events/', {
            'organization': self.organization.id,
            'title': 'Workshop',
            'venue': 'Lab 1',
            'start_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_end_must_be_after_start(self):
        self.client.force_authenticate(self.leader)
        start_time = timezone.now() + timedelta(days=1)
        response = self.client.post('/api/events/', {
            'organization': self.organization.id,
            'title': 'Invalid Workshop',
            'venue': 'Lab 1',
            'start_time': start_time.isoformat(),
            'end_time': (start_time - timedelta(hours=1)).isoformat(),
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_membership_request_uses_authenticated_user(self):
        self.client.force_authenticate(self.student)
        response = self.client.post('/api/membership-requests/', {
            'user': self.other.id,
            'organization': self.organization.id,
            'message': 'I want to join.',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request = MembershipRequest.objects.get(organization=self.organization, user=self.student)
        self.assertEqual(request.user, self.student)

    def test_list_endpoints_are_paginated(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/organizations/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

    def test_event_registration_waitlists_when_capacity_is_full(self):
        Membership.objects.create(
            user=self.student,
            organization=self.organization,
            role='member',
        )
        Membership.objects.create(
            user=self.other,
            organization=self.organization,
            role='member',
        )
        event = Event.objects.create(
            organization=self.organization,
            title='Limited Workshop',
            venue='Lab 1',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            max_attendees=1,
        )

        self.client.force_authenticate(self.student)
        first_response = self.client.post(f'/api/events/{event.id}/register/', {}, format='json')

        self.client.force_authenticate(self.other)
        second_response = self.client.post(f'/api/events/{event.id}/register/', {}, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventRegistration.objects.get(event=event, user=self.student).status, 'registered')
        self.assertEqual(EventRegistration.objects.get(event=event, user=self.other).status, 'waitlisted')

    def test_fee_assignment_payment_and_summary_flow(self):
        Membership.objects.create(
            user=self.student,
            organization=self.organization,
            role='member',
        )
        Membership.objects.create(
            user=self.other,
            organization=self.organization,
            role='member',
        )
        self.client.force_authenticate(self.leader)
        fee_response = self.client.post('/api/fees/', {
            'organization': self.organization.id,
            'title': 'Annual Due',
            'fee_type': 'membership_due',
            'amount': '100.00',
            'status': 'open',
        }, format='json')

        self.assertEqual(fee_response.status_code, status.HTTP_201_CREATED)
        fee = Fee.objects.get(id=fee_response.data['id'])

        assign_response = self.client.post(f'/api/fees/{fee.id}/assign_members/', {}, format='json')
        self.assertEqual(assign_response.status_code, status.HTTP_200_OK)
        self.assertEqual(FeeAssignment.objects.filter(fee=fee).count(), 3)

        assignment = FeeAssignment.objects.get(fee=fee, user=self.student)
        payment_response = self.client.post('/api/payments/', {
            'assignment': assignment.id,
            'amount': '100.00',
            'payment_method': 'cash',
        }, format='json')

        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'paid')
        self.assertEqual(Payment.objects.filter(assignment=assignment).count(), 1)
        self.assertTrue(Notification.objects.filter(recipient=self.student, notification_type='payment').exists())

        summary_response = self.client.get(f'/api/fees/summary/?organization={self.organization.id}')
        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(summary_response.data['total_due']), '300.00')
        self.assertEqual(str(summary_response.data['total_paid']), '100.00')


class OrganizationConstraintTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='student1@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
        )
        self.user2 = User.objects.create_user(
            email='student2@example.com',
            password='password123',
            first_name='Jane',
            last_name='Doe',
        )

    def test_one_leader_one_org(self):
        Organization.objects.create(name='Org 1', acronym='O1', leader=self.user1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Organization.objects.create(name='Org 2', acronym='O2', leader=self.user1)

        self.assertEqual(Organization.objects.filter(leader=self.user1).count(), 1)

    def test_unique_name(self):
        Organization.objects.create(name='Unique Org', acronym='UO', leader=self.user1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Organization.objects.create(name='Unique Org', acronym='UO2', leader=self.user2)
