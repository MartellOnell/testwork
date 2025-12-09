from rest_framework import serializers

from apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveySession,
    UserAnswer,
)


class AnswerOptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AnswerOption."""

    class Meta:
        model = AnswerOption
        fields = ["id", "text", "order"]
        read_only_fields = ["id"]


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Question с вложенными вариантами ответов."""

    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "order", "answer_options"]
        read_only_fields = ["id"]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вопросов с вариантами ответов."""

    answer_options = AnswerOptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ["text", "order", "answer_options"]


class SurveyListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка опросов."""

    author_username = serializers.CharField(source="author.username", read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "author_username",
            "created_at",
            "is_active",
            "question_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_question_count(self, obj):
        return obj.questions.count()


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра опроса со всеми вопросами."""

    questions = QuestionSerializer(many=True, read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "author",
            "author_username",
            "created_at",
            "updated_at",
            "is_active",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SurveyCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания опросов с вопросами и вариантами ответов."""

    questions = QuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = ["title", "questions"]


class SurveySessionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели SurveySession."""

    survey_title = serializers.CharField(source="survey.title", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    completion_time = serializers.ReadOnlyField()

    class Meta:
        model = SurveySession
        fields = [
            "id",
            "survey",
            "survey_title",
            "user",
            "username",
            "started_at",
            "completed_at",
            "is_completed",
            "completion_time",
        ]
        read_only_fields = ["id", "started_at", "completed_at", "is_completed"]


class UserAnswerSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserAnswer."""

    question_text = serializers.CharField(source="question.text", read_only=True)
    selected_option_text = serializers.CharField(
        source="selected_option.text", read_only=True
    )

    class Meta:
        model = UserAnswer
        fields = [
            "id",
            "session",
            "question",
            "question_text",
            "selected_option",
            "selected_option_text",
            "answered_at",
        ]
        read_only_fields = ["id", "answered_at"]


class SubmitAnswerSerializer(serializers.Serializer):
    """Сериализатор для отправки ответа на вопрос."""

    question_id = serializers.IntegerField()
    answer_option_id = serializers.IntegerField()


class NextQuestionSerializer(serializers.Serializer):
    """Сериализатор для ответа со следующим вопросом."""

    question = QuestionSerializer()
    progress = serializers.DictField()
    is_completed = serializers.BooleanField()
