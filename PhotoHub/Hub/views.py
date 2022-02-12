from asyncio.windows_events import NULL
from xmlrpc.client import boolean
from django.http import HttpResponse
from django.shortcuts import render, redirect

#Importing User model for creating a User instance or authenticating and login , logout
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout

#Importing Customer and Photographer module
from Hub.models import Customer, Photographer, Appointment, Blog

#For message displaying
from django.contrib import messages

import math, pytz, sys
from django.utils import timezone
from datetime import date, datetime, timedelta


# Create your views here.
def index(request):    
    now = timezone.make_aware(datetime.now(),timezone.get_default_timezone())
    now =  now.astimezone(timezone.utc)
    appointments = Appointment.objects.all()

    for appointment in appointments:
        if appointment.zip == sys.maxsize:
            appointment.delete()

    feedback = []
    for ap in appointments:
        if ap.feedback==False and ap.end_date <= now:
            ap.feedback = True
            ap.save()
            feedback.append(ap)
    print(len(feedback))

    context = {}
    context['feedback'] = feedback
    #Display posts on basis of recent publishing date
    blogs = Blog.objects.order_by('-date')[:3]
    pphs = Photographer.objects.all().order_by('-rate')[:3]
    pphs = [(pphs[0], [pphs[1], pphs[2]])]

    customerTemp = Customer.objects.all()[:4]
    customers = [customerTemp[:2], customerTemp[2:4]]

    context = {'blogs': blogs, 'customers':customers, 'pphs': pphs, 'feedback':feedback}

    if request.user.is_authenticated:
        if request.user.groups.all()[0].name == 'Photographer':
            ph = Photographer.objects.get(photographer_id=request.user.id)

            context= {'id':ph.photographer_id, 'role':'Photographer','image': ph.image, 'blogs': blogs, 'customers':customers, 'pphs': pphs, 'feedback':feedback}
            return render(request, 'landing.html', context)

        else :
            #Clean appointment model
            appointments = Appointment.objects.all()
            for appointment in appointments:
                if appointment.zip == sys.maxsize:
                    appointment.delete()

            cst = Customer.objects.get(customer_id=request.user.id)
            context= {'role':'Customer','image':cst.image, 'blogs': blogs, 'customers':customers, 'pphs': pphs, 'feedback':feedback}
            return render(request, 'landing.html', context)

    return render(request, 'landing.html', context)
    

def role(request):
    user = User.objects.get(id=request.user.id)
    if len(user.groups.all()) == 0:
       return render(request, 'role.html')
    else:
        return redirect('/')
         
  
def googleLogin(request):
    if request.method == 'POST':
       role = request.POST.get('role')

       #Update Google logged in user with it's role
       new_group, created = Group.objects.get_or_create(name = role)
       user = User.objects.get(id=request.user.id)
       user.groups.add(new_group)

       #Add to customer/photographer module depending upon role
       if new_group.name == 'Customer':
            customer = Customer(customer_id=user.id, email=user.email)
            customer.save()
       else :
            photographer = Photographer(photographer_id=user.id, email=user.email)
            photographer.save()
      
       context = {'role':new_group.name, 'id':user.id} 
       messages.info(request, 'Your initial registration is successfull !')
       return render(request, 'signup2.html', context)



def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
           # A backend authenticated the credentials
           login(request, user)
           messages.info(request, 'Successfully logged in as ' + str(request.user) + ' !')
        #  print(request.user.email)
        #  print(user.groups.all()[0])
           return redirect('/')
        else:
           # No backend authenticated the credentials
           messages.warning(request, 'Invalid credentials! Please try again.')
           return redirect('/')

    return HttpResponse('<h1>Error 404</h1><br> <h3>Page not found!</h3>')


def logoutUser(request):
    logout(request)
    messages.info(request, 'Your have logged out successfully !')
    return redirect('/')


