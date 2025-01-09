from django.urls import path
from TUPCLaboratoryEquipment.templates.TUPCLaboratoryEquipment import views  # Correct import from the proper module
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),  
    path('register/', views.register_student, name='register_student'),
    path('student_homepage/', views.student_homepage, name='student_homepage'),  
    path('faculty_homepage/', views.faculty_homepage, name='faculty_homepage'),  
    path('cart_student/', views.cart_student, name='cart_student'),  
    path('cart_faculty/', views.cart_faculty, name='cart_faculty'),  
    path('change-password/', views.change_password, name='change_password'), 
    path('main-homepage/', views.main_homepage, name='main_homepage'),  
    path('add-equipment/', views.add_equipment, name='add_equipment'),  
    path('remove-equipment/', views.remove_equipment, name='remove_equipment'),  
    path('borrowing-records/', views.borrowing_records, name='borrowing_records'),  
    path('account-register/', views.account_register, name='account_register'), 
    path('labtech_homepage/', views.labtech_homepage, name='labtech_homepage'),  
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password_otp/', views.forgot_passwordotp, name='forgot_passwordotp'),
    path('forgot-password_reset/', views.forgot_password_reset, name='forgot_password_reset'),

    path('glassware/', views.glassware_page, name='glassware'), 
    path('labtools/', views.labtools_page, name='labtools'), 
    path('heavyequipments/', views.heavyequipments_page, name='heavyequipments'),  

    path('manage-programs/', views.manage_programs, name='manage_programs'),
    path('manage-account/', views.manage_account, name='manage_account'),
    path('labstaff_homepage/', views.labstaff_homepage, name='labstaff_homepage'),
    path('blacklisted/', views.blacklisted, name='blacklisted'), 
    path('logout/', views.logout_view, name='logout'),
    path('force_change_password/', views.force_change_password, name='force_change_password'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('generate-report/', views.generate_report, name='generate_report'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)