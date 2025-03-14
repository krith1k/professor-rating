from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    # Unique identifier provided by the admin (e.g. 'JE1')
    professor_id = models.CharField(max_length=10, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.professor_id} - Professor {self.last_name}"

class Module(models.Model):
    # Unique module code (e.g. 'CD1')
    module_code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.module_code}: {self.name}"

class ModuleInstance(models.Model):
    # Represents a specific instance of a module in a given year and semester
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()  # The first year of the academic year, e.g. 2018 for 2018-19
    semester = models.IntegerField()  # Typically 1 or 2
    professors = models.ManyToManyField(Professor)

    class Meta:
        # Ensure there are no duplicate module instances for the same module, year, and semester
        unique_together = ('module', 'year', 'semester')

    def __str__(self):
        return f"{self.module.module_code} - {self.year} Semester {self.semester}"

class Rating(models.Model):
    # Each rating is linked toa user, a professor, and a module instance
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Value from 1 to 5

    class Meta:
        # A user can rate each professor in a given module instance only once
        unique_together = ('user', 'professor', 'module_instance')

    def __str__(self):
        return f"Rating by {self.user.username} for {self.professor} in {self.module_instance}: {self.rating}"