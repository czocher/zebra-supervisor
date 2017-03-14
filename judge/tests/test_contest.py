# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from django.test import TestCase, override_settings

from django.utils import timezone

from judge.models import Contest

from guardian.shortcuts import assign_perm


class ContestTestCase(TestCase):

    def setUp(self):
        self.yesterday = timezone.now() - timezone.timedelta(days=1)
        self.now = timezone.now()
        self.in_two_hours = timezone.now() + timezone.timedelta(hours=2)
        self.tomorrow = timezone.now() + timezone.timedelta(days=1)

    def test_not_started(self):
        """Contests which are not started have the right properties."""

        contest = Contest(
            name="Test contest",
            start_time=self.in_two_hours,
            freeze_time=self.tomorrow,
            end_time=self.tomorrow
        )

        self.assertFalse(contest.is_active)
        self.assertFalse(contest.is_finished)
        self.assertFalse(contest.is_started)
        contest.clean()
        contest.save()

    def test_started(self):
        """Contests which are started have the right properties."""

        contest = Contest(
            name="Test contest",
            start_time=self.yesterday,
            freeze_time=self.tomorrow,
            end_time=self.tomorrow
        )

        self.assertTrue(contest.is_active)
        self.assertFalse(contest.is_finished)
        self.assertTrue(contest.is_started)
        contest.clean()
        contest.save()

    def test_finished(self):
        """Contests which are finished have the right properties."""

        contest = Contest(
            name="Test contest",
            start_time=self.yesterday,
            freeze_time=self.yesterday,
            end_time=self.yesterday
        )

        self.assertFalse(contest.is_active)
        self.assertTrue(contest.is_finished)
        self.assertTrue(contest.is_started)
        contest.clean()
        contest.save()

    def test_before_freeze(self):
        """Contests should not be freezed before the given freeze time."""

        contest = Contest(
            name="Test contest",
            start_time=self.yesterday,
            freeze_time=self.tomorrow,
            end_time=self.tomorrow
        )

        self.assertFalse(contest.is_freezed)
        contest.clean()
        contest.save()

    def test_after_freeze(self):
        """Contests should be freezed after the given freeze time."""

        contest = Contest(
            name="Test contest",
            start_time=self.yesterday,
            freeze_time=self.yesterday,
            end_time=self.tomorrow
        )

        self.assertTrue(contest.is_freezed)
        contest.clean()
        contest.save()

    def test_construction_start_after_end(self):
        """Contests can not have start time after its end time."""

        contest = Contest(
            name="Test contest",
            start_time=self.tomorrow,
            freeze_time=self.yesterday,
            end_time=self.yesterday
        )
        self.assertRaises(ValidationError, contest.clean)
        self.assertRaises(ValidationError, contest.save)

    def test_construction_freeze_before_start(self):
        """Contests can not have freeze time before its start time."""

        contest = Contest(
            name="Test contest",
            start_time=self.now,
            freeze_time=self.yesterday,
            end_time=self.tomorrow
        )
        self.assertRaises(ValidationError, contest.clean)
        self.assertRaises(ValidationError, contest.save)

    def test_construction_freeze_after_end(self):
        """Contests can not have freeze time after its end time."""

        contest = Contest(
            name="Test contest",
            start_time=self.yesterday,
            freeze_time=self.tomorrow,
            end_time=self.now
        )
        self.assertRaises(ValidationError, contest.clean)
        self.assertRaises(ValidationError, contest.save)

    @override_settings(PRINTING_AVAILABLE=True)
    def test_printing_available(self):
        """Contests should allow printing when it is active, printing is
        enabled and global switch if on."""

        contest = Contest(
            name="Test contest",
            printing=True,
            start_time=self.yesterday,
            freeze_time=self.tomorrow,
            end_time=self.tomorrow
        )

        self.assertTrue(contest.is_active)
        self.assertTrue(contest.printing)
        self.assertTrue(contest.is_printing_available)

    @override_settings(PRINTING_AVAILABLE=True)
    def test_printing_before_start(self):
        """Contests should not allow printing when they are not started yet."""

        contest = Contest(
            name="Test contest",
            printing=True,
            start_time=self.tomorrow,
            freeze_time=self.tomorrow,
            end_time=self.tomorrow
        )

        self.assertFalse(contest.is_active)
        self.assertTrue(contest.printing)
        self.assertFalse(contest.is_printing_available)

    @override_settings(PRINTING_AVAILABLE=True)
    def test_printing_after_finish(self):
        """Contests should not allow printing when they are finished."""

        contest = Contest(
            name="Test contest",
            printing=True,
            start_time=self.yesterday,
            freeze_time=self.yesterday,
            end_time=self.yesterday
        )

        self.assertFalse(contest.is_active)
        self.assertTrue(contest.printing)
        self.assertFalse(contest.is_printing_available)

    @override_settings(PRINTING_AVAILABLE=False)
    def test_printing_global_disable(self):
        """Contests should not allow printing when it is globally disabled."""

        contest = Contest(
            name="Test contest",
            printing=True,
            start_time=self.yesterday,
            freeze_time=self.tomorrow,
            end_time=self.tomorrow
        )

        self.assertTrue(contest.is_active)
        self.assertTrue(contest.printing)
        self.assertFalse(contest.is_printing_available)

    def test_str(self):
        """Contests should have a valid __str__ method."""
        contest = Contest(
            name="Test contest",
        )
        self.assertEquals(str(contest), contest.name)

    def test_get_absolute_url(self):
        """Contests should have a get_absolute_url
        method pointing to a valid url."""

        contest = Contest(
            name="Test contest",
        )
        contest.save()

        password = 'test'
        admin = User.objects.create_superuser('test', 'test@t.com', password)
        logged_in = self.client.login(username=admin.username,
                password=password)
        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 200)

    def test_anonymous_access(self):
        """Anonymous users should be redirected to the login page."""

        contest = Contest(
            name="Test contest",
        )
        contest.save()

        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 302)
        self.assertTrue('login' in response.url)

    def test_authorized_access(self):
        """Reads by permitted users should be allowed."""

        contest = Contest(
            name="Test contest",
        )
        contest.save()

        password = 'test'
        user = User.objects.create_user('test', 'test@test.com', password)
        assign_perm('view_contest', user, contest)
        logged_in = self.client.login(username=user.username,
                password=password)

        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 200)

    def test_unauthorized_access(self):
        """Reads by users without a given permission should be forbidden."""

        contest = Contest(
            name="Test contest",
        )
        contest.save()

        password = 'test'
        user = User.objects.create_user('test', 'test@test.com', password)
        logged_in = self.client.login(username=user.username,
                password=password)

        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 403)

    def test_authorized_access_before_start(self):
        """Reads by permitted users should not be allowed
        before the contest starts."""

        contest = Contest(
            start_time=self.tomorrow,
            end_time=self.tomorrow,
            freeze_time=self.tomorrow,
            name="Test contest",
        )
        contest.save()

        password = 'test'
        user = User.objects.create_user('test', 'test@test.com', password)
        assign_perm('view_contest', user, contest)
        logged_in = self.client.login(username=user.username,
                password=password)

        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 403)

    def test_superuser_access_before_start(self):
        """Superusers should be allowed to access
        a contest even before it starts."""

        contest = Contest(
            start_time=self.tomorrow,
            end_time=self.tomorrow,
            freeze_time=self.tomorrow,
            name="Test contest",
        )
        contest.save()

        password = 'test'
        admin = User.objects.create_superuser('test', 'test@t.com', password)
        logged_in = self.client.login(username=admin.username,
                password=password)
        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 200)

    def test_staff_access_before_start(self):
        """Staff user with permissions should be allowed to access
        a contest even before it starts."""

        contest = Contest(
            start_time=self.tomorrow,
            end_time=self.tomorrow,
            freeze_time=self.tomorrow,
            name="Test contest",
        )
        contest.save()

        password = 'test'
        user = User.objects.create_user('test', 'test@test.com', password,
                is_staff=True)
        assign_perm('view_contest', user, contest)
        logged_in = self.client.login(username=user.username,
                password=password)
        response = self.client.get(contest.get_absolute_url())

        self.assertEquals(response.status_code, 200)
