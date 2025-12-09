from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.surveys.models import AnswerOption, Question, Survey

User = get_user_model()


class Command(BaseCommand):
    help = "Заполняет базу данных примерами данных опросов"

    def handle(self, *args, **kwargs):
        self.stdout.write("Создание примеров данных...")

        # Создаём примеры пользователей
        author, created = User.objects.get_or_create(
            username="survey_author",
            defaults={
                "email": "author@example.com",
                "is_author": True,
                "first_name": "Survey",
                "last_name": "Author",
            },
        )
        if created:
            author.set_password("password123")
            author.save()
            self.stdout.write(
                self.style.SUCCESS(f"Создан пользователь-автор: {author.username}")
            )

        respondent, created = User.objects.get_or_create(
            username="respondent",
            defaults={
                "email": "respondent@example.com",
                "is_author": False,
                "first_name": "Test",
                "last_name": "Respondent",
            },
        )
        if created:
            respondent.set_password("password123")
            respondent.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Создан пользователь-респондент: {respondent.username}"
                )
            )

        survey, created = Survey.objects.get_or_create(
            title="Овощи", author=author, defaults={"is_active": True}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Создан опрос: {survey.title}"))
            questions_data = [
                {
                    "text": "Ты любишь буратту с помидорами?",
                    "answers": ["Да", "Нет", "У меня непереносимость лактозы"],
                },
                {
                    "text": "Ты любишь огурцы?",
                    "answers": ["Да", "Нет", "Только в коктейлях"],
                },
                {
                    "text": "Ты любишь баклажаны?",
                    "answers": ["Да", "Нет", "Только если это бабагануш"],
                },
                {
                    "text": "Ты любишь кабачки?",
                    "answers": ["Да", "Нет", "Только жареные"],
                },
                {
                    "text": "Ты любишь морковь?",
                    "answers": ["Да", "Нет", "Только в торте"],
                },
                {
                    "text": "Ты любишь капусту?",
                    "answers": ["Да", "Нет", "Только квашенную"],
                },
                {
                    "text": "Ты любишь болгарский перец?",
                    "answers": ["Да", "Нет", "Только красный"],
                },
                {
                    "text": "Ты любишь лук?",
                    "answers": ["Да", "Нет", "Только карамелизованный"],
                },
                {
                    "text": "Ты любишь чеснок?",
                    "answers": ["Да", "Нет", "Только в соусе"],
                },
                {
                    "text": "Ты любишь помидоры?",
                    "answers": ["Да", "Нет", "Только если гаспаччо"],
                },
            ]

            for order, question_data in enumerate(questions_data):
                question = Question.objects.create(
                    survey=survey, text=question_data["text"], order=order
                )

                for answer_order, answer_text in enumerate(question_data["answers"]):
                    AnswerOption.objects.create(
                        question=question, text=answer_text, order=answer_order
                    )

                self.stdout.write(f"  Создан вопрос {order + 1}: {question.text}")

            self.stdout.write(self.style.SUCCESS("Примеры данных успешно созданы!"))
        else:
            self.stdout.write(
                self.style.WARNING("Опрос уже существует. Пропускаем создание.")
            )

        self.stdout.write(self.style.SUCCESS("\nПримеры пользователей:"))
        self.stdout.write(f"  Автор: username=survey_author, password=password123")
        self.stdout.write(f"  Респондент: username=respondent, password=password123")
