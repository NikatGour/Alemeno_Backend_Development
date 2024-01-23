from django.db import models

# Create your models here.
# models.py


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    monthly_income = models.PositiveIntegerField()
    phone_number = models.BigIntegerField()
    approved_limit = models.PositiveIntegerField(null=True, blank=True)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    interest_rate = models.FloatField()
    tenure = models.PositiveIntegerField()
    monthly_installment = models.FloatField()
    loan_approved = models.BooleanField(default=False)
