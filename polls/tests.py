import datetime

from django.utils import timezone
from django.test import TestCase

from .models import Question

class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(seconds=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False, 'Should return False for a question in the future')

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is more than one day in the past
        """
        time = timezone.now() - datetime.timedelta(minutes=(60 * 24) + 1)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False, 'Should return false for a question greater than 24 hours old.')

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose pub_ate is less than one day in the past
        """
        time = timezone.now() - datetime.timedelta(minutes=(60 * 24) - 1)
        recent_question = Question(pub_date= time)
        self.assertEqual(recent_question.was_published_recently(), True, 'Should return true for a question less than 24 hours old')