def profile(request, af):
    alert=""
    ckey=-1
    pkey=-1

    if af[0] == '1' :
       alert='modal'
       af = af.split('_')
       ckey = int(af[1])
       pkey = int(af[2])


    if request.user.groups.all()[0].name == 'Photographer':
        ph = Photographer.objects.get(photographer_id=request.user.id)
        tempappointments = Appointment.objects.filter(photographer=ph).order_by('start_date')
        appointments = []
        for appointment in tempappointments:
            if appointment.zip != sys.maxsize:
                appointments.append(appointment)
            else:
               appointment.delete() 

        length = len(appointments)
        
        # rating
        stars=''
        if ph.rate == 1:
          stars = '★☆☆☆'
        elif ph.rate == 2:
          stars = '★★☆☆☆'
        elif ph.rate == 3:
          stars = '★★★☆☆'
        elif ph.rate == 4:
          stars = '★★★★☆' 
        else:
          stars = '★★★★★'   


        #For comparing datetime field of django models.
        for appointment in appointments:
            appointment.appointment_status = update_appointment_status(appointment)
            appointment.save()

        incoming_appointments = fetch_incoming_appointments(appointments)

        context={
                 'fname': ph.fname, 'lname':ph.lname, 'gender':ph.gender, 'phone':ph.phone, 'city':ph.city, 'pin':ph.pincode,
                 'email':ph.email[:21], 'category':ph.category, 'role':'Photographer', 'image':ph.image, 'status':ph.status,
                 'state':ph.state, 'incoming_appointments': incoming_appointments, 'length': length, 'alert': alert, 
                 'id':ph.photographer_id, 'ckey':ckey, 'pkey': pkey, 'facebook':ph.facebook, 'instagram':ph.instagram, 'tweeter':ph.tweeter,
                 'stars':stars
        }
        
        return render(request, 'profile.html',  context)
    else :
        cst = Customer.objects.get(customer_id=request.user.id)
        tempappointments = Appointment.objects.filter(customer=cst).order_by('start_date')
        appointments = []
        for appointment in tempappointments:
            if appointment.zip != sys.maxsize:
                appointments.append(appointment)
            else:
               appointment.delete()    

        length = len(appointments)

        for appointment in appointments:
            appointment.appointment_status = update_appointment_status(appointment)
            appointment.save()
        
        incoming_appointments = fetch_incoming_appointments(appointments)


        context={
                'fname': cst.fname, 'lname':cst.lname, 'phone':cst.phone, 'city':cst.city, 'state':cst.state, 'pin':cst.pincode,
                'email':cst.email[:21], 'role':'Customer', 'image':cst.image, 'incoming_appointments': incoming_appointments, 'length': length,
                'alert': alert, 'ckey':ckey, 'pkey': pkey
             }
        return render(request, 'profile.html', context)

