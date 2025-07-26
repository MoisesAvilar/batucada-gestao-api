from django.urls import path
from .views import AdminDashboardAPIView, ExportAulasAPIView


app_name = "reporting"

urlpatterns = [
    path("reports/admin-dashboard/", AdminDashboardAPIView.as_view(), name="admin-dashboard"),
    path("reports/export/aulas/", ExportAulasAPIView.as_view(), name="export-aulas"),
]
