# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from django.test import TestCase, override_settings

from django.utils import timezone

from judge.models import Contest

from django.contrib.auth.models import User


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
        method poiting to a valid url."""

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
