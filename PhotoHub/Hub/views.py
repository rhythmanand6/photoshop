from django.http import HttpResponse
from django.shortcuts import render, redirect

#Importing User model for creating a User instance or authenticating and login , logout
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout

#Importing Customer and Photographer module
from Hub.models import Customer, Photographer

#For message displaying
from django.contrib import messages

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.groups.all()[0].name == 'Photographer':
            ph = Photographer.objects.get(photographer_id=request.user.id)
            context= {'image': ph.image}
            return render(request, 'landing.html', context)

        else : 
            cst = Customer.objects.get(customer_id=request.user.id)
            context= {'image':cst.image}
            return render(request, 'landing.html', context)

    return render(request, 'landing.html')
    

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


def profile(request):
    if request.user.groups.all()[0].name == 'Photographer':
        ph = Photographer.objects.get(photographer_id=request.user.id)
        context={
                'fname': ph.fname, 'lname':ph.lname, 'gender':ph.gender, 'phone':ph.phone, 'city':ph.city,
                'email':ph.email, 'age':ph.age, 'category':ph.category, 'role':'Photographer', 'image':ph.image
             }
        
        return render(request, 'profile.html',  context)
    else :
        cst = Customer.objects.get(customer_id=request.user.id)
        context={
                'fname': cst.fname, 'lname':cst.lname, 'phone':cst.phone, 'city':cst.city,
                'email':cst.email, 'role':'Customer', 'image':cst.image
             }
        return render(request, 'profile.html', context)



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


def checkout(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.groups.all()[0].name == 'Photographer':
            ph = Photographer.objects.get(photographer_id=request.user.id)
            context['image'] = ph.image

        else :
            cst = Customer.objects.get(customer_id=request.user.id)
            context['image'] = cst.image
    
    #creates dictionary for each object
    catphs = Photographer.objects.values('category', 'photographer_id')
    cats = {item['category'] for item in catphs}
    #print(cats)
    
    allcatph = []
    for cat in cats:
        catph = Photographer.objects.filter(category=cat)
        tuple = (cat, catph)
        allcatph.append(tuple)

   # print(allcatph)    
    context['allcatph'] = allcatph
    return render(request, 'checkout.html', context)



def allfromCat(request, cat):
    context = {}
    if request.user.is_authenticated:
        if request.user.groups.all()[0].name == 'Photographer':
            ph = Photographer.objects.get(photographer_id=request.user.id)
            context['image'] = ph.image

        else :
            cst = Customer.objects.get(customer_id=request.user.id)
            context['image'] = cst.image

    catph = Photographer.objects.filter(category=cat)
    context['catph'] = catph
    context['category'] = cat
    return render(request, 'allfromCat.html', context)
