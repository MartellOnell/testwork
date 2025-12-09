from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import User
from apps.surveys.models import Survey, Question, AnswerOption, SurveySession, UserAnswer


class SurveyModelTestCase(TestCase):
    """Тесты для модели Survey."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
    
    def test_create_survey(self):
        """Тест создания опроса."""
        survey = Survey.objects.create(
            title='Test Survey',
            author=self.author
        )
        self.assertEqual(survey.title, 'Test Survey')
        self.assertEqual(survey.author, self.author)
        self.assertTrue(survey.is_active)
    
    def test_survey_str(self):
        """Тест строкового представления опроса."""
        survey = Survey.objects.create(
            title='Test Survey',
            author=self.author
        )
        self.assertEqual(str(survey), 'Test Survey')


class QuestionModelTestCase(TestCase):
    """Тесты для модели Question."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author
        )
    
    def test_create_question(self):
        """Тест создания вопроса."""
        question = Question.objects.create(
            survey=self.survey,
            text='What is your favorite color?',
            order=0
        )
        self.assertEqual(question.text, 'What is your favorite color?')
        self.assertEqual(question.order, 0)
    
    def test_question_ordering(self):
        """Тест сортировки вопросов по полям survey и order."""
        q1 = Question.objects.create(survey=self.survey, text='Q1', order=1)
        q2 = Question.objects.create(survey=self.survey, text='Q2', order=0)
        
        questions = list(Question.objects.filter(survey=self.survey))
        self.assertEqual(questions[0], q2)
        self.assertEqual(questions[1], q1)


