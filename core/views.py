from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Loan, Repayment, LoanType, Document
from .forms import LoanApplicationForm, DocumentForm

def is_staff(user):
    return user.is_staff

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    user_loans = Loan.objects.filter(customer=request.user)
    total_loans = user_loans.count()
    active_loans = user_loans.filter(status='active').count()
    pending_loans = user_loans.filter(status='pending').count()
    total_balance = user_loans.filter(status='active').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'total_loans': total_loans,
        'active_loans': active_loans,
        'pending_loans': pending_loans,
        'total_balance': total_balance,
        'loans': user_loans.order_by('-application_date')[:5]
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def loan_list(request):
    loans = Loan.objects.filter(customer=request.user)
    return render(request, 'core/loan_list.html', {'loans': loans})

@login_required
def loan_detail(request, pk):
    loan = get_object_or_404(Loan, pk=pk, customer=request.user)
    repayments = loan.repayments.all()
    documents = loan.documents.all()

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.loan = loan
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('loan_detail', pk=pk)
    else:
        form = DocumentForm()

    return render(request, 'core/loan_detail.html', {
        'loan': loan,
        'repayments': repayments,
        'documents': documents,
        'form': form
    })

@login_required
def loan_application(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.customer = request.user
            loan.interest_rate = loan.loan_type.interest_rate
            loan.save()
            messages.success(request, 'Loan application submitted successfully.')
            return redirect('dashboard')
    else:
        form = LoanApplicationForm()

    return render(request, 'core/loan_application.html', {'form': form})

@login_required
def make_repayment(request, pk):
    repayment = get_object_or_404(Repayment, pk=pk, loan__customer=request.user)

    if request.method == 'POST':
        # Process payment (simplified - in real app, integrate with payment gateway)
        repayment.status = 'paid'
        repayment.paid_date = timezone.now()
        repayment.save()

        # Check if all repayments are paid
        if not repayment.loan.repayments.filter(status='pending').exists():
            repayment.loan.status = 'completed'
            repayment.loan.save()

        messages.success(request, 'Payment processed successfully.')
        return redirect('loan_detail', pk=repayment.loan.pk)

    return render(request, 'core/repayment.html', {'repayment': repayment})

@user_passes_test(is_staff)
def admin_loan_list(request):
    loans = Loan.objects.all()
    status_filter = request.GET.get('status')

    if status_filter:
        loans = loans.filter(status=status_filter)

    return render(request, 'core/admin_loan_list.html', {'loans': loans})

@user_passes_test(is_staff)
def admin_loan_detail(request, pk):
    loan = get_object_or_404(Loan, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            loan.status = 'approved'
            loan.approved_by = request.user
            loan.approved_date = timezone.now()
            loan.start_date = timezone.now().date()

            # Calculate end date
            from dateutil.relativedelta import relativedelta
            loan.end_date = loan.start_date + relativedelta(months=+loan.term)

            loan.save()

            # Create repayment schedule
            monthly_payment = loan.monthly_installment()
            for i in range(loan.term):
                due_date = loan.start_date + relativedelta(months=+i+1)
                Repayment.objects.create(
                    loan=loan,
                    amount=monthly_payment,
                    due_date=due_date,
                    installment_number=i+1
                )

            messages.success(request, 'Loan approved successfully.')

        elif action == 'reject':
            loan.status = 'rejected'
            loan.save()
            messages.success(request, 'Loan rejected.')

        return redirect('admin_loan_detail', pk=pk)

    repayments = loan.repayments.all()
    documents = loan.documents.all()

    return render(request, 'core/admin_loan_detail.html', {
        'loan': loan,
        'repayments': repayments,
        'documents': documents
    })