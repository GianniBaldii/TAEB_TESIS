from django.urls import path

from . import views

app_name = "api_mobile"

urlpatterns = [
    path("auth/login/", views.MobileLoginView.as_view(), name="login"),
    path("auth/refresh/", views.MobileRefreshView.as_view(), name="refresh"),
    path("auth/logout/", views.MobileLogoutView.as_view(), name="logout"),
    path("me/", views.MobileMeView.as_view(), name="me"),
    path("me/profile/", views.MobileProfileView.as_view(), name="profile"),
    path("me/progress/", views.MobileProgressView.as_view(), name="progress"),
    path("me/belt-history/", views.MobileBeltHistoryView.as_view(), name="belt_history"),
    path("me/exams/", views.MobileExamsView.as_view(), name="exams"),
]
