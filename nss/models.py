from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class University(models.Model):
    name = models.CharField(max_length=100, unique=True)
    directorate = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Universities"
        ordering = ['name']

class College(models.Model):
    name = models.CharField(max_length=100, unique=True)
    directorate = models.CharField(max_length=255)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    nss_unit = models.IntegerField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.university.name})"

    class Meta:
        ordering = ['university__name', 'name']

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('university', 'University'),
        ('college_po', 'College Program Officer'),
        ('college_vs', 'College Volunteer Secretary'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    def clean(self):
        super().clean()
        # Validate role-specific requirements
        if self.role == 'university' and not self.university:
            raise ValidationError("University users must be associated with a university")
        if self.role in ['college_po', 'college_vs'] and not self.college:
            raise ValidationError("College staff must be associated with a college")
        if self.college and self.university and self.college.university != self.university:
            raise ValidationError("Selected college must belong to the selected university")

    def save(self, *args, **kwargs):
        # Auto-set university for college staff
        if self.role in ['college_po', 'college_vs'] and self.college and not self.university:
            self.university = self.college.university
        super().save(*args, **kwargs)

    def is_admin(self):
        return self.role == 'admin'
    
    def is_university(self):
        return self.role == 'university'
    
    def is_college_po(self):
        return self.role == 'college_po'
    
    def is_college_vs(self):
        return self.role == 'college_vs'
    
    def get_accessible_colleges(self):
        """Returns queryset of colleges this user can access"""
        if self.is_admin():
            return College.objects.all()
        elif self.is_university():
            return College.objects.filter(university=self.university)
        elif self.college:
            return College.objects.filter(pk=self.college.pk)
        return College.objects.none()

    def __str__(self):
        role_display = self.get_role_display()
        if self.university:
            return f"{self.username} ({role_display} - {self.university.name})"
        if self.college:
            return f"{self.username} ({role_display} - {self.college.name})"
        return f"{self.username} ({role_display})"

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['role', 'username']

class Department(models.Model):
    name = models.CharField(max_length=100)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'college')
        ordering = ['college__name', 'name']

    def __str__(self):
        return f"{self.name} - {self.college.name}"

class Programme(models.Model):
    GRAD_LEVEL_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('PhD', 'Doctorate'),
        ('Diploma', 'Diploma'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    duration_years = models.IntegerField()
    grad_level = models.CharField(max_length=10, choices=GRAD_LEVEL_CHOICES)
    code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'department')
        ordering = ['department__college__name', 'department__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.department.college.name})"

class Volunteer(models.Model):
    SEX_CHOICES = [('male', 'Male'), ('female', 'Female')]
    YEAR_CHOICES = [(1, '1'), (2, '2'), (3, '3')]
    COMMUNITY_CHOICES = [('ST', 'ST'), ('SC', 'SC'), ('General', 'General'), ('OBC', 'OBC')]
    BLOOD_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    UNIT_CHOICES = [(4, '4'), (5, '5'), (96, '96')]

    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    status = models.CharField(max_length=20, default='active')
    guard_name = models.CharField(max_length=25)
    guard_mob_no = models.BigIntegerField()
    sex = models.CharField(max_length=15, choices=SEX_CHOICES)
    dob = models.DateField()
    year = models.IntegerField(choices=YEAR_CHOICES)
    community = models.CharField(max_length=15, choices=COMMUNITY_CHOICES)
    address = models.TextField()
    blood_group = models.CharField(max_length=15, choices=BLOOD_CHOICES)
    height = models.IntegerField()
    unit = models.IntegerField(choices=UNIT_CHOICES)
    weight = models.IntegerField()
    mobile_no = models.BigIntegerField()
    Email_id = models.EmailField()
    year_of_enrollment = models.IntegerField()
    cultural_talents = models.TextField()
    hobbies = models.TextField()
    roll_no = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='volunteer_images/')
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_volunteers')

    class Meta:
        unique_together = ('roll_no', 'college')
        ordering = ['college__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.college.name})"

class Event(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    date = models.DateField()
    is_campus_event = models.BooleanField(default=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')

    class Meta:
        unique_together = ('event_name', 'college', 'date')
        ordering = ['-date', 'college__name']

    def __str__(self):
        return f"{self.event_name} ({self.college.name})"

class AttendanceStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    date = models.DateField()
    unit = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendances')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_attendances')

    class Meta:
        unique_together = ('date', 'unit', 'college', 'event')
        ordering = ['-date', 'college__name']

    def __str__(self):
        return f"{self.event} - {self.get_status_display()}"

class Attendance(models.Model):
    attendance_status = models.ForeignKey(AttendanceStatus, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    date = models.DateField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    no_of_hours = models.IntegerField()

    class Meta:
        unique_together = ('volunteer', 'event', 'date')
        ordering = ['-date', 'volunteer__name']

    def __str__(self):
        return f"{self.volunteer} - {self.event}"

class EventDetails(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    des = models.TextField()
    expense = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Details of {self.event}"

class EventPhotos(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='event_photos/')

    class Meta:
        verbose_name_plural = "Event Photos"

    def __str__(self):
        return f"Photo for {self.event}"

class Camp(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField()
    location = models.CharField(max_length=255)
    theme = models.CharField(max_length=255, null=True, blank=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='coordinated_camps')

    class Meta:
        unique_together = ('name', 'college', 'from_date')
        ordering = ['-from_date', 'college__name']

    def __str__(self):
        return f"{self.name} ({self.college.name})"

class CampAttendance(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('volunteer', 'camp')
        ordering = ['camp__from_date', 'volunteer__name']

    def __str__(self):
        return f"{self.volunteer} - {self.camp}"

class CampEvent(models.Model):
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=60)
    des = models.TextField()
    date = models.DateField()

    class Meta:
        ordering = ['camp__from_date', 'date']

    def __str__(self):
        return self.event_name

class CampEventPhotos(models.Model):
    event = models.ForeignKey(CampEvent, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='camp_event_photos/')

    class Meta:
        verbose_name_plural = "Camp Event Photos"

    def __str__(self):
        return f"Photo for {self.event}"