def forgotpassword(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        present = "True"
        context = {}
        try:
            user = User.objects.get(username=uname)
            context['user'] = user
            context['email'] = user.email
            return render(request, 'forgotpassword2.html', context)
        except User.DoesNotExist:
            present = "False"
            context['present'] = present
            return render(request, 'forgotpassword.html', context)
    return render(request, 'forgotpassword.html')


def forgotpassword2(request):
    if request.method == "POST":
        original_otp = request.POST.get('original_otp')
        entered_otp = request.POST.get('entered_otp')
        user = request.POST.get('user')
        correct = "False"
        if original_otp == entered_otp:
            corrent = "True"
            user = User.objects.get(username=user)
            return render(request, 'changePassword.html', {'user':user})
        else : 
            return render(request, 'forgotpassword2.html', {'correct':correct})

def changePassword(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        usr = request.POST.get('user')
        user = User.objects.get(username = usr)
        print(user.password)
        user.set_password(new_password)
        user.save()

        print(user)
        print(user.email)
        print(user.password)

        messages.success(request, 'Your password updated succefully, please login!')
        return render(request, 'landing.html')
    

def fetch_incoming_appointments(appointments):
    incoming_appointments = []
    for appointment in appointments:
        if len(incoming_appointments) < 3 and appointment.appointment_status != 'Closed':
           incoming_appointments.append(appointment) 

        if len(incoming_appointments) == 3 :
            break

    return incoming_appointments

def update_appointment_status(appointment):
    #For comparing datetime field of django models.
    #Get awared time in current time zone
    now = timezone.make_aware(datetime.now(),timezone.get_default_timezone())
    now =  now.astimezone(timezone.utc)
    # print(now)

    apt_status = 'Incoming'
    if now >= appointment.start_date and now <= appointment.end_date:
        apt_status = 'Ongoing' 
    elif now > appointment.end_date:
        apt_status = 'Closed'

    return apt_status   

def register_step1(request):
    if request.method=='POST':
        username = request.POST.get('uname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
       
        user = User.objects.create_user(username, email, password)
        user.save()

        #returns a tuple
        new_group, created = Group.objects.get_or_create(name = role)
        user.groups.add(new_group)

        #Add to customer/photographer module depending upon role
        if new_group.name == 'Customer':
            customer = Customer(customer_id=user.id, email=user.email)
            customer.save()
        else :
            photographer = Photographer(photographer_id=user.id, email=user.email)
            photographer.save()
      
        print(user.id, new_group.name)
        context = {'role':new_group.name, 'id':user.id} 
        messages.success(request, 'Your initial registration is successfull !')
        return render(request, 'signup2.html', context)

    return HttpResponse('<h1>Error 404</h1><br> <h3>Page not found!</h3>')   
        
def register_step2(request):
    if request.method=='POST': 
        id = request.POST.get('id')
        role = request.POST.get('role')
        
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        phone = request.POST.get('phone')
        state = request.POST.get('state')
        city = request.POST.get('city')
        area = request.POST.get('area')
        pin = request.POST.get('pin')
        image= request.FILES['dp']

        if role=='Photographer':
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            category = request.POST.get('category')
            photographer = Photographer.objects.get(photographer_id=id)
            photographer.fname = fname
            photographer.lname = lname
            photographer.phone = phone
            photographer.state = state
            photographer.city = city
            photographer.area = area
            photographer.pincode = pin
            photographer.age = age
            photographer.gender = gender
            photographer.category = category
            photographer.image = image
            photographer.save()

        else :
            customer = Customer.objects.get(customer_id=id)
            customer.fname = fname
            customer.lname = lname
            customer.phone = phone
            customer.state = state
            customer.city = city
            customer.area = area
            customer.pincode = pin
            customer.image = image
            customer.save()

        messages.info(request, "Your registration is completed successfuly !")
        return redirect('/')


def editProfile(request):
   if request.method == 'POST':
      fname = request.POST.get('fname')
      lname = request.POST.get('lname')
      email = request.POST.get('email')
      phone = request.POST.get('phone')
      state = request.POST.get('state')
      city = request.POST.get('city')
      area = request.POST.get('area')
      pin = request.POST.get('pin')
      image= request.FILES['dp'] 

      if request.user.groups.all()[0].name == 'Photographer':
          facebook = request.POST.get('facebook')
          instagram = request.POST.get('instagram')
          tweeter = request.POST.get('tweeter')
          age = request.POST.get('age')
          category = request.POST.get('category')  
          photographer = Photographer.objects.get(photographer_id=request.user.id)
          photographer.fname = fname
          photographer.lname = lname
          photographer.phone = phone
          photographer.state = state
          photographer.city = city
          photographer.area = area
          photographer.pincode = pin
          photographer.age = age
          photographer.email = email
          photographer.category = category
          photographer.image = image
          photographer.facebook = facebook
          photographer.instagram = instagram
          photographer.tweeter = tweeter
          photographer.save()

      else :
            customer = Customer.objects.get(customer_id=request.user.id)
            customer.fname = fname
            customer.lname = lname
            customer.email = email
            customer.phone = phone
            customer.state = state
            customer.city = city
            customer.area = area
            customer.pincode = pin
            customer.image = image
            customer.save()
      
      messages.info(request, 'Your profile was updated successfully')
      return redirect('/profile0')


   if request.user.groups.all()[0].name == 'Photographer':
        ph = Photographer.objects.get(photographer_id=request.user.id)

        context={
                 'fname': ph.fname, 'lname':ph.lname, 'phone':ph.phone, 'city':ph.city, 'pin':ph.pincode,
                 'email':ph.email, 'category':ph.category, 'image':ph.image, 'state':ph.state, 'age':ph.age,
                 'area': ph.area, 'id':ph.photographer_id, 'facebook':ph.facebook, 'instagram':ph.instagram, 'tweeter':ph.tweeter
        }
        
        return render(request, 'editProfile.html',  context)

   else :
        cst = Customer.objects.get(customer_id=request.user.id)
        context={
                'fname': cst.fname, 'lname':cst.lname, 'phone':cst.phone, 'city':cst.city, 'state':cst.state, 'pin':cst.pincode,
                'email':cst.email, 'image':cst.image, 'area': cst.area
             }
        return render(request, 'editProfile.html', context)
   

def location_eligibility(request):
    cst = Customer.objects.get(customer_id=request.user.id) 
    context= {'image': cst.image}  

    if request.method == 'POST':
        city = request.POST.get('city')
        hours = int(request.POST.get('hours'))

        if hours < 24 or hours > 72 :
           messages.warning(request, 'Invalid selection of hours !') 
           return redirect('/location')
        else :
           start_date = datetime.now() + timedelta(hours=hours)
           appointment = Appointment(customer = cst, start_date=start_date, zip=sys.maxsize)
           appointment.save()
           return redirect('/category/' + city)

    return render(request, 'location_eligibility.html', context)

def category(request, city):
    context = {'city':city}

    cst = Customer.objects.get(customer_id=request.user.id)
    context['image'] = cst.image
    
    #creates dictionary for each object
    catphs = Photographer.objects.values('category', 'photographer_id')
    cats = {item['category'] for item in catphs}
    #print(cats)
    
    allcatph = []
    for cat in cats:
        catph = Photographer.objects.filter(category=cat, city=city)
        if len(catph) != 0:
          tuple = (cat, catph)
          allcatph.append(tuple)

   # print(allcatph)    
    context['allcatph'] = allcatph
    return render(request, 'category.html', context)


def allfromCat(request, cat):
    context = {}
    cat = cat.split('_')
    cst = Customer.objects.get(customer_id=request.user.id)
    context['image'] = cst.image

    tempcatphall = Photographer.objects.filter(category=cat[0], city=cat[1])
    catphall = []
    st=0
    for ind in range(3, len(tempcatphall)+1, 3):
        catphall.append(tempcatphall[st:ind])
        st+=3
    if len(tempcatphall[st:]) != 0:
      catphall.append(tempcatphall[st:])


    context['catphall'] = catphall
    context['category'] = cat[0]
    context['city'] = cat[1]
    return render(request, 'allfromCat.html', context)


def appointment(request, pid):
    pid = pid.split('_')
    
    cst = Customer.objects.get(customer_id=request.user.id)
    appointment = Appointment.objects.get(zip=sys.maxsize)
    sdate = appointment.start_date
    context = {'image': cst.image, 'pid': pid[0], 'city': pid[1], 'sdate': sdate}
    return render(request, 'appointment.html', context)
  

def createAppointment(request, city):
    if request.method == 'POST':
        pid = request.POST.get('pid')
        edate = request.POST.get('edate')
        state = request.POST.get('state')
        city = request.POST.get('city')
        area = request.POST.get('area')
        zip = request.POST.get('zip')

        apt = Appointment.objects.get(zip=sys.maxsize)

        #Validating the start and end dates
        sdate = str(apt.start_date).split(' ')
        # print('Rohit___' + sdate[0] + '___' + sdate[1])
        edt = str(edate).split('T')
        # print('Rohit___' + edt[0] + '___' + edt[1])
        flag = validateDate(sdate[0], sdate[1], edt[0], edt[1])
        if not flag:
            messages.warning(request, 'Invalid end date, appointment duration must be atleast 30 minutes !')
            return redirect('/appointment/'+pid + '_' + city)


        ph = Photographer.objects.get(photographer_id=pid)
        cst = Customer.objects.get(customer_id=request.user.id)

        apt.photographer=ph
        apt.end_date=edate
        apt.state=state
        apt.city=city
        apt.area=area
        apt.zip=zip
        apt.appointment_status='incoming'   
        apt.save()
        
        ph.status="Busy"
        ph.save()
        context = {'ph': ph, 'cst': cst, 'appointment' : apt ,'image': cst.image, 'edate':edt[0]}
        return render(request, 'successAppointment.html', context)


def validateDate(sdate, stime, edate, etime):
    #Processing sdate
    date1 = sdate.split('-')
    date1[0] = int(date1[0])
    date1[1] = int(date1[1])
    date1[2] = int(date1[2])

    stime = stime.split(':')
    stime[0] = int(stime[0])
    stime[1] = int(stime[1])

    #Processing edate
    date2 = edate.split('-')
    date2[0] = int(date2[0])
    date2[1] = int(date2[1])
    date2[2] = int(date2[2])

    etime = etime.split(':')
    etime[0] = int(etime[0])
    etime[1] = int(etime[1])

    sdate = datetime(date1[0], date1[1], date1[2], stime[0], stime[1])
    edate = datetime(date2[0], date2[1], date2[2], etime[0], etime[1])  
    duration = edate - sdate
    duration_in_s = duration.total_seconds()
    minutes = divmod(duration_in_s, 60)[0]

    # print('Rohit___' + str(minutes))

    if minutes >= 30:
        return True
    return False 


def pagination(request, bnum):
    pnum, first, last = bnum.split('_')
    
    #Range of buttons to show for controlling pagination
    first = int(first)
    last = int(last)

    #Appointments to show for current pnum
    pnum = int(pnum)-1
    start=pnum*2
    end=start+2

    if request.user.groups.all()[0].name == 'Photographer':
        ph = Photographer.objects.get(photographer_id=request.user.id)
        tempappointments = Appointment.objects.filter(photographer=ph)
        appointments = []
        for appointment in tempappointments:
            if appointment.zip != sys.maxsize:
                appointments.append(appointment)

        # for setting up pagination
        pages = [int(i) for i in range(1, math.ceil(len(appointments)/2)+1)]
        length = len(pages)
        if last == 0:
            last = min(3, length)

        if request.method=='POST':
            f = int(request.POST.get('first'))
            l = int(request.POST.get('last'))
            funct = request.POST.get('funct') 

            first, last = updateMarkers(f, l, funct)
            
            start = int(request.POST.get('start'))
            end = int(request.POST.get('end'))

        apt_list = appointments[start:end]
        context={
            'role':'Photographer', 
            'apt_list':apt_list, 
            'pages':pages, 
            'first':first, 
            'last':last, 
            'length':length,
            'start':start,
            'end':end,
            'pnum':pnum+1,
            'image': ph.image
            }    
        return render(request, 'pagination.html', context)

    else :
        cst = Customer.objects.get(customer_id=request.user.id)
        tempappointments = Appointment.objects.filter(customer=cst)
        appointments = []
        for appointment in tempappointments:
            if appointment.zip != sys.maxsize:
                appointments.append(appointment)

        # for setting up pagination
        pages = [int(i) for i in range(1, math.ceil(len(appointments)/2)+1)]
        length = len(pages)
        if last == 0:
           last = min(3, length)

        if request.method=='POST':
            f = int(request.POST.get('first'))
            l = int(request.POST.get('last'))
            funct = request.POST.get('funct') 

            first, last = updateMarkers(f, l, funct)

            start = int(request.POST.get('start'))
            end = int(request.POST.get('end'))

        apt_list = appointments[start:end]
        context={
            'role':'Customer', 
            'apt_list':apt_list, 
            'pages':pages, 
            'first':first, 
            'last':last, 
            'length':length,
            'start':start,
            'end':end,
            'pnum':pnum+1,
            'image': cst.image
            }    
        return render(request, 'pagination.html', context)


def updateMarkers(first, last, funct):
    if funct=='prev':
        first=first-1
        last = last-1

    else :
        first=first+1
        last = last+1

    return [first, last]


# For Blog of photographer
def blog(request, pid):
    pid = pid.split('_')
    ph = Photographer.objects.get(photographer_id=pid[0])
    post = Blog.objects.filter(photographer = ph).order_by('-date')
    context={}
    context['ph'] = ph
    context['post'] = post
    context['pid'] = int(pid[0])
    # rating
    stars=''
    if ph.rate == 1:
      stars = '★☆☆☆'
    elif ph.rate == 2:
      stars = '★★☆☆☆'
    elif ph.rate == 3:
      stars = '★★★☆☆'
    elif ph.rate == 4:
      stars = '★★★★☆' 
    else:
      stars = '★★★★★'    

    context['stars'] = stars

    if request.user.is_authenticated:
        if request.user.groups.all()[0].name == 'Customer':
            usr = Customer.objects.get(customer_id=request.user.id)
            context['role'] = 'Customer'
            context['image'] = usr.image
            context['id'] = usr.customer_id
            context['city'] = pid[1]
        else : 
            usr = Photographer.objects.get(photographer_id=request.user.id)
            context['role'] = 'Photographer'
            context['image'] = usr.image
            context['id'] = int(usr.photographer_id)
            # if int(pid[0]) == int(usr.photographer_id):
            #    print('Yes')

    return render(request, 'blog.html', context)


def deletePost(request, pid):
    post = Blog.objects.get(id=pid)
    post.delete()
    return redirect('/blog/'+str(post.photographer.photographer_id))


def editPost(request, pid):
    post = Blog.objects.get(id=pid)
    if request.method == 'POST':
        img1 = request.FILES['img1']
        img2 = request.FILES['img2']
        img3 = request.FILES['img3']
        img4 = request.FILES['img4']
        head = request.POST.get('head')
        date = request.POST.get('date')
        desc = request.POST.get('desc')
        post.img1 = img1
        post.img2 = img2
        post.img3 = img3
        post.img4 = img4
        post.head = head
        post.date = date
        post.desc = desc
        post.save()
        return redirect('/blog/'+str(post.photographer.photographer_id))
    else : 
        context = {}
        context['post'] = post
        context['id'] = post.photographer.photographer_id
        context['image'] = post.photographer.image
        return render(request, 'editPost.html', context)

    
def addPost(request, pid):
    if request.method == 'POST':
        photographer = Photographer.objects.get(photographer_id = pid)
        img1 = request.FILES['img1']
        img2 = request.FILES['img2']
        img3 = request.FILES['img3']
        img4 = request.FILES['img4']
        head = request.POST.get('head')
        date = request.POST.get('date')
        desc = request.POST.get('desc')
        post = Blog(
                    photographer = photographer,
                    img1 = img1,
                    img2 = img2,
                    img3 = img3,
                    img4 = img4,
                    head = head,
                    date = date,
                    desc = desc
                    )
        post.save()
        return redirect('/blog/'+str(pid))
    ph = Photographer.objects.get(photographer_id = pid)
    context = {}
    context['id'] = ph.photographer_id
    context['image'] = ph.image
    return render(request, 'addPost.html', context)



def changeStatus(request):
    if request.method == 'POST':
        ph = Photographer.objects.get(photographer_id=request.user.id)
        ph.status = request.POST.get('status')
        ph.save()

        return redirect('/profile0')    
    

def rescheduleAppointment(request, flag):
    if flag == 0:
        cst = request.POST.get('cust')
        photo = request.POST.get('photo')
        action = request.POST.get('action')
        
        customer = Customer.objects.get(customer_id=cst)
        photographer = Photographer.objects.get(photographer_id=photo)
        appointment = Appointment.objects.filter(customer=customer, photographer=photographer)[0]

        if action == 'Delete':
           appointment.delete()
           photographer.status = 'Available'
           photographer.save()
           messages.info(request, 'Appointment was deleted successfully')
           return redirect('/profile0')

        else :
            return redirect('/profile1_' + cst + '_' + photo)

    else :
        hours = int(request.POST.get('hours'))
        edate = request.POST.get('edate')
        cst = request.POST.get('cust')
        photo = request.POST.get('photo')

        customer = Customer.objects.get(customer_id=cst)
        photographer = Photographer.objects.get(photographer_id=photo)
        appointment = Appointment.objects.filter(customer=customer, photographer=photographer)[0]

        if hours < 24 or hours > 72 :
           messages.warning(request, 'Invalid selection of hours !') 
           return redirect('/profile0')
        else : 
            start_date = datetime.now() + timedelta(hours=hours)
            sdate = str(start_date).split(' ')
            edt = str(edate).split('T')
            flag = validateDate(sdate[0], sdate[1], edt[0], edt[1])
            if not flag:
                messages.warning(request, 'Invalid end date, appointment duration must be atleast 30 minutes !')
                return redirect('/profile0')
            

            appointment.start_date = start_date
            appointment.end_date = edate

            appointment.save()
            messages.info(request, 'Your Appointment was rescheduled successfully')
            return redirect('/profile0')


def feedbackForm(request, ap_id):
    if request.method == "POST":
        rate = request.POST.get('rate')
        query = request.POST.get('query')
        id = request.POST.get('ap_id')
        appointment = Appointment.objects.get(id=id)
        appointment.query = query
        appointment.save()
        ph = appointment.photographer
        n = ph.no_of_feedback + 1
        ph.rate = ph.rate*(n-1)  + int(rate)
        ph.rate = ph.rate/n
        ph.no_of_feedback = n
        ph.save()
        return redirect("/")
    return render(request, 'feedbackForm.html', {'ap_id':ap_id})
  