from django.contrib import admin
from .models import LoanType, Loan, Repayment, Document

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'interest_rate', 'min_amount', 'max_amount', 'min_term', 'max_term']
    list_filter = ['interest_rate']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loan_type', 'amount', 'term', 'status', 'application_date']
    list_filter = ['status', 'loan_type', 'application_date']
    search_fields = ['customer__username', 'customer__email']

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'installment_number', 'amount', 'due_date', 'status']
    list_filter = ['status', 'due_date']
    search_fields = ['loan__customer__username']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'title', 'uploaded_at']
    search_fields = ['loan__customer__username', 'title']