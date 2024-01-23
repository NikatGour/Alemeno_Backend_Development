# urls.py
from django.urls import path
from .views import register_customer, create_loan, check_loan_eligibility, view_loan, view_loans
# urls.py

urlpatterns = [
    path('register/', register_customer, name='register_customer'),
    path('create-loan/', create_loan, name='create_loan'),
    path('check-eligibility/', check_loan_eligibility, name='check_loan_eligibility'),
    path('view-loan/<int:loan_id>/', view_loan, name='view_loan'),
    path('view-loans/<int:customer_id>/', view_loans, name='view_loans'),
    path('view-loans/<int:customer_id>/', view_loans, name='view_loans'),
]