class AnswerOptionModelTestCase(TestCase):
    """Тесты для модели AnswerOption."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author
        )
        self.question = Question.objects.create(
            survey=self.survey,
            text='What is your favorite color?',
            order=0
        )
    
    def test_create_answer_option(self):
        """Тест создания варианта ответа."""
        option = AnswerOption.objects.create(
            question=self.question,
            text='Blue',
            order=0
        )
        self.assertEqual(option.text, 'Blue')
        self.assertEqual(option.question, self.question)


class SurveyAPITestCase(APITestCase):
    """Тесты для API эндпоинтов опросов."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.client = APIClient()
    
    def test_list_surveys_unauthenticated(self):
        """Тест: неаутентифицированные пользователи не могут получить список опросов."""
        url = reverse('survey-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_surveys_as_author(self):
        """Тест: авторы видят только свои опросы."""
        self.client.force_authenticate(user=self.author)
        
        # Создаём опрос от имени автора
        Survey.objects.create(title='Author Survey', author=self.author)
        
        # Создаём опрос другого автора
        other_author = User.objects.create_user(
            username='other_author',
            email='other@test.com',
            password='testpass123',
            is_author=True
        )
        Survey.objects.create(title='Other Survey', author=other_author)
        
        url = reverse('survey-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ответ может быть пагинированным (dict с 'results') или списком
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Author Survey')
    
    def test_list_surveys_as_respondent(self):
        """Тест: респонденты видят все активные опросы."""
        self.client.force_authenticate(user=self.respondent)
        
        # Создаём активные опросы
        Survey.objects.create(title='Active Survey 1', author=self.author, is_active=True)
        Survey.objects.create(title='Active Survey 2', author=self.author, is_active=True)
        Survey.objects.create(title='Inactive Survey', author=self.author, is_active=False)
        
        url = reverse('survey-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ответ может быть пагинированным (dict с 'results') или списком
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 2)
    
    def test_create_survey_as_author(self):
        """Тест: авторы могут создавать опросы."""
        self.client.force_authenticate(user=self.author)
        
        url = reverse('survey-list')
        data = {
            'title': 'New Survey',
            'questions': [
                {
                    'text': 'Question 1',
                    'order': 0,
                    'answer_options': [
                        {'text': 'Option A', 'order': 0},
                        {'text': 'Option B', 'order': 1}
                    ]
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(AnswerOption.objects.count(), 2)
    
    def test_create_survey_without_questions(self):
        """Тест: опросы можно создавать без вопросов."""
        self.client.force_authenticate(user=self.author)
        
        url = reverse('survey-list')
        data = {'title': 'Empty Survey'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)
    
    def test_get_survey_detail(self):
        """Тест получения детальной информации об опросе."""
        self.client.force_authenticate(user=self.author)
        
        survey = Survey.objects.create(title='Test Survey', author=self.author)
        question = Question.objects.create(
            survey=survey,
            text='Sample question',
            order=0
        )
        AnswerOption.objects.create(question=question, text='Option 1', order=0)
        
        url = reverse('survey-detail', kwargs={'pk': survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Survey')
        self.assertEqual(len(response.data['questions']), 1)
    
    def test_update_survey(self):
        """Тест обновления опроса."""
        self.client.force_authenticate(user=self.author)
        
        survey = Survey.objects.create(title='Original Title', author=self.author)
        
        url = reverse('survey-detail', kwargs={'pk': survey.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey.refresh_from_db()
        self.assertEqual(survey.title, 'Updated Title')
    
    def test_delete_survey(self):
        """Тест удаления опроса."""
        self.client.force_authenticate(user=self.author)
        
        survey = Survey.objects.create(title='Test Survey', author=self.author)
        
        url = reverse('survey-detail', kwargs={'pk': survey.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Survey.objects.count(), 0)


class NextQuestionAPITestCase(APITestCase):
    """Тесты для эндпоинта next-question."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author,
            is_active=True
        )
        self.question1 = Question.objects.create(
            survey=self.survey,
            text='Question 1',
            order=0
        )
        self.question2 = Question.objects.create(
            survey=self.survey,
            text='Question 2',
            order=1
        )
        self.option1 = AnswerOption.objects.create(
            question=self.question1,
            text='Option A',
            order=0
        )
        self.option2 = AnswerOption.objects.create(
            question=self.question2,
            text='Option B',
            order=0
        )
        self.client = APIClient()
    
    def test_get_first_question(self):
        """Тест получения первого вопроса опроса."""
        self.client.force_authenticate(user=self.respondent)
        
        url = reverse('survey-next-question', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('question', response.data)
        self.assertEqual(response.data['question']['text'], 'Question 1')
        self.assertFalse(response.data['is_completed'])
    
    def test_get_next_question_after_answer(self):
        """Тест получения следующего вопроса после ответа на предыдущий."""
        self.client.force_authenticate(user=self.respondent)
        
        # Создаём сессию и отвечаем на первый вопрос
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent
        )
        UserAnswer.objects.create(
            session=session,
            question=self.question1,
            selected_option=self.option1,
            survey=self.survey,
            user=self.respondent
        )
        
        url = reverse('survey-next-question', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question']['text'], 'Question 2')
    
    def test_survey_completed(self):
        """Тест ответа когда все вопросы отвечены."""
        self.client.force_authenticate(user=self.respondent)
        
        # Создаём сессию с is_completed=False (как в usecase с get_or_create)
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent,
            is_completed=False
        )
        # Отвечаем на все вопросы
        UserAnswer.objects.create(
            session=session,
            question=self.question1,
            selected_option=self.option1,
            survey=self.survey,
            user=self.respondent
        )
        UserAnswer.objects.create(
            session=session,
            question=self.question2,
            selected_option=self.option2,
            survey=self.survey,
            user=self.respondent
        )
        
        url = reverse('survey-next-question', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Когда все вопросы отвечены, is_completed должен быть True
        self.assertTrue(response.data.get('is_completed', False))
    
    def test_next_question_unauthenticated(self):
        """Тест: неаутентифицированные пользователи не могут получить следующий вопрос."""
        url = reverse('survey-next-question', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubmitAnswerAPITestCase(APITestCase):
    """Тесты для эндпоинта submit-answer."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author,
            is_active=True
        )
        self.question = Question.objects.create(
            survey=self.survey,
            text='Question 1',
            order=0
        )
        self.option1 = AnswerOption.objects.create(
            question=self.question,
            text='Option A',
            order=0
        )
        self.option2 = AnswerOption.objects.create(
            question=self.question,
            text='Option B',
            order=1
        )
        self.client = APIClient()
    
    def test_submit_answer(self):
        """Тест отправки ответа."""
        self.client.force_authenticate(user=self.respondent)
        
        url = reverse('survey-submit-answer', kwargs={'pk': self.survey.pk})
        data = {
            'question_id': self.question.pk,
            'answer_option_id': self.option1.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserAnswer.objects.count(), 1)
        
        answer = UserAnswer.objects.first()
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.selected_option, self.option1)
        self.assertEqual(answer.user, self.respondent)
    
    def test_submit_answer_creates_session(self):
        """Тест: отправка ответа создаёт сессию, если её нет."""
        self.client.force_authenticate(user=self.respondent)
        
        self.assertEqual(SurveySession.objects.count(), 0)
        
        url = reverse('survey-submit-answer', kwargs={'pk': self.survey.pk})
        data = {
            'question_id': self.question.pk,
            'answer_option_id': self.option1.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SurveySession.objects.count(), 1)
    
    def test_submit_answer_invalid_question(self):
        """Тест отправки ответа с неверным ID вопроса."""
        self.client.force_authenticate(user=self.respondent)
        
        url = reverse('survey-submit-answer', kwargs={'pk': self.survey.pk})
        data = {
            'question_id': 9999,
            'answer_option_id': self.option1.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_answer_invalid_option(self):
        """Тест отправки ответа с неверным ID варианта."""
        self.client.force_authenticate(user=self.respondent)
        
        url = reverse('survey-submit-answer', kwargs={'pk': self.survey.pk})
        data = {
            'question_id': self.question.pk,
            'answer_option_id': 9999
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_answer_option_wrong_question(self):
        """Тест отправки ответа с вариантом от другого вопроса."""
        self.client.force_authenticate(user=self.respondent)
        
        # Создаём другой вопрос со своим вариантом
        other_question = Question.objects.create(
            survey=self.survey,
            text='Question 2',
            order=1
        )
        other_option = AnswerOption.objects.create(
            question=other_question,
            text='Other Option',
            order=0
        )
        
        url = reverse('survey-submit-answer', kwargs={'pk': self.survey.pk})
        data = {
            'question_id': self.question.pk,
            'answer_option_id': other_option.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_answer_unauthenticated(self):
        """Тест: неаутентифицированные пользователи не могут отправлять ответы."""
        url = reverse('survey-submit-answer', kwargs={'pk': self.survey.pk})
        data = {
            'question_id': self.question.pk,
            'answer_option_id': self.option1.pk
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StatisticsAPITestCase(APITestCase):
    """Тесты для эндпоинта statistics."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.other_author = User.objects.create_user(
            username='other_author',
            email='other@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author,
            is_active=True
        )
        self.question = Question.objects.create(
            survey=self.survey,
            text='Question 1',
            order=0
        )
        self.option1 = AnswerOption.objects.create(
            question=self.question,
            text='Option A',
            order=0
        )
        self.option2 = AnswerOption.objects.create(
            question=self.question,
            text='Option B',
            order=1
        )
        self.client = APIClient()
    
    def test_get_statistics_as_author(self):
        """Тест: автор опроса может просматривать статистику."""
        self.client.force_authenticate(user=self.author)
        
        # Создаём ответы
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent,
            is_completed=True
        )
        UserAnswer.objects.create(
            session=session,
            question=self.question,
            selected_option=self.option1,
            survey=self.survey,
            user=self.respondent
        )
        
        url = reverse('survey-statistics', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_responses', response.data)
        self.assertIn('completed_responses', response.data)
        self.assertIn('questions_statistics', response.data)
    
    def test_get_statistics_as_non_author(self):
        """Тест: не-авторы не могут просматривать статистику."""
        self.client.force_authenticate(user=self.other_author)
        
        url = reverse('survey-statistics', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_statistics_as_respondent(self):
        """Тест: респонденты не могут просматривать статистику."""
        self.client.force_authenticate(user=self.respondent)
        
        url = reverse('survey-statistics', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_statistics_unauthenticated(self):
        """Тест: неаутентифицированные пользователи не могут просматривать статистику."""
        url = reverse('survey-statistics', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MySessionAPITestCase(APITestCase):
    """Тесты для эндпоинта my-session."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author,
            is_active=True
        )
        self.client = APIClient()
    
    def test_get_my_session(self):
        """Test getting user's session for a survey."""
        self.client.force_authenticate(user=self.respondent)
        
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent
        )
        
        url = reverse('survey-my-session', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], session.pk)
    
    def test_get_my_session_not_found(self):
        """Test getting session when none exists."""
        self.client.force_authenticate(user=self.respondent)
        
        url = reverse('survey-my-session', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_my_session_unauthenticated(self):
        """Test that unauthenticated users cannot get session."""
        url = reverse('survey-my-session', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SurveySessionModelTestCase(TestCase):
    """Tests for SurveySession model."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author
        )
    
    def test_create_session(self):
        """Test session creation."""
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent
        )
        self.assertFalse(session.is_completed)
        self.assertIsNone(session.completed_at)
    
    def test_session_str(self):
        """Test session string representation."""
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent
        )
        self.assertIn(self.respondent.username, str(session))
        self.assertIn(self.survey.title, str(session))
    
    def test_completion_time_none_when_not_completed(self):
        """Test completion_time is None when not completed."""
        session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent
        )
        self.assertIsNone(session.completion_time)


class UserAnswerModelTestCase(TestCase):
    """Tests for UserAnswer model."""
    
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='testpass123',
            is_author=True
        )
        self.respondent = User.objects.create_user(
            username='respondent',
            email='respondent@test.com',
            password='testpass123',
            is_author=False
        )
        self.survey = Survey.objects.create(
            title='Test Survey',
            author=self.author
        )
        self.question = Question.objects.create(
            survey=self.survey,
            text='Question 1',
            order=0
        )
        self.option = AnswerOption.objects.create(
            question=self.question,
            text='Option A',
            order=0
        )
        self.session = SurveySession.objects.create(
            survey=self.survey,
            user=self.respondent
        )
    
    def test_create_answer(self):
        """Test answer creation."""
        answer = UserAnswer.objects.create(
            session=self.session,
            question=self.question,
            selected_option=self.option,
            survey=self.survey,
            user=self.respondent
        )
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.selected_option, self.option)
    
    def test_unique_answer_per_question_per_session(self):
        """Test that only one answer per question per session is allowed."""
        UserAnswer.objects.create(
            session=self.session,
            question=self.question,
            selected_option=self.option,
            survey=self.survey,
            user=self.respondent
        )
        
        # Try to create a duplicate answer
        with self.assertRaises(Exception):
            UserAnswer.objects.create(
                session=self.session,
                question=self.question,
                selected_option=self.option,
                survey=self.survey,
                user=self.respondent
            )
