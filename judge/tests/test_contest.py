#-*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from django.test import TestCase
from django.utils import timezone

from judge.models import Contest


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

    def test_str(self):
        """Contests should have a valid str method return value."""
        pass # TODO

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

    def test_printing_before_start(self):
        """Contests should not allow printing when they are not started yet."""
        pass

    def test_printing_after_finish(self):
        """Contests should not allow printing when they are finished."""
        pass

    def test_printing_global_disable(self):
        """Contests should not allow printing when it is globally disabled."""
        pass
