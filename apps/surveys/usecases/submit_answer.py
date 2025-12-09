from django.db import transaction
from django.utils import timezone

from apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveySession,
    UserAnswer,
)


class SubmitAnswerUseCase:
    def __init__(self, user, survey_id):
        self.user = user
        self.survey_id = survey_id

    @transaction.atomic
    def execute(self, question_id, answer_option_id):
        """
        Отправляет ответ на вопрос в опросе.
        """
        # Проверяем существование опроса
        try:
            survey = Survey.objects.get(id=self.survey_id, is_active=True)
        except Survey.DoesNotExist:
            raise ValueError("Опрос не существует или неактивен.")

        # Проверяем, что вопрос принадлежит опросу
        try:
            question = Question.objects.get(id=question_id, survey=survey)
        except Question.DoesNotExist:
            raise ValueError("Вопрос не принадлежит этому опросу.")

        # Проверяем, что вариант ответа принадлежит вопросу
        try:
            answer_option = AnswerOption.objects.get(
                id=answer_option_id, question=question
            )
        except AnswerOption.DoesNotExist:
            raise ValueError("Вариант ответа не принадлежит этому вопросу.")

        # Получаем или создаём сессию опроса
        session, created = SurveySession.objects.get_or_create(
            user=self.user,
            survey=survey,
            is_completed=False,
            defaults={"started_at": timezone.now()},
        )

        # Создаём или обновляем ответ
        answer, created = UserAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                "selected_option": answer_option,
                "survey": survey,
                "user": self.user,
            },
        )

        # Проверяем, завершён ли опрос
        total_questions = survey.questions.count()
        answered_questions = session.answers.count()

        if answered_questions >= total_questions:
            session.is_completed = True
            session.completed_at = timezone.now()
            session.save()

        return answer
