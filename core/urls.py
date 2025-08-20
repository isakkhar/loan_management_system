from django.urls import path
from . import views

urlpatterns = [
    # path('', views.dashboard, name='dashboard'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/<int:pk>/', views.loan_detail, name='loan_detail'),
    path('apply/', views.loan_application, name='loan_application'),
    path('repayment/<int:pk>/', views.make_repayment, name='make_repayment'),
    path('admin/loans/', views.admin_loan_list, name='admin_loan_list'),
    path('admin/loans/<int:pk>/', views.admin_loan_detail, name='admin_loan_detail'),
    path('', views.home, name='home'),  # Add this line
    path('dashboard/', views.dashboard, name='dashboard'),
]