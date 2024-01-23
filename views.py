from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from .loan_eligibility import calculate_credit_score, check_loan_eligibility

@api_view(['POST'])
def register_customer(request):
    data = request.data
    
    # Calculate approved limit based on salary
    monthly_salary = data.get('monthly_income')
    approved_limit = round(36 * monthly_salary / 100000) * 100000
    
    # Create a new customer and save to the database
    customer_data = {
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'age': data.get('age'),
        'monthly_income': monthly_salary,
        'phone_number': data.get('phone_number'),
        'approved_limit': approved_limit,
    }
    customer_serializer = CustomerSerializer(data=customer_data)
    if customer_serializer.is_valid():
        customer = customer_serializer.save()
        # Return customer details in the response
        response_data = {
            'customer_id': customer.id,
            'name': f'{customer.first_name} {customer.last_name}',
            'age': customer.age,
            'monthly_income': customer.monthly_income,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    data = request.data

    # Fetch customer data from the database
    customer_id = data.get('customer_id')
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Calculate credit score
    credit_score = calculate_credit_score(customer)

    # Check loan eligibility
    eligibility_result = check_loan_eligibility(credit_score, data)

    # Check if the loan is approved
    if eligibility_result['approval']:
        # Create a new Loan instance and save it
        loan_data = {
            'customer': customer,
            'loan_amount': data.get('loan_amount'),
            'interest_rate': eligibility_result['interest_rate'],
            'tenure': data.get('tenure'),
        }
        loan_serializer = LoanSerializer(data=loan_data)
        if loan_serializer.is_valid():
            loan = loan_serializer.save()
            # Return loan details in the response
            response_data = {
                'loan_id': loan.id,
                'customer_id': customer.id,
                'loan_approved': True,
                'message': 'Loan approved',
                'monthly_installment': eligibility_result['monthly_installment'],
            }
            return Response(response_data)
        else:
            return Response({'error': 'Failed to create loan'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'loan_id': None,
            'customer_id': customer.id,
            'loan_approved': False,
            'message': 'Loan not approved',
            'monthly_installment': 0,
        })


@api_view(['POST'])
def check_loan_eligibility(request):
    data = request.data

    # Fetch customer data from the database
    customer_id = data.get('customer_id')
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Calculate credit score
    credit_score = calculate_credit_score(customer)

    # Check loan eligibility
    eligibility_result = check_loan_eligibility(credit_score, data)

    # Prepare the response data
    response_data = {
        'customer_id': customer.id,
        'approval': eligibility_result['approval'],
        'interest_rate': eligibility_result['interest_rate'],
        'corrected_interest_rate': eligibility_result['corrected_interest_rate'],
        'tenure': data.get('tenure'),
        'monthly_installment': eligibility_result['monthly_installment'],
    }

    # Return the response
    return Response(response_data)


@api_view(['GET'])
def view_loan(request, loan_id):
    # Fetch loan data from the database
    loan = get_object_or_404(Loan, id=loan_id)
    customer = loan.customer

    # Prepare the response data
    response_data = {
        'loan_id': loan.id,
        'customer': {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone_number': customer.phone_number,
            'age': customer.age,
        },
        'loan_approved': loan.loan_approved,
        'loan_amount': loan.loan_amount,
        'interest_rate': loan.interest_rate,
        'monthly_installment': loan.monthly_installment,
        'tenure': loan.tenure,
    }

    # Return the response
    return Response(response_data)


# views.py
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def view_loans(request, customer_id):
    # Fetch all loans associated with the customer from the database
    customer = get_object_or_404(Customer, id=customer_id)
    loans = Loan.objects.filter(customer=customer)

    # Serialize the list of loans
    loan_serializer = LoanSerializer(loans, many=True)

    # Prepare the response data
    response_data = {
        'customer_id': customer.id,
        'loans': loan_serializer.data,
    }

    # Return the response
    return Response(response_data)
