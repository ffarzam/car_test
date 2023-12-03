from django.urls import path
from . import views

app_name = "car"
urlpatterns = [
    path('parts_list/<int:car_id>/', views.CarPartsListView.as_view(), name='parts_list'),
    path('upload/<str:car_model>/<str:part_name>/', views.FileUploadView.as_view()),
    path('download_file/<int:file_id>/', views.FileDownloadView.as_view(), name='download_file'),
    path('download_part_files/<int:part_id>/', views.PartFilesDownloadView.as_view(), name='download_part_files'),
    path('download_car_parts_files/<int:part_id>/', views.CarPartsFilesDownloadView.as_view(), name='download_car_parts_files'),
]