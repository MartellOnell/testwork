from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q

from apps.surveys.models import (
    Question,
    Survey,
    SurveySession,
    UserAnswer,
)


class GetStatisticsUseCase:
    def __init__(self, survey_id):
        self.survey_id = survey_id

    def execute(self):
        """
        Получает подробную статистику по опросу.
        """
        # Проверяем существование опроса
        try:
            survey = Survey.objects.get(id=self.survey_id)
        except Survey.DoesNotExist:
            raise ValueError("Опрос не существует.")

        # Получаем общее количество и завершённые ответы
        total_sessions = SurveySession.objects.filter(survey=survey).count()
        completed_sessions = SurveySession.objects.filter(
            survey=survey, is_completed=True
        ).count()

        # Вычисляем среднее время прохождения, используя агрегацию базы данных
        avg_completion_time = None
        completed_sessions_with_time = SurveySession.objects.filter(
            survey=survey,
            is_completed=True,
            completed_at__isnull=False,
            started_at__isnull=False,
        ).annotate(
            duration=ExpressionWrapper(
                F("completed_at") - F("started_at"),
                output_field=DurationField(),
            )
        )

        if completed_sessions_with_time.exists():
            # Вычисляем среднюю продолжительность
            avg_duration = completed_sessions_with_time.aggregate(
                avg_duration=Avg("duration")
            )["avg_duration"]

            if avg_duration:
                avg_completion_time = avg_duration.total_seconds()

        # Получаем статистику по каждому вопросу
        questions = Question.objects.filter(survey=survey).order_by("order")
        questions_statistics = []

        for question in questions:
            # Получаем количество ответов для этого вопроса
            answer_stats = (
                UserAnswer.objects.filter(question=question)
                .values("selected_option", "selected_option__text")
                .annotate(count=Count("id"))
                .order_by("-count")
            )

            total_answers = sum(stat["count"] for stat in answer_stats)

            popular_answers = [
                {
                    "answer_option_id": stat["selected_option"],
                    "answer_text": stat["selected_option__text"],
                    "count": stat["count"],
                    "percentage": (stat["count"] / total_answers * 100)
                    if total_answers > 0
                    else 0,
                }
                for stat in answer_stats
            ]

            questions_statistics.append(
                {
                    "question_id": question.id,
                    "question_text": question.text,
                    "question_order": question.order,
                    "total_answers": total_answers,
                    "popular_answers": popular_answers,
                }
            )

        return {
            "survey_id": survey.id,
            "survey_title": survey.title,
            "total_responses": total_sessions,
            "completed_responses": completed_sessions,
            "average_completion_time": avg_completion_time,
            "questions_statistics": questions_statistics,
        }
