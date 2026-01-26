from django.db import models


class Region(models.Model):
    """
    Ethiopian administrative regions reference model
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # ISO code or internal code
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Regions"


class Skill(models.Model):
    """
    Standardized skill categories reference model
    """
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)  # e.g., 'domestic', 'technical', 'professional'
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Skills"


class Language(models.Model):
    """
    Supported languages reference model
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)  # ISO language code
    is_local = models.BooleanField(default=False)  # Ethiopian local language
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Languages"


class EducationLevel(models.Model):
    """
    Education classification system reference model
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0, db_index=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Education Levels"
        ordering = ['sort_order']


class Religion(models.Model):
    """
    Religion reference model
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Religions"


class WorkingTime(models.Model):
    """
    Working time preference reference model
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Working Time Preferences"


class JobCategory(models.Model):
    """
    Job category reference model
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Job Categories"


class WageUnit(models.Model):
    """
    Wage unit reference model (e.g., per month, per day, per hour)
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Wage Units"