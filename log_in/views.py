from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random, pickle
# # Create your views here.

def send_mail_to_client(mail, username = ""):
    subject = "OTP Verification for creating account"
    otp = random.randint(1000, 9999)
    message = f"Dear{' ' + username}, \n\t\tOTP for creating an account in this website is {otp}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    send_mail(subject, message, from_email, recipient_list)
    return otp

def encrypt(psswd):
    l = 'asdfghjklqwertyuiopzxcvbnm!@#$%^&*()<>?:"{}\\\' ASDFGHJKLQWERTYUIOPZXCVBNM1234567890'
    l = list(l)
    s = ""
    for i in range(len(psswd)):
        for j in range(4):
            s+=random.choice(l)
        s+=psswd[i]
    for j in range(4):
        s+=random.choice(l)
    return s

def decrypt(psswd):
    s = ""
    for i in range(1, (len(psswd)//5)+1):
        s+=psswd[(i*5)-1]
    return s

def verify(username, password):
    f = open("auth.dat", "rb")
    s = pickle.load(f)
    while True:
        u, e, p = s.split('--split--')
        if (username == u):
            if (decrypt(p).strip() == password):
                return True
            else:
                return False
        try:
            s = pickle.load(f)
        except EOFError:
            break
    f.close()
    return False

def base(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def logIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        psswd = request.POST.get('password')
        if verify(username, psswd):
            return HttpResponse("Logged In Success Fully")
        else:
            messages.add_message(request, messages.WARNING, "Invalid Credentials")
            return HttpResponseRedirect('/')


def signUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        mail = request.POST.get('email')
        f = open("auth.dat", "rb")
        r = pickle.load(f)
        if mail in r:
            messages.add_message(request, messages.WARNING, "An account exist under this Account")
            return HttpResponseRedirect('/signup')
        f.close()
        psswd = request.POST.get('password')
        otp = send_mail_to_client(mail, username)
        f = open("otp.dat", "ab")
        pickle.dump(f"{username}--split--{mail}--split--{encrypt(psswd)}--split--{otp}\n", f)
        f.close()
        return HttpResponseRedirect(f'verify/{mail}')
    template = loader.get_template("logon.html")
    return HttpResponse(template.render({}, request))

def otpVerification(request, mail):
    if request.method == "POST":
        s = ""
        f = open("otp.dat", "rb")
        opts = pickle.load(f)
        verified = 0
        for i in [i for i in opts.split("\n") if i.strip() != '']:
            username, email, psswd, otp = i.split('--split--')
            if mail == email and otp == request.POST.get('otp'):
                auth = open("auth.dat", "ab")
                pickle.dump(f"{username}--split--{email}--split--{psswd}\n", auth)
                auth.close()
                verified = 1
            else:
                s+=i
                s+='\n'
        f.close()
        f = open("otp.dat", "wb")
        if s!="":
            f.dump(s)
        f.close()
        if verified == 1:
            messages.add_message(request, messages.SUCCESS, "Account created successfully")
            return HttpResponseRedirect('/')
        else:
            messages.add_message(request, messages.WARNING, "Invalid Otp")
            return HttpResponseRedirect(f'verify/{mail}')
    template = loader.get_template("otp.html")
    context = {
        "email": mail,
    }
    return HttpResponse(template.render(context, request))