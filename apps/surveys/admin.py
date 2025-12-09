from django.contrib import admin

from .models import AnswerOption, Question, Survey, SurveySession, UserAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ["text", "order"]
    ordering = ["order"]


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1
    fields = ["text", "order"]
    ordering = ["order"]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "author__username"]
    inlines = [QuestionInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "survey", "order"]
    list_filter = ["survey"]
    search_fields = ["text", "survey__title"]
    inlines = [AnswerOptionInline]
    ordering = ["survey", "order"]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ["text", "question", "order"]
    list_filter = ["question__survey"]
    search_fields = ["text", "question__text"]
    ordering = ["question", "order"]


@admin.register(SurveySession)
class SurveySessionAdmin(admin.ModelAdmin):
    list_display = ["user", "survey", "started_at", "completed_at", "is_completed"]
    list_filter = ["is_completed", "started_at", "survey"]
    search_fields = ["user__username", "survey__title"]
    readonly_fields = ["started_at", "completed_at"]


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ["user", "survey", "question", "selected_option", "answered_at"]
    list_filter = ["survey", "answered_at"]
    search_fields = ["user__username", "survey__title", "question__text"]
    readonly_fields = ["answered_at"]
