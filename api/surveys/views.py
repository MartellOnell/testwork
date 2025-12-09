from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.surveys.models import Survey, SurveySession
from apps.surveys.usecases.create_survey import CreateSurveyUseCase
from apps.surveys.usecases.get_next_question import GetNextQuestionUseCase
from apps.surveys.usecases.get_statistics import GetStatisticsUseCase
from apps.surveys.usecases.submit_answer import SubmitAnswerUseCase

from .serializers import (
    QuestionSerializer,
    SubmitAnswerSerializer,
    SurveyCreateSerializer,
    SurveyDetailSerializer,
    SurveyListSerializer,
    SurveySessionSerializer,
    UserAnswerSerializer,
)


class SurveyViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с опросами.
    Использует UseCases для бизнес-логики, следуя паттерну Service Layer.
    """

    permission_classes = [IsAuthenticated]
    queryset = Survey.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return SurveyListSerializer
        elif self.action == "create":
            return SurveyCreateSerializer
        return SurveyDetailSerializer

    def get_queryset(self):
        """Фильтрует опросы в зависимости от роли пользователя."""
        user = self.request.user
        if user.is_author:
            # Авторы видят свои собственные опросы
            return Survey.objects.filter(author=user).select_related("author")
        else:
            # Респонденты видят все активные опросы
            return Survey.objects.filter(is_active=True).select_related("author")

    def perform_create(self, serializer):
        """Использует CreateSurveyUseCase для создания опросов."""
        validated_data = serializer.validated_data

        usecase = CreateSurveyUseCase(author=self.request.user)
        survey = usecase.execute(
            title=validated_data["title"],
            questions_data=validated_data.get("questions", []),
        )

        # Устанавливаем созданный survey в serializer для правильного ответа
        serializer.instance = survey

    @action(detail=True, methods=["get"], url_path="next-question")
    def next_question(self, request, pk=None):
        """
        Получить следующий неотвеченный вопрос для текущего пользователя.
        """
        try:
            usecase = GetNextQuestionUseCase(user=request.user, survey_id=pk)
            result = usecase.execute()

            if result["is_completed"]:
                return Response(
                    {
                        "message": "Опрос завершён",
                        "is_completed": True,
                        "progress": result["progress"],
                    },
                    status=status.HTTP_200_OK,
                )

            if result["question"] is None:
                return Response(
                    {
                        "message": "Нет доступных вопросов",
                        "is_completed": True,
                        "progress": result["progress"],
                    },
                    status=status.HTTP_200_OK,
                )

            # Сериализуем вопрос с вариантами ответов
            question_serializer = QuestionSerializer(result["question"])

            return Response(
                {
                    "question": question_serializer.data,
                    "progress": result["progress"],
                    "is_completed": result["is_completed"],
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="submit-answer")
    def submit_answer(self, request, pk=None):
        """
        Отправить ответ на вопрос в опросе.
        """
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usecase = SubmitAnswerUseCase(user=request.user, survey_id=pk)
            answer = usecase.execute(
                question_id=serializer.validated_data["question_id"],
                answer_option_id=serializer.validated_data["answer_option_id"],
            )

            answer_serializer = UserAnswerSerializer(answer)
            return Response(answer_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, pk=None):
        """
        Получить статистику по опросу.
        """
        # Разрешить просмотр статистики только авторам опроса
        survey = get_object_or_404(Survey, pk=pk)
        if not request.user.is_author or survey.author != request.user:
            return Response(
                {"error": "Только автор опроса может просматривать статистику"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            usecase = GetStatisticsUseCase(survey_id=pk)
            stats = usecase.execute()
            return Response(stats, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="my-session")
    def my_session(self, request, pk=None):
        """
        Получить сессию текущего пользователя для этого опроса.
        """
        survey = get_object_or_404(Survey, pk=pk)
        sessions = SurveySession.objects.filter(
            user=request.user, survey=survey
        ).order_by("-started_at")

        if not sessions.exists():
            return Response(
                {"message": "Сессия для этого опроса не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SurveySessionSerializer(sessions.first())
        return Response(serializer.data, status=status.HTTP_200_OK)
