from django.db import models

# Create your models here.
class Agent(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.first_name

    def save_resident(self):
        self.save()    

    class Meta:
        ordering = ['first_name']

class Estate(models.Model):
    locations = (
        ('Westlands', 'Westlands'),
        ('Parklands', 'Parklands'),
        ('Kilimani', 'Kilimani'),
        ('Machakos', 'Machakos'),
        ('Nakuru', 'Nakuru'),
        ('Kisumu', 'Kisumu'),
        ('Bungoma', 'Bungoma'),
        ('Ruaka', 'Ruaka'),
        ('Ruiru', 'Ruiru'),
        ('Kibera', 'Kibera'),
        ('Kitengela', 'Kitengela'),
        ('Athi River', 'Athi River'),        
        ('Thika', 'Thika'),
        ('Syokimau', 'Syokimau'),
        ('Utawala', 'Utawala'),
        ('Kasarani', 'Kasarani'),
        ('Ngong', 'Ngong'),
        ('Embu', 'Embu'),
        ('Runda', 'Runda'),
        ('Voi', 'Voi'),        
        ('Komarock', 'Komarock'), 
        ('Donholm', 'Donholm'),  
        ('Kileleshwa', 'Kileleshwa'),
        ('Mombasa', 'Mombasa'),       
    )
    name = models.CharField(max_length=100, default='',blank=True)
    location_name = models.CharField(max_length=100, choices=locations)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.name