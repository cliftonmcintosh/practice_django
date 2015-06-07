import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from .models import Question


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(seconds=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False, 'Should return False for a question in the future')

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is more than one day in the past.
        """
        time = timezone.now() - datetime.timedelta(minutes=(60 * 24) + 1)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False, 'Should return false for a question greater than 24 hours old.')

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose pub_ate is less than one day in the past.
        """
        time = timezone.now() - datetime.timedelta(minutes=(60 * 24) - 1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True, 'Should return true for a question less than 24 hours old')

def create_question(question_text, days):
    """
    Helper method to create a question for testing.
    :param question_text: the text of the question
    :param days: the number of days to add to now for the pub_date
    :return: the created question
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200, 'Should get a successful response')
        self.assertContains(response, 'No polls are available')

    def test_index_view_with_a_past_question(self):
        """
        A question with a pub_date that is in the past should be displayed on the index page.
        """
        question_text = 'Is that all there is?'
        create_question(question_text=question_text, days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200, 'Should get a successful response')
        self.assertEqual(len(response.context['latest_question_list']), 1, 'There should be one question')
        self.assertEqual(response.context['latest_question_list'][0].question_text, question_text, 'The text should be what we saved')

    def test_index_view_with_a_future_question(self):
        """
        A question with a pub_date that is in the future should not be displayed on the index page.
        """
        question_text = 'Is that all there is?'
        create_question(question_text=question_text, days=1)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200, 'Should get a successful response')
        self.assertEqual(len(response.context['latest_question_list']), 0, 'There should be no question in the view')

    def test_index_view_with_a_future_question_and_a_past_question(self):
        """
        When there is a question in the past and a question in the future, only the one in the past should be displayed.
        """
        past_question_text = 'Is it past?'
        create_question(question_text=past_question_text, days=-1)
        future_question_text = 'Are we there yet?'
        create_question(question_text=future_question_text, days=1)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200, 'Should get a successful response')
        self.assertEqual(len(response.context['latest_question_list']), 1, 'There should be one question')
        self.assertEqual(response.context['latest_question_list'][0].question_text, past_question_text, 'The text should be the text for the past question')

    def test_index_view_with_two_past_questions(self):
        """
        All the past questions should be displayed.
        """
        past_question_text_one = 'Is it past?'
        create_question(question_text=past_question_text_one, days=-1)
        past_question_text_two = 'Has it happened?'
        create_question(question_text=past_question_text_two, days=-1)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200, 'Should get a successful response')
        self.assertEqual(len(response.context['latest_question_list']), 2, 'There should be two questions')
        self.assertEqual(len([question for question in response.context['latest_question_list'] if question.question_text == past_question_text_one]), 1)
        self.assertEqual(len([question for question in response.context['latest_question_list'] if question.question_text == past_question_text_two]), 1)

class QuestionDetailViewTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        """
        The detail view should not display a question with a future pub_date.
        """
        future_question = create_question(question_text='Is this what you expected?', days=1)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404, 'The question should not be found')

    def test_detail_view_with_a_past_question(self):
        """
        The detail view should not display a question with a future pub_date.
        """
        past_question = create_question(question_text='Is this what happened?', days=-1)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertEqual(response.status_code, 200, 'The question should be found')
