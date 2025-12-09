from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Survey(models.Model):
    """
    Модель опроса, представляющая анкету, созданную автором.
    """

    title = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_surveys",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "surveys"
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["is_active", "created_at"]),
        ]

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Модель вопроса, представляющая отдельный вопрос в опросе.
    """

    TEXT_PREVIEW_LENGTH = 50

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField()
    order = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions"
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["survey", "order"]
        indexes = [
            models.Index(fields=["survey", "order"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["survey", "order"], name="unique_question_order_per_survey"
            )
        ]

    def __str__(self):
        return f"{self.survey.title} - Q{self.order}: {self.text[: self.TEXT_PREVIEW_LENGTH]}"


class AnswerOption(models.Model):
    """
    Модель варианта ответа, представляющая возможные ответы на вопрос.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answer_options",
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "answer_options"
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        ordering = ["question", "order"]
        indexes = [
            models.Index(fields=["question", "order"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"], name="unique_answer_order_per_question"
            )
        ]

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"


class SurveySession(models.Model):
    """
    Модель сессии опроса, отслеживающая попытку пользователя завершить опрос.
    """

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="sessions"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="survey_sessions",
    )
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_completed = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "survey_sessions"
        verbose_name = "Сессия опроса"
        verbose_name_plural = "Сессии опросов"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "survey"]),
            models.Index(fields=["survey", "is_completed"]),
            models.Index(fields=["user", "started_at"]),
            models.Index(fields=["survey", "completed_at"]),
        ]

    def __str__(self):
        status = "Завершён" if self.is_completed else "В процессе"
        return f"{self.user.username} - {self.survey.title} ({status})"

    @property
    def completion_time(self):
        """Вычисляет время, затраченное на прохождение опроса в секундах."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class UserAnswer(models.Model):
    """
    Модель ответа пользователя, хранящая индивидуальные ответы пользователей.
    """

    session = models.ForeignKey(
        SurveySession,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
        related_name="user_selections",
    )
    # Денормализованные поля для более быстрых запросов статистики
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="all_answers",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    answered_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        db_table = "user_answers"
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"
        ordering = ["session", "question__order"]
        indexes = [
            models.Index(fields=["session", "question"]),
            models.Index(fields=["survey", "question"]),
            models.Index(fields=["survey", "selected_option"]),
            models.Index(fields=["user", "survey"]),
            models.Index(fields=["question", "selected_option"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "question"],
                name="unique_answer_per_question_per_session",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]} - {self.selected_option.text}"
