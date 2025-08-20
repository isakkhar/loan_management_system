from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class LoanType(models.Model):
    name = models.CharField(max_length=100)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_term = models.PositiveIntegerField(help_text="Maximum term in months")
    min_term = models.PositiveIntegerField(help_text="Minimum term in months")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Loan(models.Model):
    LOAN_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    term = models.PositiveIntegerField(help_text="Loan term in months")
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_loans')
    approved_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True, help_text="Reason for rejection (if applicable)")

    def __str__(self):
        return f"{self.customer.username} - {self.loan_type.name} - ${self.amount}"

    def monthly_installment(self):
        # Calculate monthly installment using the formula:
        # P * r * (1+r)^n / ((1+r)^n - 1)
        # Where P = principal, r = monthly interest rate, n = number of payments
        monthly_rate = self.interest_rate / 100 / 12
        numerator = monthly_rate * (1 + monthly_rate) ** self.term
        denominator = (1 + monthly_rate) ** self.term - 1
        return self.amount * numerator / denominator

    def total_repayment(self):
        return self.monthly_installment() * self.term


class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    due_date = models.DateField()
    paid_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('late', 'Late')],
                              default='pending')
    installment_number = models.PositiveIntegerField()

    class Meta:
        ordering = ['installment_number']

    def __str__(self):
        return f"Repayment #{self.installment_number} for {self.loan}"


class Document(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='loan_documents/')
    title = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title