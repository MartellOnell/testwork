from django.db import transaction

from apps.surveys.models import AnswerOption, Question, Survey


class CreateSurveyUseCase:
    def __init__(self, author):
        self.author = author

    @transaction.atomic
    def execute(self, title, questions_data):
        """
        Создаёт опрос с связанными вопросами и вариантами ответов.
        """
        # Проверяем права автора
        if not self.author.is_author:
            raise PermissionError(
                "Пользователь должен быть автором для создания опросов."
            )

        # Создаём опрос
        survey = Survey.objects.create(title=title, author=self.author)

        # Создаём вопросы и варианты ответов
        for question_data in questions_data:
            answer_options_data = question_data.pop("answer_options", [])

            question = Question.objects.create(
                survey=survey,
                text=question_data["text"],
                order=question_data.get("order", 0),
            )

            for option_data in answer_options_data:
                AnswerOption.objects.create(
                    question=question,
                    text=option_data["text"],
                    order=option_data.get("order", 0),
                )

        return survey
