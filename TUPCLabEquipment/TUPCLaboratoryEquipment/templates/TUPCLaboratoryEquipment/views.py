from datetime import datetime, timedelta, date
import random
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, redirect
from TUPCLaboratoryEquipment.models import Borrowing_Records, Program  
from TUPCLaboratoryEquipment.models import Staff_Faculty_Accounts 
from TUPCLaboratoryEquipment.models import StudentAccounts
from django.http import FileResponse, HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from TUPCLaboratoryEquipment.models import InventoryItem, Archived_Equipments
from django.contrib.auth.hashers import check_password
from TUPCLaboratoryEquipment.models import LabtechAccounts
from django.contrib.auth import authenticate, login
from TUPCLaboratoryEquipment.models import Cart
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from TUPCLaboratoryEquipment.models import OTP
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils.http import urlencode
from secrets import token_urlsafe
from django.utils.timezone import now
import re

# Define your email settings
EMAIL_ADDRESS = "tupclaboratory@gmail.com"
EMAIL_PASSWORD = "wrxx wlxh dlkn gony"

def index(request):
    return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

def force_change_password(request):
    return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

def register_student(request):
    programs = Program.objects.all()

    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        surname = request.POST.get('last-name')
        program_id = request.POST.get('program')
        student_id = request.POST.get('student-id')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        certificate = request.FILES.get('certificate')

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char in "!@#$%^&*()-+=" for char in password):
            messages.warning(request, "Password must be at least 8 characters long and include letters (a-z, A-Z), numbers (0-9), and symbols (!@#$%^&*()-+=).")
            return render(request, 'account-register_student.html', {'programs': programs, 'first_name': first_name, 'surname': surname, 'student_id': student_id, 'email': email, 'program_id': program_id})

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'account-register_student.html', {'programs': programs, 'first_name': first_name, 'surname': surname, 'student_id': student_id, 'email': email, 'program_id': program_id})

        if StudentAccounts.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, 'account-register_student.html', {'programs': programs, 'first_name': first_name, 'surname': surname, 'student_id': student_id, 'email': email, 'program_id': program_id})

        if StudentAccounts.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists!")
            return render(request, 'account-register_student.html', {'programs': programs, 'first_name': first_name, 'surname': surname, 'student_id': student_id, 'email': email, 'program_id': program_id})

        program = Program.objects.get(id=program_id)

        # Generate a unique verification token
        verification_token = token_urlsafe(32)

        student = StudentAccounts.objects.create(
            first_name=first_name,
            surname=surname,
            program=program.program_name,
            student_id=student_id,
            proof_of_enrollment=certificate,
            email=email,
            password=password,  # Hash this in production!
            verification_token=verification_token
        )

        # Send verification email
        try:
            verification_url = request.build_absolute_uri(f"/verify-email/?{urlencode({'token': verification_token})}")
            
            # Create email message with HTML content
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = "Verify Your Email Address"

            body = f"""
            <html>
                <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
                    <table align="center" width="600" style="border-collapse: collapse; background: white; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                        <!-- Header with Image -->
                        <tr>
                            <td align="center" style="padding: 0;">
                                <img src="https://drive.google.com/uc?id=1va5EOjzxjfSwYDaisC1xhTtDdAEzJWt2" alt="TUPC LAB EQUIPMENT BORROWING SYSTEM" style="width: auto; height: 60px; padding: 3px;">
                            </td>
                        </tr>
                        <!-- Title -->
                        <tr>
                            <td align="center" style="padding: 5px; font-size: 18px; font-weight: bold; color: #333;">
                                VERIFY YOUR EMAIL ADDRESS
                            </td>
                        </tr>
                        <!-- Message -->
                        <tr>
                            <td align="center" style="padding: 5px; font-size: 16px; color: #555;">
                                Click the button below to get your email verified. After that, please wait for our administrator to approve your account.
                            </td>
                        </tr>
                        <!-- Verify Button -->
                        <tr>
                            <td align="center" style="padding: 20px;">
                                <a href="{verification_url}" style="
                                    display: inline-block;
                                    padding: 15px 25px;
                                    font-size: 16px;
                                    color: white;
                                    background-color: #800000;
                                    text-decoration: none;
                                    border-radius: 5px;
                                    font-weight: bold;
                                ">VERIFY MY EMAIL</a>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                © 2024 TUPC Laboratory Equipment Borrowing System.
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))


            # Send the email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")
            messages.error(request, "Error sending confirmation email. Please try again.")

        return redirect('index')

    return render(request, 'account-register_student.html', {'programs': programs})

def verify_email(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, "Invalid or missing verification token.")
        return redirect('index')

    student = get_object_or_404(StudentAccounts, verification_token=token)

    if student.email_verified:
        messages.info(request, "Your email is already verified.")
    else:
        # Update email verification status and the "status" column
        student.email_verified = True
        student.verification_token = None  # Clear the token after verification
        student.status = "Verified"  # Update the "status" column
        student.save()

        # Send email notification of successful verification
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = student.email
            msg['Subject'] = "Email Verification Successful"

            # Email body
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
                    <table align="center" width="600" style="border-collapse: collapse; background: white; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                    <!-- Header Section with Image -->
                        <tr>
                            <td align="center" style="padding: 0;">
                                <img src="https://drive.google.com/uc?id=1va5EOjzxjfSwYDaisC1xhTtDdAEzJWt2" alt="TUPC LAB EQUIPMENT BORROWING SYSTEM" style="width: auto; height: 60px; padding: 3px;">
                            </td>
                        </tr>
                        <!-- Title -->
                        <tr>
                            <td align="center" style="padding: 5px; font-size: 18px; font-weight: bold; color: #333;">
                                EMAIL VERIFICATION SUCCESSFUL
                            </td>
                        </tr>
                        <!-- Message -->
                        <tr>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 5px; font-size: 16px; color: #555;">
                                <p>Your email verification was <strong style="color: green;">successful</strong>! Thank you for confirming your email address.</p>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 5px; font-size: 16px; color: #555;">
                                Please wait while our admins review your account. You will receive another email once your account has been approved.
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 5px; font-size: 16px; color: #555;">
                                Thank you,<br>The Team
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                © 2024 TUPC Laboratory Equipment Borrowing System.
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))


            # Send the email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, student.email, msg.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")
            messages.warning(request, "Email verification successful, but there was an error sending the follow-up email.")

        messages.success(request, "Your email has been successfully verified! Please check your email for further instructions.")

    return redirect('index')

def student_homepage(request):
    if 'user_id' in request.session and request.session.get('user_type') == 'student':
        user_id = request.session['user_id']

        try:
            student = StudentAccounts.objects.get(id=user_id)

            # Fetch the most borrowed items separated by category
            glassware_items = InventoryItem.objects.filter(category='glasswares').order_by('-times_borrowed')[:3]
            labtools_items = InventoryItem.objects.filter(category='labtools').order_by('-times_borrowed')[:3]
            heavy_equipments_items = InventoryItem.objects.filter(category='heavyequipments').order_by('-times_borrowed')[:3]

            context = {
                'first_name': student.first_name,
                'student_id': student.student_id,  # Include the student ID
                'position': 'STUDENT',  # Add the position
                'glassware_items': glassware_items,
                'labtools_items': labtools_items,
                'heavy_equipments_items': heavy_equipments_items,
            }

            return render(request, 'TUPCLaboratoryEquipment/student_homepage.html', context)

        except StudentAccounts.DoesNotExist:
            messages.error(request, "Student account not found.")
            return redirect('main_homepage')

    return redirect('main_homepage')



def faculty_homepage(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'faculty':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as faculty

    # Get the top 3 items with the highest quantity for each category
    glassware_items = InventoryItem.objects.filter(category='glasswares').order_by('-times_borrowed')[:3]
    labtools_items = InventoryItem.objects.filter(category='labtools').order_by('-times_borrowed')[:3]
    heavy_equipments_items = InventoryItem.objects.filter(category='heavyequipments').order_by('-times_borrowed')[:3]

    # Base context with inventory items
    context = {
        'glassware_items': glassware_items,
        'labtools_items': labtools_items,
        'heavy_equipments_items': heavy_equipments_items,
        'first_name': request.user.first_name if request.user.is_authenticated else "Guest",
    }

    # Check if 'user_id' is in session and retrieve staff details if available
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        
        try:
            staff = Staff_Faculty_Accounts.objects.get(id=user_id)
            
            # Add staff-specific data to the context
            context.update({
                'first_name': staff.first_name,
                'position': 'FACULTY',  # Add the position for faculty
            })

            return render(request, 'TUPCLaboratoryEquipment/faculty_homepage.html', context)

        except Staff_Faculty_Accounts.DoesNotExist:
            messages.error(request, "Staff account not found.")
            return redirect('main_homepage')

    # Redirect to the main homepage if 'user_id' is not in session
    return redirect('main_homepage')


def cart_student(request):
    if 'user_id' in request.session and request.session.get('user_type') == 'student':
        user_id = request.session['user_id']
        
        try:
            student = StudentAccounts.objects.get(id=user_id)
            cart_items = Cart.objects.filter(name=student.first_name + ' ' + student.surname)

            today_date = date.today()

            # Check if the cart is empty
            if not cart_items.exists():
                if request.method == 'POST' and 'reservation_date' in request.POST:
                    messages.error(request, "Your cart is empty. Please add items to the cart before making a reservation.")
                    return redirect('cart_student')

            # Check if it's a POST request for removing an item
            if request.method == 'POST':
                if 'remove_item_id' in request.POST:
                    remove_item_id = request.POST.get('remove_item_id')
                    # Get and delete the cart item
                    cart_item = get_object_or_404(Cart, id=remove_item_id)
                    cart_item.delete()
                    messages.success(request, f"{cart_item.item} removed from cart.")
                    return redirect('cart_student')  # Redirect to refresh the page and update cart items

                # Reservation handling
                elif 'reservation_date' in request.POST:
                    reservation_date = request.POST.get('reservation_date')
                    if reservation_date:
                        reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()

                        # Check if the reservation_date is a Friday
                        if reservation_date.weekday() == 4:  # Friday is 4 in Python's weekday()
                            date_returned = reservation_date + timedelta(days=3)  # Add 2 days to skip the weekend
                        else:
                            date_returned = reservation_date + timedelta(days=1)  # Default: 1 day return time

                        # Check if there is sufficient stock for each item before proceeding with the borrowing process
                        insufficient_stock = False
                        for cart_item in cart_items:
                            inventory_item = InventoryItem.objects.get(item=cart_item.item)
                            if inventory_item.quantity < cart_item.quantity:
                                messages.warning(request, f"Insufficient stock for {inventory_item.item}.")
                                insufficient_stock = True
                                break  # Stop further processing if any item has insufficient stock

                        # Only proceed with creating borrowing records and sending email if there is sufficient stock
                        if not insufficient_stock:
                            # Create the borrowing record for each item in the cart
                            for cart_item in cart_items:
                                Borrowing_Records.objects.create(
                                    name=student.first_name + ' ' + student.surname,
                                    items_borrowed=cart_item.item,
                                    quantity=cart_item.quantity,
                                    reservation_date=date.today(),
                                    date_claim=reservation_date,
                                    date_returned=date_returned,
                                    position="student",
                                    status="Pending",
                                    email=student.email
                                )

                                # Update the inventory for each borrowed item
                                inventory_item = InventoryItem.objects.get(item=cart_item.item)
                                inventory_item.quantity -= cart_item.quantity
                                inventory_item.times_borrowed += cart_item.quantity
                                inventory_item.save()

                            # Send an email notification to the student
                            subject = "Reservation Request Submitted"
                            body = f"""
                                <html>
                                    <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0; background-color: #f9f9f9;">
                                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                            <!-- Header Section -->
                                            <tr>
                                                <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                                    <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                                        alt="Header Image" 
                                                        style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                                                </td>
                                            </tr>
                                            <!-- Body Content -->
                                            <tr>
                                                <td style="padding: 30px; text-align: center; color: #333333;">
                        
                                                    <p style="font-size: 16px; line-height: 1.5; margin: 0 0 15px;">
                                                        Your reservation request has been successfully sent to the laboratory technician and is awaiting confirmation.
                                                    </p>
                                                    <p style="font-size: 16px; line-height: 1.5; margin: 0 0 15px;">
                                                        <strong>Reservation Date:</strong> {reservation_date}
                                                    </p>
                                                    <p style="font-size: 16px; line-height: 1.5; margin: 0 0 15px;">
                                                        You will be notified once your reservation is confirmed.
                                                    </p>
                                                </td>
                                            </tr>
                                            <!-- Footer Section -->
                                            <tr>
                                                <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                                    © 2024 TUPC Laboratory Equipment Borrowing System.
                                                </td>
                                            </tr>
                                        </table>
                                    </body>
                                </html>
                            """

                            # Set up the email
                            msg = MIMEMultipart()
                            msg['From'] = EMAIL_ADDRESS
                            msg['To'] = student.email
                            msg['Subject'] = subject
                            msg.attach(MIMEText(body, 'html'))

                            # Send the email via SMTP
                            try:
                                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                                    server.starttls()  # Secure the connection
                                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                                    server.sendmail(EMAIL_ADDRESS, student.email, msg.as_string())
                                messages.success(request, "Reservation successful! A confirmation email has been sent.")
                            except Exception as e:
                                messages.error(request, f"Error sending email: {e}")

                            # Delete the items from the cart
                            cart_items.delete()
                            return redirect('cart_student')
                
                # Check if the item_id is passed (added part from your code)
                item_id = request.POST.get('item_id')
                reservation_date = request.POST.get('reservation_date')

                if item_id:
                    # Check if the item is already in the user's tray
                    existing_item = Cart.objects.filter(name=student.first_name + ' ' + student.surname, item=item_id).first()

                    if existing_item:
                        messages.warning(request, "This item is already in your tray.")
                    else:
                        # If item doesn't exist in tray, add it
                        new_cart_item = Cart(name=student.first_name + ' ' + student.surname, item=item_id, quantity=1)  # Assuming quantity is 1
                        new_cart_item.save()
                        messages.success(request, "Item added to tray.")

                # Handle the reservation date if provided
                if reservation_date:
                    # Process the reservation logic (e.g., save reservation)
                    messages.success(request, "Reservation successfully made.")

            context = {
                'cart_items': cart_items,
                'today_date': today_date,
            }

            return render(request, 'TUPCLaboratoryEquipment/cart_student.html', context)

        except StudentAccounts.DoesNotExist:
            messages.error(request, "Student account not found.")
            return redirect('main_homepage')

    return redirect('main_homepage')

def cart_faculty(request):
    if 'user_id' in request.session and request.session.get('user_type') == 'faculty':
        user_id = request.session['user_id']
        
        try:
            faculty = Staff_Faculty_Accounts.objects.get(id=user_id)
            full_name = faculty.first_name + ' ' + faculty.surname + ' - faculty'
            cart_items = Cart.objects.filter(name=full_name)

            # Check if the cart is empty
            if not cart_items.exists():
                if request.method == 'POST' and 'reservation_date' in request.POST:
                    messages.error(request, "Your cart is empty. Please add items to the cart before making a reservation.")
                    return redirect('cart_faculty')

            if request.method == 'POST':
                # Handle quantity update
                if 'update_quantity' in request.POST:
                    item_id = request.POST.get('id')
                    new_quantity = request.POST.get('quantity')

                    if item_id and new_quantity:
                        try:
                            cart_item = Cart.objects.get(id=item_id, name=full_name)
                            cart_item.quantity = int(new_quantity)
                            cart_item.save()
                            messages.success(request, "Quantity updated successfully.")
                        except Cart.DoesNotExist:
                            messages.error(request, "Cart item not found.")

                # Handle item deletion
                elif 'delete_item' in request.POST:
                    delete_item_id = request.POST.get('delete_item_id')
                    if delete_item_id:
                        cart_item = get_object_or_404(Cart, id=delete_item_id, name=full_name)
                        cart_item.delete()
                        messages.success(request, f"{cart_item.item} removed from cart.")
                        return redirect('cart_faculty')  # Redirect to refresh the page and update cart items

                # Handle reservation
                elif 'reservation_date' in request.POST:
                    reservation_date = request.POST.get('reservation_date')
                    if reservation_date:
                        reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()

                        # Check if the reservation_date is a Friday
                        if reservation_date.weekday() == 4:  # Friday is 4 in Python's weekday()
                            date_returned = reservation_date + timedelta(days=3)  # Add 2 days to skip the weekend
                        else:
                            date_returned = reservation_date + timedelta(days=1)  # Default: 1 day return time

                        # Check if there is sufficient stock for each item before proceeding with the borrowing process
                        insufficient_stock = False
                        for cart_item in cart_items:
                            inventory_item = InventoryItem.objects.get(item=cart_item.item)
                            if inventory_item.quantity < cart_item.quantity:
                                messages.warning(request, f"Insufficient stock for {inventory_item.item}.")
                                insufficient_stock = True
                                break  # Stop further processing if any item has insufficient stock

                        # Only proceed with creating borrowing records and sending email if there is sufficient stock
                        if not insufficient_stock:
                            # Create the borrowing record for each item in the cart
                            for cart_item in cart_items:
                                Borrowing_Records.objects.create(
                                    name=full_name,
                                    items_borrowed=cart_item.item,
                                    quantity=cart_item.quantity,
                                    reservation_date=date.today(),
                                    date_claim=reservation_date,
                                    date_returned=date_returned,
                                    position="faculty",
                                    status="Pending",
                                    email=faculty.email  # Save the faculty's email here
                                )

                                # Update the inventory for each borrowed item
                                inventory_item = InventoryItem.objects.get(item=cart_item.item)
                                inventory_item.quantity -= cart_item.quantity
                                inventory_item.times_borrowed += cart_item.quantity
                                inventory_item.save()

                            # Send an email notification to the faculty
                            items_borrowed = ", ".join([f"{item.item} (Qty: {item.quantity})" for item in cart_items])  # Generate items list for email
                            subject = "Reservation Request Submitted"
                            body = f"""
                                <html>
                                    <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0; background-color: #f9f9f9;">
                                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                            <!-- Header Section -->
                                            <tr>
                                                <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                                    <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                                        alt="Header Image" 
                                                        style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                                                </td>
                                            </tr>
                                            <!-- Body Content -->
                                            <tr>
                                                <td style="padding: 30px; text-align: center; color: #333333;">
                        
                                                    <p style="font-size: 16px; line-height: 1.5; margin: 0 0 15px;">
                                                        Your reservation request has been successfully sent to the laboratory technician and is awaiting confirmation.
                                                    </p>
                                                    <p style="font-size: 16px; line-height: 1.5; margin: 0 0 15px;">
                                                        <strong>Reservation Date:</strong> {reservation_date}
                                                    </p>
                                                    <p style="font-size: 16px; line-height: 1.5; margin: 0 0 15px;">
                                                        You will be notified once your reservation is confirmed.
                                                    </p>
                                                </td>
                                            </tr>
                                            <!-- Footer Section -->
                                            <tr>
                                                <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                                    © 2024 TUPC Laboratory Equipment Borrowing System.
                                                </td>
                                            </tr>
                                        </table>
                                    </body>
                                </html>
                                """
                            # Set up the email
                            msg = MIMEMultipart()
                            msg['From'] = EMAIL_ADDRESS
                            msg['To'] = faculty.email
                            msg['Subject'] = subject
                            msg.attach(MIMEText(body, 'html'))

                            # Send the email via SMTP
                            try:
                                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                                    server.starttls()  # Secure the connection
                                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                                    server.sendmail(EMAIL_ADDRESS, faculty.email, msg.as_string())
                                messages.success(request, "Reservation successful! A confirmation email has been sent.")
                            except Exception as e:
                                messages.error(request, f"Error sending email: {e}")

                            # Delete the items from the cart
                            cart_items.delete()
                            return redirect('cart_faculty')

            context = {
                'cart_items': cart_items
            }

            return render(request, 'TUPCLaboratoryEquipment/cart_faculty.html', context)

        except Staff_Faculty_Accounts.DoesNotExist:
            messages.error(request, "Faculty account not found.")
            return redirect('main_homepage')

    return redirect('main_homepage')

def change_password(request):
    if 'user_id' not in request.session:
        return redirect('main_homepage')  # Redirect to the login page if not logged in

    if request.method == 'POST':
        old_password = request.POST.get('oldPassword')
        new_password = request.POST.get('newPassword')
        confirm_new_password = request.POST.get('confirmNewPassword')

        print("Change password POST request received")

        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')

        print(f"User Type: {user_type}, User ID: {user_id}")

        if user_type == 'student':
            try:
                user = StudentAccounts.objects.get(id=user_id)
                redirect_url = 'student_homepage'
            except StudentAccounts.DoesNotExist:
                messages.error(request, "Student account not found.")
                return redirect('main_homepage')

        elif user_type == 'faculty':
            try:
                user = Staff_Faculty_Accounts.objects.get(id=user_id, position='faculty')
                redirect_url = 'faculty_homepage'
            except Staff_Faculty_Accounts.DoesNotExist:
                messages.error(request, "Faculty account not found.")
                return redirect('main_homepage')

        elif user_type == 'staff' or user_type == 'labstaff':  # Include 'labstaff' type check
            try:
                user = Staff_Faculty_Accounts.objects.get(id=user_id, position='laboratory-staff')
                redirect_url = 'labstaff_homepage'
            except Staff_Faculty_Accounts.DoesNotExist:
                messages.error(request, "Staff account not found.")
                return redirect('main_homepage')

        elif user_type == 'labtech':
            try:
                user = LabtechAccounts.objects.get(id=user_id)
                redirect_url = 'labtech_homepage'
            except LabtechAccounts.DoesNotExist:
                messages.error(request, "Labtech account not found.")
                return redirect('main_homepage')

        else:
            messages.error(request, "Invalid user type.")
            return redirect('main_homepage')

        # Validate the old password
        if user.password != old_password:
            print("Old password does not match")
            messages.error(request, "Old password is incorrect.")
            return render(request, 'TUPCLaboratoryEquipment/change-password.html')

        # Ensure new password is not the same as the old password
        if new_password == old_password:
            print("New password is the same as old password")
            messages.error(request, "New password cannot be the same as the old password.")
            return render(request, 'TUPCLaboratoryEquipment/change-password.html')

        # Confirm the new password matches the confirmation input
        if new_password != confirm_new_password:
            print("New passwords do not match")
            messages.error(request, "New passwords do not match.")
            return render(request, 'TUPCLaboratoryEquipment/change-password.html')

        password_regex = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()\-+=])[A-Za-z\d!@#$%^&*()\-+=]{8,}$'
        if not re.match(password_regex, new_password):
            messages.warning(request, "Password must be at least 8 characters long and include letters (a-z, A-Z), numbers (0-9), and symbols (!@#$%^&*()-+=).")
            return render(request, 'TUPCLaboratoryEquipment/change-password.html')
        
        # Update the password and save
        user.password = new_password
        if user_type == 'labtech':
            user.first_login = False  # Mark first_login as False after the password change for labtechs
        user.save()
        print("Password updated successfully")
        return redirect(redirect_url)

    return render(request, 'TUPCLaboratoryEquipment/change-password.html')

def main_homepage(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print("Login attempt with email:", email)

        try:
            user = LabtechAccounts.objects.get(email=email)
            print("Labtech account found for email:", email)

            if password == user.password:
                if user.first_login:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'labtech'
                    print("First login detected, redirecting to change password")
                    return redirect('change_password')  # Redirect to the change password page

                request.session['user_id'] = user.id
                request.session['user_type'] = 'labtech'
                print("Labtech login successful")
                return redirect('labtech_homepage')
            else:
                print("Labtech password mismatch")
                messages.error(request, "Invalid password for laboratory technician account.")
                return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

        except LabtechAccounts.DoesNotExist:
            print("Labtech account not found for email:", email)

            try:
                student = StudentAccounts.objects.get(email=email)
                print("Student account found for email:", email)

                if student.status != 'Activated':
                    messages.error(request, "Your account is not activated.")
                    return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

                if password == student.password:
                    request.session['user_id'] = student.id
                    request.session['user_type'] = 'student'
                    request.session['first_name'] = student.first_name
                    # Set session expiry after 15 minutes for student
                    if request.session.get('user_type') == 'student':
                        request.session.set_expiry(timedelta(minutes=15))
                        print("Session set to expire after 15 minutes for student.")
                    print("Student login successful")
                    return redirect('student_homepage')
                else:
                    print("Student password mismatch")
                    messages.error(request, "Invalid Student email or password.")
                    return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

            except StudentAccounts.DoesNotExist:
                print("Student account not found for email:", email)

                try:
                    acc = Staff_Faculty_Accounts.objects.get(email=email)
                    print("Faculty/Labstaff account found for email:", email)

                    if acc.status != 'Activated':  # Check if the account is activated
                        messages.error(request, "Your account is not activated.")
                        return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')


                    if password == acc.password:
                        request.session['user_id'] = acc.id
                        request.session['first_name'] = acc.first_name
                        # Set session expiry after 15 minutes for faculty
                        if acc.position == 'faculty':
                            request.session['user_type'] = 'faculty'
                            request.session.set_expiry(timedelta(minutes=15))
                            print("Session set to expire after 15 minutes for faculty.")
                            print("Faculty login successful")
                            return redirect('faculty_homepage')
                        elif acc.position == 'laboratory-staff':
                            request.session['user_type'] = 'labstaff'
                            print("Lab Staff login successful")
                            return redirect('labstaff_homepage')
                        else:
                            messages.error(request, "Unrecognized position.")
                            return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')
                    else:
                        print("Faculty/Labstaff password mismatch")
                        messages.error(request, "Invalid Faculty/Laboratory staff email or password.")
                        return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

                except Staff_Faculty_Accounts.DoesNotExist:
                    print("Faculty account not found for email:", email)
                    messages.error(request, "No account found with this email.")
                    return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')

    return render(request, 'TUPCLaboratoryEquipment/main-homepage.html')


def labtech_homepage(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech
    
    sort_option = request.GET.get('sort', 'all')  # Default to 'all'

    # Filter inventory items based on the selected sort option
    if sort_option == 'category':
        inventory_items = InventoryItem.objects.filter(category='glasswares')
    elif sort_option == 'name':
        inventory_items = InventoryItem.objects.filter(category='labtools')
    elif sort_option == 'quantity':
        inventory_items = InventoryItem.objects.filter(category='heavyequipments')
    else:
        inventory_items = InventoryItem.objects.all()

    # Filter borrowing requests with status "Pending" and get the count
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()

    # Check if the request method is POST for handling the accept/reject actions
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        print(f"Action: {action}, Request ID: {request_id}")

        # Get the borrowing record and update its status based on the action
        borrow_record = get_object_or_404(Borrowing_Records, id=request_id)
        if action == 'accept':
            borrow_record.status = "Accepted"
            borrow_record.save()

            # Send an email to the user whose request was accepted
            student_email = borrow_record.email  # Fetch the student's email from the Borrowing_Records
            subject = "Borrow Request Approved"
    
            # HTML body for the email
            body = f"""
            <html>
                <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <!-- Header Section with Radial Gradient Background -->
                        <tr>
                            <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                    alt="Header Image" 
                                    style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                            </td>
                        </tr>
                        <!-- Body Content -->
                        <tr>
                            <td style="padding: 30px; text-align: left; color: #333333;">
                                <p style="font-size: 16px; margin: 2px 0; font-weight: 800; text-align: center; color: #333333; line-height: 1.2;">
                                    Your Borrow Request has been <span style="color: #28a745; font-weight: bold; text-transform: uppercase;">APPROVED</span>.
                                </p>

                                <p style="font-size: 15px; margin-bottom: 0; text-align: center; color: #333333;"><strong>Item Borrowed:</strong></p>
                                <p style="font-size: 18px; text-align: center; font-weight: 700; color: #333333;">
                                    {"".join([f"{item}" for item in borrow_record.items_borrowed])}
                                </p>
                                <div style="text-align: center; margin: 20px 0;">
                                    <p style="font-size: 15px; margin: 10px 0; color: #333333;">You can now proceed to pick up the items from the lab.</p>
                                    <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                        If you fail to claim the item(s) you borrowed by the return date, your reservation will be automatically voided.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        <!-- Footer Section with Copyright and Small Logo -->
                        <tr>
                            <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                 © 2024 TUPC Laboratory Equipment Borrowing System.
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            # Set up the email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = student_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))  # Specify 'html' instead of 'plain' for HTML content


            # Send the email via SMTP
            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()  # Secure the connection
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, student_email, msg.as_string())
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")

            return JsonResponse({'status': 'accepted'}, status=200)
        elif action == 'reject':
            borrow_record.status = "Rejected"
            borrow_record.save()

            # Send an email to the user whose request was rejected
            student_email = borrow_record.email  # Fetch the student's email from the Borrowing_Records
            subject = "Reservation Request Declined"
            body = f"""
            <html>
                <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <!-- Header Section with Radial Gradient Background -->
                        <tr>
                            <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                    alt="TUPC Laboratory Equipment Borrowing System" 
                                    style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                            </td>
                        </tr>
                        <!-- Body Content -->
                        <tr>
                            <td style="padding: 30px; text-align: center; color: #333333;">
                                <p style="font-size: 16px; margin: 3px 0; color: #333333;">
                                     We regret to inform you that your reservation request has been <strong style="color: #ff0000;">REJECTED</strong>
                                </p>
                                <p style="font-size: 15px; margin-bottom: -5px; text-align: center; color: #333333;"><strong>Items Borrowed:</strong></p>
                                <p style="font-size: 18px; text-align: center; font-weight: 700; color: #333333;">
                                    {borrow_record.items_borrowed}
                                </p>
                                <div style="text-align: center; margin: 10px 0;">
                                    <p style="font-size: 15px; margin: 5px 0; color: #333333;">
                                        If you have any questions or require further clarification, please feel free to visit the laboratory.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        <!-- Footer Section with Copyright and Automated Message -->
                        <tr>
                            <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                © 2024 TUPC Laboratory Equipment Borrowing System.
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            # Set up the email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = student_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))


            # Send the email via SMTP
            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()  # Secure the connection
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, student_email, msg.as_string())
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")

            # Update the inventory quantity based on the quantity in the Borrowing_Records
            # Use 'item' instead of 'name' for the InventoryItem lookup
            inventory_item = get_object_or_404(InventoryItem, item=borrow_record.items_borrowed)
            inventory_item.quantity += borrow_record.quantity  # Add the rejected quantity back to inventory
            inventory_item.save()

            return JsonResponse({'status': 'rejected'}, status=200)

    # Pass context data to the template
    context = {
        'inventory_items': inventory_items,
        'borrow_requests': borrow_requests,
        'sort_option': sort_option,  # Include the selected sort option in context
        'pending_count': pending_count,  # Pass pending count to context
    }

    return render(request, 'TUPCLaboratoryEquipment/labtech_homepage.html', context)

from django.db.models import F
from django.utils.timezone import now


def add_equipment(request):
    # Ensure the user is logged in and is a lab technician
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech

    # Fetch pending borrow requests
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()

    if request.method == 'POST':
        # Get form data
        item = request.POST.get('item')
        quantity = request.POST.get('quantity')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Validate required fields
        if not item or not quantity or not category or not image:
            messages.error(request, "All fields are required.")
            return render(request, 'TUPCLaboratoryEquipment/add-equipment_labtech.html', {
                'borrow_requests': borrow_requests,
                'pending_count': pending_count,
            })

        # Ensure the quantity is a valid integer
        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "Quantity must be a valid number.")
            return render(request, 'TUPCLaboratoryEquipment/add-equipment_labtech.html', {
                'borrow_requests': borrow_requests,
                'pending_count': pending_count,
            })

        # Check if an item with the same name and category already exists
        existing_item = InventoryItem.objects.filter(item=item, category=category).first()
        if existing_item:
            # Update the existing item's quantity and added quantity
            if image:
                existing_item.image = image  # Update image if provided
            existing_item.quantity += quantity  # Increment current quantity
            existing_item.added_quantity += quantity  # Increment added quantity
            existing_item.last_updated_date = now().date()  # Update last_updated_date
            existing_item.save()
            messages.success(request, f"Quantity updated for existing item '{item}' in category '{category}'.")
        else:
            # Create a new inventory item with an initial quantity
            InventoryItem.objects.create(
                image=image,
                item=item,
                initial_quantity=quantity,  # Store initial quantity
                quantity=quantity,  # Set current quantity
                category=category,
                date_added=now().date()  # Set date added
            )
            messages.success(request, "Equipment added successfully!")

        # Redirect to the same page after submission
        return redirect('add_equipment')

    # Render the form template
    return render(request, 'TUPCLaboratoryEquipment/add-equipment_labtech.html', {
        'borrow_requests': borrow_requests,
        'pending_count': pending_count,
    })


def remove_equipment(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech
    
    categories = InventoryItem.objects.values_list('category', flat=True).distinct()
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()
    selected_category = request.GET.get('category')
    equipment_list = InventoryItem.objects.filter(category=selected_category) if selected_category else []

    if request.method == 'POST':
        equipment_id = request.POST.get('equipment')
        reason = request.POST.get('reason')
        quantity_to_remove = int(request.POST.get('quantity'))

        equipment = InventoryItem.objects.get(id=equipment_id)

        if quantity_to_remove > equipment.quantity:
            messages.error(request, "Quantity to remove exceeds available stock.")
            return redirect('remove_equipment')

        if quantity_to_remove == equipment.quantity:
            equipment.delete()  
        else:
            equipment.quantity -= quantity_to_remove
            equipment.save()

        Archived_Equipments.objects.create(
            name=equipment.item,
            category=equipment.category,
            reason_for_removal=reason,
            quantity=quantity_to_remove,  
            date_removed=date.today()  # Current date without time
        )

        messages.success(request, "Equipment removed and archived successfully.")
        return redirect('remove_equipment')

    context = {
        'categories': categories,
        'equipment_list': equipment_list,
        'borrow_requests': borrow_requests,
        'pending_count': pending_count,
    }
    return render(request, 'TUPCLaboratoryEquipment/remove-equipment_labtech.html', context)

def borrowing_records(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech
    
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()
    
    # Fetch all records
    all_records = Borrowing_Records.objects.all()

    context = {
        'records': all_records,
        'borrow_requests': borrow_requests,
        'pending_count': pending_count,
    }

    # Pass the context to the normal rendering of the page
    return render(request, 'TUPCLaboratoryEquipment/borrowing-records.html', context)

from django.db.models import F, Sum

def generate_report(request):
    # Extract query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status', 'all')

    # Convert start_date to datetime object and format it
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    formatted_start_date = start_date_obj.strftime('%B %Y') if start_date_obj else 'All Time'

    # Filter records based on the query parameters
    records = Borrowing_Records.objects.all()
    if start_date_obj and end_date_obj:
        records = records.filter(date_claim__range=[start_date_obj, end_date_obj])
    if status != 'all':
        records = records.filter(status=status)

    # Summary Calculations
    total_borrowing_records = records.count()
    total_items_borrowed = records.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Removed Equipment summary
    removed_equipment = Archived_Equipments.objects.filter(date_removed__range=[start_date_obj, end_date_obj])
    total_removed_equipment = removed_equipment.count()
    total_quantity_removed = removed_equipment.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Top 3 Most Borrowed Items
    top_borrowed_items = InventoryItem.objects.all().order_by('-times_borrowed')[:3]
    # Added Equipment
    added_equipment = InventoryItem.objects.filter(
        date_added__range=[start_date_obj, end_date_obj]
    ).values('item', 'initial_quantity', 'date_added')


        # Updated Quantities
    updated_quantities = InventoryItem.objects.filter(
        last_updated_date__range=[start_date_obj, end_date_obj]
    ).annotate(
        quantity_added=F('added_quantity')
    ).values('item', 'quantity_added', 'last_updated_date', 'quantity')



    # Context for the PDF template
    context = {
        'records': records,
        'removed_equipment': removed_equipment,
        'total_borrowing_records': total_borrowing_records,
        'total_items_borrowed': total_items_borrowed,
        'total_removed_equipment': total_removed_equipment,
        'total_quantity_removed': total_quantity_removed,
        'top_borrowed_items': top_borrowed_items,
        'added_equipment': added_equipment,  # Added equipment data
        'updated_quantities': updated_quantities,  # Updated quantities data
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'report_header': f"GENERATED REPORT FOR {formatted_start_date}".upper(),  # Pass the formatted month and year
    }

    # Render HTML to PDF
    html_content = render_to_string('TUPCLaboratoryEquipment/borrowing-records-pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="borrowing_records.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


def account_register(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech
    
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()

    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        surname = request.POST.get('last-name')
        email = request.POST.get('email')
        position = request.POST.get('position')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password') 

        password_regex = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()\-+=]).{8,}$'

        if first_name and surname and email and position and password:
            if position.lower() == "laboratory-staff":  # Case insensitive comparison
                pass

            if Staff_Faculty_Accounts.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. Please use a different email.")
                return render(request, 'TUPCLaboratoryEquipment/account-register.html', {'borrow_requests': borrow_requests})
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match. Please try again.")
                return render(request, 'TUPCLaboratoryEquipment/account-register.html', {'borrow_requests': borrow_requests})

            if not re.match(password_regex, password):
                messages.error(request, "Password must be at least 8 characters long and include letters (a-z, A-Z), numbers (0-9), and symbols (!@#$%^&*()-+=).")
                return render(request, 'TUPCLaboratoryEquipment/account-register.html', {'borrow_requests': borrow_requests})
            
            account = Staff_Faculty_Accounts.objects.create(
                first_name=first_name,
                surname=surname,
                email=email,
                position=position,
                password=password  
            )

            messages.success(request, "Account registered successfully.")
            return render(request, 'TUPCLaboratoryEquipment/account-register.html') 

    context = {
        'borrow_requests': borrow_requests,
        'pending_count': pending_count,
    }

    return render(request, 'TUPCLaboratoryEquipment/account-register.html', context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email exists in any of the tables
        user = None
        if LabtechAccounts.objects.filter(email=email).exists():
            user = LabtechAccounts.objects.get(email=email)
        elif Staff_Faculty_Accounts.objects.filter(email=email).exists():
            user = Staff_Faculty_Accounts.objects.get(email=email)
        elif StudentAccounts.objects.filter(email=email).exists():
            user = StudentAccounts.objects.get(email=email)

        if user:
            # Generate a 6-digit OTP
            otp_code = random.randint(100000, 999999)
            
            # Check if an OTP already exists for this email
            otp, created = OTP.objects.get_or_create(email=email)
            otp.otp = otp_code
            otp.created_at = datetime.now()
            otp.save()

            # Send OTP email
            try:
                # Set up the server
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

                # Create the email
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = email
                msg['Subject'] = 'Your OTP for Password Reset'

                # Using HTML to make OTP bold
                body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <tr>
                            <td align="center" style="padding: 0;">
                                <img src="https://drive.google.com/uc?id=1va5EOjzxjfSwYDaisC1xhTtDdAEzJWt2" alt="TUPC LAB EQUIPMENT BORROWING SYSTEM" style="width: auto; height: 60px; padding: 3px;">
                            </td>
                        </tr>
                            <!-- Message Content -->
                            <tr>
                                <td style="padding: 20px; text-align: center; color: #333333;">
                                    <p style="font-size: 18px; margin-bottom: 5px; font-weight: bold; color: #1a1a1a;">To reset your password, use the OTP below:</p>
                                    <p style="font-size: 36px; font-weight: bold; color: #ff0000; margin: 0;">{otp_code}</p>
                                    <p style="font-size: 15px; color: #666666; margin-top: -5px;">If you did not request this, please ignore this email.</p>
                                </td>
                            </tr>
                            <!-- Footer Section with Copyright and Small Logo -->
                            <tr>
                                <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                    © 2024 TUPC Laboratory Equipment Borrowing System.
                                </td>
                            </tr>
                        </table>
                    </body>
                </html>
                """
                msg.attach(MIMEText(body, 'html'))  # Notice the 'html' MIME type

                # Send the email
                server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
                server.quit()

                # Return success response
                return JsonResponse({'status': 'success', 'message': 'OTP sent to your email.'}, status=200)

            except Exception as e:
                print(f"Error sending email: {e}")
                return JsonResponse({'status': 'error', 'message': 'Error sending OTP email. Please try again later.'}, status=500)

        else:
            return JsonResponse({'status': 'error', 'message': 'Email not found in our records.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def forgot_passwordotp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_code = request.POST.get('otp_code')

        # Check if OTP exists for the given email
        try:
            otp = OTP.objects.get(email=email, otp=otp_code)

            # OTP is valid, proceed to open the change password modal
            return JsonResponse({'status': 'success', 'message': 'OTP verified. Proceed to reset password.'}, status=200)
        
        except OTP.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP. Please try again.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def forgot_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')

        # Check if passwords match
        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'}, status=400)

        # Find the user by email in any of the tables
        user = None
        if LabtechAccounts.objects.filter(email=email).exists():
            user = LabtechAccounts.objects.get(email=email)
        elif Staff_Faculty_Accounts.objects.filter(email=email).exists():
            user = Staff_Faculty_Accounts.objects.get(email=email)
        elif StudentAccounts.objects.filter(email=email).exists():
            user = StudentAccounts.objects.get(email=email)

        if user:
            # Update the password (without hashing it)
            user.password = new_password
            user.save()

            # Delete OTP record
            OTP.objects.filter(email=email).delete()

            # Return success response
            return JsonResponse({'status': 'success', 'message': 'Password updated successfully.'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Email not found in our records.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def glassware_page(request):
    if 'user_id' not in request.session:
        return redirect('main_homepage')  # Redirect to the login page if not logged in
    
    glassware_items = InventoryItem.objects.filter(category='glasswares')

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = InventoryItem.objects.get(id=item_id)

            if 'user_id' in request.session and 'user_type' in request.session:
                user_id = request.session['user_id']
                user_type = request.session['user_type']
                user_name = None  

                if user_type == 'student':
                    try:
                        student = StudentAccounts.objects.get(id=user_id)
                        user_name = f"{student.first_name} {student.surname}"

                        # Check if the item is already in the cart for this student
                        if Cart.objects.filter(name=user_name, item=item.item).exists():
                            messages.error(request, "You have already added this item to your tray.")
                            return redirect(request.META.get('HTTP_REFERER', 'glassware'))

                    except StudentAccounts.DoesNotExist:
                        messages.error(request, "Student account not found.")
                        return redirect('main_homepage')

                elif user_type in ['faculty', 'labstaff']:
                    try:
                        faculty = Staff_Faculty_Accounts.objects.get(id=user_id, position=user_type)
                        user_name = f"{faculty.first_name} {faculty.surname} - {faculty.position}"  
                    except Staff_Faculty_Accounts.DoesNotExist:
                        messages.error(request, "Faculty or Lab Staff account not found.")
                        return redirect('main_homepage')

                if user_name:
                    # Check if the item is already in the cart for this user (only applies to faculty/labstaff)
                    cart_entry, created = Cart.objects.get_or_create(
                        name=user_name,
                        item=item.item,
                        defaults={'quantity': 1}
                    )
                    if not created and user_type in ['faculty', 'labstaff']:
                        # If the item already exists in the cart, update the quantity
                        cart_entry.quantity += 1
                        cart_entry.save()
                else:
                    messages.error(request, "You need to be logged in to add items to the tray.")

        except InventoryItem.DoesNotExist:
            messages.error(request, "Item not found.")

        # Redirect back to the page where the request originated
        return redirect(request.META.get('HTTP_REFERER', 'glassware'))

    context = {
        'glassware_items': glassware_items
    }

    return render(request, 'TUPCLaboratoryEquipment/category1_glasswares.html', context)

def labtools_page(request):
    if 'user_id' not in request.session:
        return redirect('main_homepage')  # Redirect to the login page if not logged in
    
    labtools_items = InventoryItem.objects.filter(category='labtools')

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = InventoryItem.objects.get(id=item_id)

            if 'user_id' in request.session and 'user_type' in request.session:
                user_id = request.session['user_id']
                user_type = request.session['user_type']
                user_name = None  

                if user_type == 'student':
                    try:
                        student = StudentAccounts.objects.get(id=user_id)
                        user_name = f"{student.first_name} {student.surname}"

                        # Check if the item is already in the cart for this student
                        if Cart.objects.filter(name=user_name, item=item.item).exists():
                            messages.error(request, "You have already added this item to your tray.")
                            return redirect(request.META.get('HTTP_REFERER', 'labtools'))

                    except StudentAccounts.DoesNotExist:
                        messages.error(request, "Student account not found.")
                        return redirect('main_homepage')

                elif user_type in ['faculty', 'labstaff']:
                    try:
                        faculty = Staff_Faculty_Accounts.objects.get(id=user_id, position=user_type)
                        user_name = f"{faculty.first_name} {faculty.surname} - {faculty.position}"  
                    except Staff_Faculty_Accounts.DoesNotExist:
                        messages.error(request, "Faculty or Lab Staff account not found.")
                        return redirect('main_homepage')

                if user_name:
                    # Check if the item is already in the cart for this user
                    cart_entry, created = Cart.objects.get_or_create(
                        name=user_name,
                        item=item.item,
                        defaults={'quantity': 1}
                    )
                    if not created and user_type in ['faculty', 'labstaff']:
                        # If the item already exists in the cart, update the quantity
                        cart_entry.quantity += 1
                        cart_entry.save()
                else:
                    messages.error(request, "You need to be logged in to add items to the tray.")

        except InventoryItem.DoesNotExist:
            messages.error(request, "Item not found.")

        # Redirect back to the page where the request originated
        return redirect(request.META.get('HTTP_REFERER', 'labtools'))

    context = {
        'labtools_items': labtools_items
    }

    return render(request, 'TUPCLaboratoryEquipment/category2_labtools.html', context)

def heavyequipments_page(request):
    if 'user_id' not in request.session:
        return redirect('main_homepage')  # Redirect to the login page if not logged in
    
    heavyequipments_items = InventoryItem.objects.filter(category='heavyequipments')

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = InventoryItem.objects.get(id=item_id)

            if 'user_id' in request.session and 'user_type' in request.session:
                user_id = request.session['user_id']
                user_type = request.session['user_type']
                user_name = None  

                if user_type == 'student':
                    try:
                        student = StudentAccounts.objects.get(id=user_id)
                        user_name = f"{student.first_name} {student.surname}"

                        # Check if the item is already in the cart for this student
                        if Cart.objects.filter(name=user_name, item=item.item).exists():
                            messages.error(request, "You have already added this item to your tray.")
                            return redirect(request.META.get('HTTP_REFERER', 'heavyequipments'))

                    except StudentAccounts.DoesNotExist:
                        messages.error(request, "Student account not found.")
                        return redirect('main_homepage')

                elif user_type in ['faculty', 'labstaff']:
                    try:
                        faculty = Staff_Faculty_Accounts.objects.get(id=user_id, position=user_type)
                        user_name = f"{faculty.first_name} {faculty.surname} - {faculty.position}"  
                    except Staff_Faculty_Accounts.DoesNotExist:
                        messages.error(request, "Faculty or Lab Staff account not found.")
                        return redirect('main_homepage')

                if user_name:
                    # Check if the item is already in the cart for this user
                    cart_entry, created = Cart.objects.get_or_create(
                        name=user_name,
                        item=item.item,
                        defaults={'quantity': 1}
                    )
                    if not created and user_type in ['faculty', 'labstaff']:
                        # If the item already exists in the cart, update the quantity
                        cart_entry.quantity += 1
                        cart_entry.save()
                else:
                    messages.error(request, "You need to be logged in to add items to the tray.")

        except InventoryItem.DoesNotExist:
            messages.error(request, "Item not found.")

        # Redirect back to the page where the request originated
        return redirect(request.META.get('HTTP_REFERER', 'heavyequipments'))

    context = {
        'heavyequipments_items': heavyequipments_items
    }

    return render(request, 'TUPCLaboratoryEquipment/category3_heavyequipments.html', context)

def manage_account(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech
    
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()
    pending_approvals = StudentAccounts.objects.filter(status='Verified')

    proof_of_enrollment = None  # Variable to hold the proof file URL for viewing

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        staff_id = request.POST.get('staff_id')
        action = request.POST.get('action')

        try:
            if student_id:
                # Handle student account actions
                student = StudentAccounts.objects.get(id=student_id)

                if action == 'approve':
                    student.status = 'Activated'
                    student.save()

                    # Send approval email
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_ADDRESS
                        msg['To'] = student.email
                        msg['Subject'] = "Account Registration Approved"
                        body = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
                                <table align="center" width="600" style="border-collapse: collapse; background: white; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                                <!-- Header with Image -->
                                <tr>
                                    <td align="center" style="padding: 0;">
                                        <img src="https://drive.google.com/uc?id=1va5EOjzxjfSwYDaisC1xhTtDdAEzJWt2" alt="TUPC LAB EQUIPMENT BORROWING SYSTEM" style="width: auto; height: 60px; padding: 3px;">
                                    </td>
                                </tr>   
                                    <!-- Title -->
                                    <tr>
                                        <td align="center" style="padding: 5px; font-size: 18px; font-weight: bold; color: #333;">
                                            ACCOUNT REGISTRATION APPROVED
                                        </td>
                                    </tr>
                                    <!-- Message -->
                                    <tr>
                                        <td align="center" style="padding: 5px; font-size: 16px; color: #555;">
                                            Congratulations! Your account registration has been <strong style="color: #28a745;">APPROVED</strong>.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="padding: 5px; font-size: 16px; color: #555;">
                                            You can now proceed to use the system and access the available laboratory equipment for borrowing.
                                        </td>
                                    </tr>
                                    <!-- Footer -->
                                    <tr>
                                        <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                            © 2024 TUPC Laboratory Equipment Borrowing System.
                                        </td>
                                    </tr>
                                </table>
                            </body>
                        </html>
                        """
                        msg.attach(MIMEText(body, 'html'))


                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                        server.send_message(msg)
                        server.quit()

                        messages.success(request, "Student account approved and notification email sent successfully!")
                    except Exception as e:
                        messages.error(request, f"Student account approved, but an error occurred while sending the email: {e}")

                elif action == 'deactivate':
                    student.status = 'Deactivated'
                    student.save()
                    messages.success(request, "Student account deactivated successfully!")

                elif action == 'activate':
                    student.status = 'Activated'
                    student.save()
                    messages.success(request, "Student account activated successfully!")

                elif action == 'reject':
                    # Send rejection email
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_ADDRESS
                        msg['To'] = student.email
                        msg['Subject'] = "Account Registration Rejected"

                        body = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
                                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                    <!-- Header Section with Image -->
                                    <tr>
                                        <td align="center" style="padding: 0;">
                                            <img src="https://drive.google.com/uc?id=1va5EOjzxjfSwYDaisC1xhTtDdAEzJWt2" alt="TUPC LAB EQUIPMENT BORROWING SYSTEM" style="width: auto; height: 60px; padding: 3px;">
                                        </td>
                                    </tr>
                                    <!-- Body Content -->
                                    <tr>
                                        <td style="padding: 30px; text-align: left; color: #333333;">
                                            <p style="font-size: 18px; margin: 2px 0; font-weight: 800; text-align: center; color: #800000; line-height: 1.2;">
                                                ACCOUNT REGISTRATION REJECTED
                                            </p>
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                We regret to inform you that your account registration has been <strong style="color: #ff0000;">REJECTED</strong> due to an issue with the provided information.
                                            </p>
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                Please review the information you provided and resubmit your application if needed.
                                            </p>
                                            <div style="text-align: center; margin: 20px 0;">
                                                <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                    If you have any questions, feel free to visit the laboratory.
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                    <!-- Footer Section -->
                                    <tr>
                                        <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                            © 2024 TUPC Laboratory Equipment Borrowing System. <br>
                                        </td>
                                    </tr>
                                </table>
                            </body>
                        </html>
                        """
                        
                        msg.attach(MIMEText(body, 'html'))

                        # Setting up the SMTP server
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()  # Secure the connection
                        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login to your email account
                        server.send_message(msg)  # Send the email
                        server.quit()  # Close the connection

                        # After email is sent, delete the request from the database
                        student.delete()

                        messages.success(request, "Student account rejected and request deleted successfully! Rejection email sent.")
                    except Exception as e:
                        messages.error(request, f"Rejection email sent, but an error occurred while deleting the request: {e}")

                elif action == 'view':
                    # Check if the student has a proof of enrollment
                    if student.proof_of_enrollment:
                        # Construct the file URL based on MEDIA_URL and the relative file path in proof_of_enrollment
                        file_url = settings.MEDIA_URL + student.proof_of_enrollment.name
                        return redirect(file_url)  # Redirect to the actual file URL
                    else:
                        messages.error(request, "No enrollment proof found for this user.")
                        return redirect('manage_account')  # Redirect back to the manage account page if no file

            elif staff_id:
                # Handle staff/faculty account actions
                staff = Staff_Faculty_Accounts.objects.get(id=staff_id)

                if action == 'deactivate':
                    staff.status = 'Deactivated'
                    staff.save()
                    messages.success(request, "Staff/Faculty account deactivated successfully!")

                elif action == 'activate':
                    staff.status = 'Activated'
                    staff.save()
                    messages.success(request, "Staff/Faculty account activated successfully!")

        except StudentAccounts.DoesNotExist:
            messages.error(request, "Student account not found.")
        except Staff_Faculty_Accounts.DoesNotExist:
            messages.error(request, "Staff/Faculty account not found.")

    # Fetch all accounts with statuses Activated and Deactivated
    active_students = StudentAccounts.objects.filter(status__in=['Activated', 'Deactivated'])
    faculty_staff = Staff_Faculty_Accounts.objects.filter(status__in=['Activated', 'Deactivated'])

    return render(request, 'TUPCLaboratoryEquipment/manage_accounts.html', {
        'pending_approvals': pending_approvals,
        'active_students': active_students,
        'faculty_staff': faculty_staff,
        'borrow_requests': borrow_requests,
        'pending_count': pending_count,
    })

def send_email(recipient_email, subject, message):
    """Send email to the recipient."""
    try:
        # Setup the MIME
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Establish a secure session with the email server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")

def labstaff_homepage(request):
    if 'user_id' in request.session and request.session.get('user_type') == 'labstaff':
        user_id = request.session['user_id']

        try:
            # Fetch the logged-in user's position from Staff_Faculty_Accounts
            user = Staff_Faculty_Accounts.objects.get(id=user_id)
            position = user.position  # Assuming the position field exists in Staff_Faculty_Accounts

            # Fetch records with statuses Accepted, Handed In, Overdue, or Returned
            valid_statuses = ['Accepted', 'Handed In', 'Overdue', 'Returned', 'Void']
            all_records = Borrowing_Records.objects.filter(status__in=valid_statuses)

            # Check if the record is overdue based on the date_returned field
            current_date = timezone.now().date()
            for record in all_records:
                # First, check if the status is 'Accepted' and if the date_returned has passed
                # Inside the loop where you're checking if the status needs to be changed to 'Void'
                if record.status == 'Accepted' and record.date_returned and record.date_returned < current_date:
                    # Change the status to 'Void' if the item has not been handed in
                    record.status = 'Void'
                    
                    # Update the quantity in the inventory (similar to how it's done when returning)
                    item_name = record.items_borrowed  # Treat it as a single string
                    try:
                        # Find the corresponding item in the InventoryItem table
                        inventory_item = InventoryItem.objects.get(item=item_name)

                        # Get the borrowed quantity from Borrowing_Records and add it back to the inventory
                        borrowed_quantity = record.quantity  # Use the quantity field from Borrowing_Records
                        inventory_item.quantity += borrowed_quantity  # Add the borrowed quantity back to the inventory

                        # Save the updated inventory item
                        inventory_item.save()
                    except InventoryItem.DoesNotExist:
                        print(f"Item {item_name} not found in inventory.")
                    
                    record.save()  # Save the record after updating the status

                
                # Then, check if the status is not already "Void" and the date_returned is passed
                elif record.date_returned and record.date_returned < current_date:
                    # If the status isn't "Accepted", "Returned", or "Overdue", mark it as "Overdue"
                    if record.status not in ['Accepted', 'Returned', 'Overdue', 'Void']:
                        record.status = 'Overdue'
                        record.save()  # Save the record

                        # Send an email when the status is updated to "Overdue"
                        recipient_name = None
                        try:
                            # Try fetching from Staff_Faculty_Accounts
                            recipient = Staff_Faculty_Accounts.objects.get(email=record.email)
                            recipient_name = recipient.first_name

                            # Update account status to "Blacklisted"
                            recipient.status = 'Blacklisted'
                            recipient.save()
                        except Staff_Faculty_Accounts.DoesNotExist:
                            try:
                                # If not found, fetch from StudentAccounts
                                recipient = StudentAccounts.objects.get(email=record.email)
                                recipient_name = recipient.first_name

                                # Update account status to "Blacklisted"
                                recipient.status = 'Blacklisted'
                                recipient.save()
                            except StudentAccounts.DoesNotExist:
                                # Handle case where the email is not found in both tables
                                recipient_name = "User"

                        subject = "Item Overdue"
                        body = f"""
                        <html>
                            <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0;">
                                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                    <!-- Header Section with Radial Gradient Background -->
                                    <tr>
                                        <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                            <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                                alt="Header Image" 
                                                style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                                        </td>
                                    </tr>
                                    <!-- Body Content -->
                                    <tr>
                                        <td style="padding: 30px; text-align: left; color: #333333;">
                                            <p style="font-size: 22px; margin: 2px 0; font-weight: 800; text-align: center; color: #800000; line-height: 1.2;">Item(s) Overdue</p>
                                            <div style="text-align: center; margin: 20px 0;">
                                                <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                    We are writing to inform you that the item(s) you borrowed from the TUPC Laboratory have exceeded the due date for return. As a result, your account has been temporarily blacklisted until the overdue items are returned.
                                                </p>
                                                <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                    <strong>Action Required:</strong><br>
                                                    1. Return the overdue item(s) immediately.<br>
                                                    If you have already returned the items, please disregard this message.
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                    <!-- Footer Section with Copyright Logo -->
                                    <tr>
                                        <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                            © 2024 TUPC Laboratory Equipment Borrowing System.
                                        </td>
                                    </tr>
                                </table>
                            </body>
                        </html>
                        """

                        # Create the email message
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_ADDRESS
                        msg['To'] = record.email
                        msg['Subject'] = subject

                        # Attach the HTML body
                        msg.attach(MIMEText(body, 'html'))

                        # Send the email using SMTP
                        try:
                            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                                server.starttls()  # Secure the connection
                                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                                server.sendmail(EMAIL_ADDRESS, record.email, msg.as_string())
                        except Exception as e:
                            messages.error(request, f"Error sending email: {e}")

            # Handle POST requests to update status (Hand In or Return)
            if request.method == 'POST':
                record_id = request.POST.get('record_id')
                action = request.POST.get('action')

                record = Borrowing_Records.objects.get(id=record_id)

                # Handle status change for returning items
                if action == 'hand_in' and record.status == 'Accepted':
                    record.status = 'Handed In'

                    # Find the owner of the email in Staff_Faculty_Accounts or StudentAccounts
                    recipient_name = None
                    try:
                        # Try fetching from Staff_Faculty_Accounts
                        recipient = Staff_Faculty_Accounts.objects.get(email=record.email)
                        recipient_name = recipient.first_name
                    except Staff_Faculty_Accounts.DoesNotExist:
                        try:
                            # If not found, fetch from StudentAccounts
                            recipient = StudentAccounts.objects.get(email=record.email)
                            recipient_name = recipient.first_name
                        except StudentAccounts.DoesNotExist:
                            # Handle case where the email is not found in both tables
                            recipient_name = "User"

                    # Send email notification for Hand In
                    student_email = record.email  # Fetch the student's email from the Borrowing_Records
                    subject = "Item Handed In"
                    body = f"""
                    <html>
                        <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0;">
                            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                <!-- Header Section with Radial Gradient Background -->
                                <tr>
                                    <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                        <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                            alt="Header Image" 
                                            style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                                    </td>
                                </tr>
                                <!-- Body Content -->
                                <tr>
                                    <td style="padding: 30px; text-align: left; color: #333333;">
                                        <p style="font-size: 22px; margin: 2px 0; font-weight: 800; text-align: center; color: #800000; line-height: 1.2;">The item you requested has been handed in successfully.</p>
                                        <div style="text-align: center; margin: 20px 0;">
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">Please ensure the equipment is handled responsibly and returned on time.</p>
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">Here are some important guidelines for handling the item:</p>
                                            <ul style="font-size: 15px; color: #333333; text-align: left; margin: 10px 0; padding-left: 20px;">
                                                <li>Ensure the equipment is stored properly when not in use.</li>
                                                <li>Inspect the equipment for any damage before use. Report any issues immediately.</li>
                                                <li>Follow all safety protocols while using the equipment.</li>
                                                <li>Return the equipment in the same condition it was handed to you, with all components intact.</li>
                                                <li>Make sure to return the equipment by the specified due date to avoid penalties.</li>
                                            </ul>
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">By following these guidelines, you help ensure that the equipment remains in good condition for future use by others.</p>
                                        </div>
                                    </td>
                                </tr>
                                <!-- Footer Section with Copyright and Small Logo -->
                                <tr>
                                    <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                        © 2024 TUPC Laboratory Equipment Borrowing System.
                                    </td>
                                </tr>
                            </table>
                        </body>
                    </html>
                    """
                    # Set up the email
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_ADDRESS
                    msg['To'] = student_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'html'))  # Specify 'html' instead of 'plain' for HTML content


                    # Send the email via SMTP
                    try:
                        with smtplib.SMTP('smtp.gmail.com', 587) as server:
                            server.starttls()  # Secure the connection
                            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                            server.sendmail(EMAIL_ADDRESS, student_email, msg.as_string())
                    except Exception as e:
                        messages.error(request, f"Error sending email: {e}")

                elif action == 'return' and record.status in ['Handed In', 'Overdue']:  # Now allows return from both Handed In and Overdue
                    record.status = 'Returned'

                    # Find the owner of the email in Staff_Faculty_Accounts or StudentAccounts
                    recipient_name = None
                    try:
                        # Try fetching from Staff_Faculty_Accounts
                        recipient = Staff_Faculty_Accounts.objects.get(email=record.email)
                        recipient_name = recipient.first_name

                        # Update account status to "Activated" if the item is returned
                        recipient.status = 'Activated'
                        recipient.save()
                    except Staff_Faculty_Accounts.DoesNotExist:
                        try:
                            # If not found, fetch from StudentAccounts
                            recipient = StudentAccounts.objects.get(email=record.email)
                            recipient_name = recipient.first_name

                            # Update account status to "Activated" if the item is returned
                            recipient.status = 'Activated'
                            recipient.save()
                        except StudentAccounts.DoesNotExist:
                            # Handle case where the email is not found in both tables
                            recipient_name = "User"

                    # Send email notification for Return
                    # Send email notification for Return
                    subject = "Item Successfully Returned"
                    body = f"""
                    <html>
                        <body style="font-family: 'Arial', sans-serif; padding: 0; margin: 0;">
                            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                <!-- Header Section with Radial Gradient Background -->
                                <tr>
                                    <td align="center" style="padding: 0; background: radial-gradient(circle at top, rgb(107, 1, 1), rgba(46, 1, 1, 0.9)); border-radius: 8px 8px 0 0;">
                                        <img src="https://drive.google.com/uc?id=1yuZBz8h6EEbRowzqMiAAz4Ix3u6hL9zc" 
                                            alt="Header Image" 
                                            style="width: auto; height: 80px; max-width: 100%; padding: 5px; display: block;">
                                    </td>
                                </tr>
                                <!-- Body Content -->
                                <tr>
                                    <td style="padding: 30px; text-align: left; color: #333333;">
                                        <p style="font-size: 22px; margin: 2px 0; font-weight: 800; text-align: center; color: #800000; line-height: 1.2;">The item you borrowed has been returned successfully.</p>
                                        <div style="text-align: center; margin: 20px 0;">
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                Thank you for returning the borrowed equipment on time and adhering to the borrowing guidelines. Your cooperation is highly appreciated and ensures the efficient operation of our system.
                                            </p>
                                            <p style="font-size: 15px; margin: 10px 0; color: #333333;">
                                                We look forward to assisting you again in the future with any laboratory equipment needs.
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                                <!-- Footer Section with Copyright and Small Logo -->
                                <tr>
                                    <td align="center" style="padding: 10px; font-size: 12px; color: #333; background-color: #f4f4f4; border-top: 1px solid #ddd;">
                                        © 2024 TUPC Laboratory Equipment Borrowing System.
                                    </td>
                                </tr>
                            </table>
                        </body>
                    </html>
                    """
                    # Create the email message
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_ADDRESS
                    msg['To'] = record.email
                    msg['Subject'] = subject

                    # Attach the HTML body
                    msg.attach(MIMEText(body, 'html'))

                    # Send the email using SMTP
                    try:
                        with smtplib.SMTP('smtp.gmail.com', 587) as server:
                            server.starttls()  # Secure the connection
                            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                            server.sendmail(EMAIL_ADDRESS, record.email, msg.as_string())
                    except Exception as e:
                        messages.error(request, f"Error sending email: {e}")


                    # Update the inventory when the item is returned
                    item_name = record.items_borrowed  # Just treat it as a single string, not a list
                    try:
                        # Find the corresponding item in the InventoryItem table
                        inventory_item = InventoryItem.objects.get(item=item_name)

                        # Get the borrowed quantity from Borrowing_Records and add it to the inventory
                        borrowed_quantity = record.quantity  # Use the quantity field from Borrowing_Records
                        inventory_item.quantity += borrowed_quantity  # Add the borrowed quantity to the inventory

                        # Save the updated inventory item
                        inventory_item.save()
                    except InventoryItem.DoesNotExist:
                        print(f"Item {item_name} not found in inventory.")

                record.save()
                return redirect('labstaff_homepage')

            context = {
                'records': all_records,
                'position': position, 
                'current_date': current_date,
            }

            return render(request, 'TUPCLaboratoryEquipment/labstaff_homepage.html', context)

        except Staff_Faculty_Accounts.DoesNotExist:
            return redirect('main_homepage')

    return redirect('main_homepage')


def blacklisted(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labstaff':
        return redirect('main_homepage')  

    user_id = request.session['user_id']

    try:
        overdue_records = Borrowing_Records.objects.filter(status='Overdue')  
        return render(request, 'TUPCLaboratoryEquipment/blacklisted.html', {
            'overdue_records': overdue_records
        })
    except Exception as e:
        messages.error(request, f"An error occurred while fetching overdue records: {e}")
        return redirect('labstaff_homepage')  

def manage_programs(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'labtech':
        return redirect('main_homepage')  # Redirect to the login page if not logged in as labtech
    
    programs = Program.objects.all()  
    borrow_requests = Borrowing_Records.objects.filter(status="Pending")
    pending_count = borrow_requests.count()

    if request.method == 'POST':
        program_name = request.POST.get('program-name')
        program_id = request.POST.get('program-id')  
        delete_id = request.POST.get('delete-id')  

        if Program.objects.filter(program_name=program_name).exists():
            messages.error(request, "Program name already exists.")
            return render(request, 'TUPCLaboratoryEquipment/manage_programs.html', {
                'programs': programs,
                'borrow_requests': borrow_requests
            })
        
        if delete_id:  
            program = get_object_or_404(Program, id=delete_id)
            program.delete()
            return JsonResponse({'success': True})

        elif program_name:
            if program_id:  
                program = get_object_or_404(Program, id=program_id)
                program.program_name = program_name
                program.save()
                return JsonResponse({'success': True, 'program_name': program_name})
            else:  
                new_program = Program.objects.create(program_name=program_name)
            
    return render(request, 'TUPCLaboratoryEquipment/manage_programs.html', {
        'programs': programs,
        'borrow_requests': borrow_requests,
        'pending_count': pending_count, 
    })


def logout_view(request):
    if 'user_id' in request.session:
        print(f"Logging out user ID: {request.session['user_id']}")  
        del request.session['user_id']
    if 'first_name' in request.session:
        del request.session['first_name']

    # Clear all session data
    request.session.flush()  # This will clear all session data

    print("Session after logout:", request.session.keys())
    
    # Redirect to main homepage after logout
    return redirect('main_homepage')