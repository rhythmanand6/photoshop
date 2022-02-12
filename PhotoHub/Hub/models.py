from statistics import mode
from django.db import models
from numpy import blackman


class Customer(models.Model):
    customer_id = models.IntegerField(default=0, null=True, blank=True)
    fname = models.CharField(max_length=50, null=True, blank=True)
    lname = models.CharField(max_length=50, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True,  blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=200, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank = True)

    def __str__(self):
        return str(self.fname) + " " + str(self.lname)


class Photographer(models.Model):
   
    CATEGORY_OPTIONS = (
        ('Event', 'Event'),
        ('Fashion', 'Fashion'),
        ('Sports', 'Sports'),
        ('Food', 'Food'),
        ('Art_and_Portrait', 'Art_and_Portrait'),
        ('Architecture', 'Architecture'),
        ('Documentary', 'Documentary'),
        ('Travel', 'Travel'),
        ('Modelling_and_Lifestyle', 'Modelling_and_Lifestyle'),
        ('Nature_and_Wildlife', 'Natue_and_Wildlife'),
        ('Product', 'Product'),
        ('Photo_Journalism', 'Photo_journalism')
    )


    STATUS_OPTIONS = (
        ('Available', 'Available'),
        ('Busy', 'Busy')
    )

    photographer_id = models.IntegerField(default=0, null=True, blank=True)
    fname = models.CharField(max_length=50, null=True, blank=True)
    lname = models.CharField(max_length=50, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True,  blank=True)
    age = models.IntegerField(default=0, null=True, blank=True)
    category = models.CharField(
        max_length=100,
        choices = CATEGORY_OPTIONS,
        null=True, 
        blank=True
    )
    area = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length = 20,
        choices = STATUS_OPTIONS,
        default = 'Available',
        null=True, 
        blank=True
    )
    image = models.ImageField(upload_to="images/", blank=True, null = True)
    bio = models.CharField(max_length=500, null=True, blank=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    tweeter = models.CharField(max_length=100, blank=True, null=True)
    rate = models.IntegerField(default=0, blank=True, null=True)
    no_of_feedback = models.IntegerField(default=0)

    def __str__(self):
        return str(self.fname) + " " + str(self.lname)


class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)    
    photographer = models.ForeignKey(Photographer, on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=200, null=True, blank=True)
    zip = models.IntegerField(null=True, blank=True)
    appointment_status = models.CharField(max_length=50, null=True, blank=True)
    feedback = models.BooleanField(default=False)
    query = models.CharField(max_length=5000, blank=True, null=True)

    def __str__(self):
        return str(self.customer.fname) + " " + str(self.customer.lname) +'('+str(self.photographer.fname)+')'


class City(models.Model):
    city = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.city)


class Blog(models.Model):
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE)
    img1 = models.ImageField(upload_to="images/", blank=True, null=True)
    img2 = models.ImageField(upload_to="images/", blank=True, null=True)
    img3 = models.ImageField(upload_to="images/", blank=True, null=True)
    img4 = models.ImageField(upload_to="images/", blank=True, null=True)
    head = models.CharField(max_length=50)
    date = models.DateField()
    desc = models.CharField(max_length=5000)

    def __str__(self):
        return str(self.photographer.fname) + " " + str(self.photographer.lname)