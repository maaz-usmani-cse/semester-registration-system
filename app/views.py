import random
from django.contrib import messages  
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q  
from .models import UserProfile


def is_password_strong(password):
    digit = any(i.isdigit() for i in password)
    symbol = any(not i.isalnum() for i in password)
    alphabet = any(i.isalpha() for i in password)
    
    if not (digit and symbol and alphabet):
        return False, "Password mein kam se kam ek digit, ek symbol, aur ek alphabet hona chahiye!"
    return True, ""


def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name', '').strip().title()
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip().lower()
        mobile = request.POST.get('mobile', '').strip()  # HTML name="mobile"
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        profile_pic = request.FILES.get('profile_pic')
        terms_accepted = request.POST.get('terms')

        if not all([full_name, username, email, mobile, password, confirm_password]):
            return render(request, 'signup.html', {'error': 'Bhai, saare fields bharna zaroori hai!'})
        

        if not terms_accepted:
            return render(request, 'signup.html', {'error': 'Bhai, aage badhne ke liye Terms & Service agree karna zaroori hai!'})
        

        if len(mobile) < 10 or not mobile.replace('+', '').replace(' ', '').isdigit():
            return render(request, 'signup.html', {'error': 'Bhai, valid mobile number enter karo!'})

        # Junk cleanup for unverified data on re-attempts
        UserProfile.objects.filter(email=email, is_verified=False).delete()
        UserProfile.objects.filter(username=username, is_verified=False).delete()
        UserProfile.objects.filter(mobile=mobile, is_verified=False).delete()
        

        if UserProfile.objects.filter(username=username, is_verified=True).exists():
            return render(request, 'signup.html', {'error': 'Bhai, ye username pehle se kisi ne le rakha hai!'})

        if UserProfile.objects.filter(email=email, is_verified=True).exists():
            return render(request, 'signup.html', {'error': 'Ye email pehle se register hai!'})

        if UserProfile.objects.filter(mobile=mobile, is_verified=True).exists():
            return render(request, 'signup.html', {'error': 'Bhai, ye mobile number pehle se use ho raha hai!'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Dono password match nahi kar rahe!'})
             
        is_strong, msg = is_password_strong(password)
        if not is_strong:   
            return render(request, 'signup.html', {'error': msg})

        otp_code = str(random.randint(100000, 999999))
        
        try:
            with transaction.atomic():
                hashed_pw = make_password(password)
                UserProfile.objects.create(
                    full_name=full_name,
                    username=username,
                    email=email,
                    mobile=mobile,
                    profile_pic=profile_pic,
                    password=hashed_pw,
                    otp=otp_code,
                    otp_created_at=timezone.now(),
                    is_verified=False
                )
                
                send_mail(
                    "Verify Your Account",
                    f"Bhai, aapka OTP hai: {otp_code}. Ye sirf 5 minute tak valid hai.",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=True
                )
                
                request.session['pre_verified_username'] = username
                return redirect('verify_otp')
                
        except Exception:
            return render(request, 'signup.html', {'error': 'Technical error! Email ya data save nahi ho paya.'})

    return render(request, 'signup.html')






def verify_otp_view(request):
    username = request.session.get('pre_verified_username')
    
   
    if not username:
        return redirect('signup')

    if request.method == "POST":
        submitted_otp = request.POST.get('otp_code', '').strip()

       
        if not submitted_otp:
            return render(request, 'verify.html', {'error': 'Bhai, OTP daalna zaroori hai!'})

        profiles = UserProfile.objects.filter(username=username, is_verified=False)
        
       
        if not profiles.exists():
            return redirect('signup')

        profile = profiles.first()

       
        if not profile.is_otp_valid():
            return render(request, 'verify.html', {
                'error': 'Bhai, OTP ka 5-minute ka time khatam ho gaya! "Resend OTP" par click karo.'
            })

       
        if profile.otp != submitted_otp:
            return render(request, 'verify.html', {'error': 'Galat OTP code daala hai bhai, sahi se check karo!'})

        # SUCCESS BLOCK: Agar saare checks pass ho gaye
        profile.is_verified = True
        profile.otp = None  
        profile.save()

       
        del request.session['pre_verified_username']
        
        return redirect('login')

    return render(request, 'verify.html')





def resend_otp_view(request):
    username = request.session.get('pre_verified_username')
    
    
    if not username:
        return redirect('signup')

    if request.method != "POST":
        return redirect('verify_otp')

    profiles = UserProfile.objects.filter(username=username, is_verified=False)
    
    if not profiles.exists():
        return redirect('signup')

    profile = profiles.first()
    
    new_otp = str(random.randint(100000, 999999))
    profile.otp = new_otp
    profile.otp_created_at = timezone.now()
    profile.save()
    
    try:
        send_mail(
            "Resend: Verify Your Account",
            f"Bhai, aapka naya OTP hai: {new_otp}. Ye bhi sirf 5 minute tak valid hai.",
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=True
        )
        # Dynamic success notification for standard alert rendering
        messages.success(request, 'Naya OTP aapke email par bhej diya gaya hai!')
        return redirect('verify_otp')
        
    except Exception:
        messages.error(request, 'Mail server error! Naya OTP nahi bhej paye.')
        return redirect('verify_otp')




def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('login_input', '').strip().lower() 
        password_input = request.POST.get('password', '').strip()
        remember_me=request.POST.get('remember_me')

       
        if not all([login_input, password_input]):
            return render(request, 'login.html', {'error': 'Bhai, fields khali mat chodo!'})

       
        profiles = UserProfile.objects.filter(Q(username=login_input) | Q(email=login_input))
        
       
        if not profiles.exists():
            return render(request, 'login.html', {'error': 'Bhai, ye credentials registered nahi hain!'})
        
       
        profile = profiles.first()
        
      
        if not check_password(password_input, profile.password):
            return render(request, 'login.html', {'error': 'Password galat hai bhai!'})
            
        
        if not profile.is_verified:
            request.session['pre_verified_username'] = profile.username
            # Redirect logic update standard ko manage karega (Verification state path rendering)
            return redirect('resend_otp', {'error': 'Bhai, account verified nahi hai! Pehle OTP verify karo.'})

        
       
        request.session['user_id'] = profile.id

        if remember_me:
           
            request.session.set_expiry(None)
        else:
            # Checkbox Unchecked -> Browser Band (`X`) Hote Hi Instantly Logout!
            request.session.set_expiry(0)
        return redirect('dashboard')

    return render(request, 'login.html')





def dashboard_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
        
    profiles = UserProfile.objects.filter(id=user_id)
    if profiles.exists():
        return render(request, 'dashboard.html', {'user': profiles.first()})
    
    return redirect('login')






def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')






def forgot_password_view(request):
    if request.method == "POST":
        email_input = request.POST.get('email', '').strip().lower()
        if not email_input:
            return render(request, 'forgot_password.html', {'error': 'Email bharna zaroori hai!'})
            
        profiles = UserProfile.objects.filter(email=email_input, is_verified=True)
        if not profiles.exists():
            return render(request, 'forgot_password.html', {'error': 'Email verified nahi hai!'})
            
        profile = profiles.first()
        reset_otp = str(random.randint(100000, 999999))
        profile.otp = reset_otp
        profile.otp_created_at = timezone.now()
        profile.save()
        
        try:
            send_mail(
                "Reset Your Password",
                f"Aapka OTP hai: {reset_otp}",
                settings.EMAIL_HOST_USER,
                [email_input],
                fail_silently=True
            )
            request.session['reset_email'] = email_input
            return redirect('reset')
        except Exception:
            return render(request, 'forgot_password.html', {'error': 'Mail send error.'})

    
    return render(request, 'forgot_password.html')







def reset_password_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot')

    if request.method == "POST":
        submitted_otp = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not all([submitted_otp, new_password, confirm_password]):
            return render(request, 'reset_password.html', {'error': 'Saare fields fill karo!'})

        if new_password != confirm_password:
            return render(request, 'reset_password.html', {'error': 'Passwords match nahi ho rahe!'})

        is_strong, msg = is_password_strong(new_password)
        if not is_strong:
            return render(request, 'reset_password.html', {'error': msg})

        profiles = UserProfile.objects.filter(email=email)
        if not profiles.exists():
            return redirect('forgot')

        profile = profiles.first()
        if not profile.is_otp_valid():
            return render(request, 'reset_password.html', {'error': 'OTP expire ho gaya hai!'})

        if profile.otp != submitted_otp:
            return render(request, 'reset_password.html', {'error': 'Galat OTP code hai.'})

        # Success Action
        profile.password = make_password(new_password)
        profile.otp = None
        profile.save()

        if 'reset_email' in request.session:
            del request.session['reset_email']

        messages.success(request, 'Password reset ho gaya! Ab login karein.')
        return redirect('login')

    # GET Request par direct template render
    return render(request, 'reset_password.html')







def resend_forgot_password_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot')

    # Action Guard: Direct GET walo ko wapas redirect karo
    if request.method != "POST":
        return redirect('reset')

    profiles = UserProfile.objects.filter(email=email, is_verified=True)
    if not profiles.exists():
        return redirect('forgot')

    profile = profiles.first()
    new_otp = str(random.randint(100000, 999999))
    profile.otp = new_otp
    profile.otp_created_at = timezone.now()
    profile.save()

    try:
        send_mail(
            "Resend: Reset Your Password",
            f"Aapka naya OTP hai: {new_otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True
        )
        messages.success(request, 'Naya OTP email par bhej diya gaya hai!')
    except Exception:
        messages.error(request, 'Mail server issue! OTP nahi gaya.')

    return redirect('reset')








def legal_policy_view(req):
    return render(req,'legal.html')




