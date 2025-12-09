from apps.surveys.models import Question, Survey, SurveySession, UserAnswer


class GetNextQuestionUseCase:
    def __init__(self, user, survey_id):
        self.user = user
        self.survey_id = survey_id

    def execute(self):
        """
        Получает следующий вопрос для пользователя в опросе вместе с прогрессом.
        """
        try:
            survey = Survey.objects.get(id=self.survey_id, is_active=True)
        except Survey.DoesNotExist:
            raise ValueError("Опрос не существует или неактивен.")

        # Получаем или создаём сессию опроса
        session, created = SurveySession.objects.get_or_create(
            user=self.user, survey=survey, is_completed=False
        )

        # Получаем все ID отвеченных вопросов для этой сессии
        answered_question_ids = set(
            UserAnswer.objects.filter(session=session).values_list(
                "question_id", flat=True
            )
        )

        # Получаем все вопросы для опроса, упорядоченные по полю order
        all_questions = list(
            Question.objects.filter(survey=survey)
            .prefetch_related("answer_options")
            .order_by("order")
        )

        # Находим первый неотвеченный вопрос
        next_question = None
        for question in all_questions:
            if question.id not in answered_question_ids:
                next_question = question
                break

        # Подсчитываем прогресс
        total_questions = len(all_questions)
        answered_count = len(answered_question_ids)
        progress = {
            "answered": answered_count,
            "total": total_questions,
            "percentage": (answered_count / total_questions * 100)
            if total_questions > 0
            else 0,
        }

        # Проверяем, завершён ли опрос
        is_completed = answered_count >= total_questions

        return {
            "question": next_question,
            "progress": progress,
            "is_completed": is_completed,
            "session": session,
        }
