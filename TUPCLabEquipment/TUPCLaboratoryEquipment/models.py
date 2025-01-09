from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.forms import ValidationError


class Program(models.Model):
    program_name = models.CharField(max_length=255)  

    def __str__(self):
        return self.program_name

class Staff_Faculty_Accounts(models.Model):
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=50, choices=[
        ('faculty', 'Faculty'),
        ('laboratory-staff', 'Laboratory Staff')
    ])
    password = models.CharField(max_length=255) 
    status = models.CharField(max_length=50, default='Activated') 

    def __str__(self):
        return f"{self.first_name} {self.surname} ({self.position})"
    
class StudentAccounts(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    proof_of_enrollment = models.FileField(upload_to='enrollment_proofs/')  
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Not Verified')
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.surname} - {self.student_id}"
    
class Archived_Equipments(models.Model): 
    name = models.CharField(max_length=255)  
    category = models.CharField(max_length=255)  
    reason_for_removal = models.TextField()  
    quantity = models.PositiveIntegerField(default=0)  # Set default value to 0
    date_removed = models.DateField(null=True, blank=True)  

    def __str__(self):
        return f"{self.name} - {self.quantity} ({self.category})"
    
class Cart(models.Model):
    name = models.CharField(max_length=255)  
    item = models.CharField(max_length=255)  
    quantity = models.PositiveIntegerField()    

    def __str__(self):
        return f"{self.name} - {self.item} ({self.quantity})"
    
class Borrowing_Records(models.Model):
    name = models.CharField(max_length=255)  
    items_borrowed = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(null=True, blank=True)  
    reservation_date = models.DateField()  
    date_claim = models.DateField(null=True, blank=True)  
    date_returned = models.DateField(null=True, blank=True) 
    position = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Handed In', 'Handed In'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
        ('Void', 'Void'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  

    def __str__(self):
        return f"{self.name} - {self.items_borrowed} ({self.status})"
    
class InventoryItem(models.Model):
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    category = models.CharField(max_length=255)
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    times_borrowed = models.PositiveIntegerField(default=0)  # Set default to 0
    date_added = models.DateField(auto_now_add=True, null=True)  # Allow NULL values if necessary
    last_updated_date = models.DateField(auto_now=True, null=True)  # Allow NULL values
    added_quantity = models.PositiveIntegerField(default=0)  # Keeps track of the quantity added in the last update
    initial_quantity = models.PositiveIntegerField(default=0)  # Keeps track of the quantity added in the last update

    def __str__(self):
        return f"{self.item} - {self.quantity} ({self.category})"


    
class LabtechAccounts(models.Model):
    email = models.EmailField(unique=True)  # Email column (unique)
    password = models.CharField(max_length=255)  # Password column
    first_login = models.BooleanField(default=True)

    def __str__(self):
        return self.email  # Show the email when displaying instances

# Step 2: Use the post_migrate signal to automatically create default Labtech accounts
@receiver(post_migrate)
def create_default_labtech_accounts(sender, **kwargs):
    default_accounts = [
        {'email': 'tupclaboratory@gmail.com', 'password': 'admin'},
        {'email': 'twisyabenitez@gmail.com', 'password': 'admin1'},
        {'email': 'robertoaustria@gmail.com', 'password': 'admin2'},
        {'email': 'yuri.allen.camerino@gmail.com', 'password': 'admin3'},
        {'email': 'aaronayapana30@gmail.com', 'password': 'admin4'},
        {'email': 'cv6913182@gmail.com', 'password': 'admin5'},
        {'email': 'jasperian.denobo@gsfe.tupcavite.edu.ph', 'password': 'admin6'},
        {'email': 'xianerick@gmail.com', 'password': 'admin7'},
        {'email': 'daphdeligero13@gmail.com', 'password': 'admin8'},
        # Add more accounts as needed
    ]

    for account in default_accounts:
        if not LabtechAccounts.objects.filter(email=account['email']).exists():
            LabtechAccounts.objects.create(
                email=account['email'],
                password=account['password']
            )
    
class OTP(models.Model):
    email = models.EmailField(unique=True)  # Email field to associate with the OTP
    otp = models.CharField(max_length=6)  # OTP will be a 6-digit number, so max length is 6
    created_at = models.DateTimeField(auto_now_add=True)  # To track when the OTP was created

    def __str__(self):
        return f"OTP for {self.email}: {self.otp}"
    
    def clean(self):
        # Ensure OTP is numeric
        if not self.otp.isdigit():
            raise ValidationError("OTP must only contain numbers.")
        if len(self.otp) != 6:  # Ensuring OTP is 6 digits
            raise ValidationError("OTP must be exactly 6 digits.")