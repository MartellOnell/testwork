from django.urls import include, path

urlpatterns = [
    path("users/", include("api.users.urls")),
    path("surveys/", include("api.surveys.urls")),
]
