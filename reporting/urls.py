from django.urls import path
from .views import AdminDashboardAPIView


app_name = "reporting"

urlpatterns = [
    path("reports/admin-dashboard/", AdminDashboardAPIView.as_view(), name="admin-dashboard"),
]
