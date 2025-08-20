from django import forms
from .models import Loan, LoanType, Document
from django.core.validators import MinValueValidator
from decimal import Decimal


class LoanApplicationForm(forms.ModelForm):
    loan_type = forms.ModelChoiceField(
        queryset=LoanType.objects.all(),
        empty_label="Select Loan Type"
    )

    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'term', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.loan_type_id:
            loan_type = LoanType.objects.get(id=self.instance.loan_type_id)
            self.fields['amount'].validators.append(
                MinValueValidator(loan_type.min_amount)
            )
            self.fields['amount'].widget.attrs['min'] = loan_type.min_amount
            self.fields['amount'].widget.attrs['max'] = loan_type.max_amount
            self.fields['term'].widget.attrs['min'] = loan_type.min_term
            self.fields['term'].widget.attrs['max'] = loan_type.max_term


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'document']