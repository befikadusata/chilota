from django.test import TestCase
from jobs.models import Region, Skill, Language, EducationLevel, Religion, WorkingTime, JobCategory, WageUnit


class RegionModelTest(TestCase):
    def test_region_creation(self):
        """Test creating a region with all required fields"""
        region = Region.objects.create(
            name='Addis Ababa',
            code='AA'
        )
        
        self.assertEqual(region.name, 'Addis Ababa')
        self.assertEqual(region.code, 'AA')
        self.assertEqual(str(region), 'Addis Ababa')

    def test_unique_region_name(self):
        """Test that region names must be unique"""
        Region.objects.create(name='Addis Ababa', code='AA')
        
        # Creating another region with the same name should raise an exception
        with self.assertRaises(Exception):
            Region.objects.create(name='Addis Ababa', code='AB')

    def test_unique_region_code(self):
        """Test that region codes must be unique"""
        Region.objects.create(name='Addis Ababa', code='AA')
        
        # Creating another region with the same code should raise an exception
        with self.assertRaises(Exception):
            Region.objects.create(name='Adama', code='AA')


class SkillModelTest(TestCase):
    def test_skill_creation(self):
        """Test creating a skill with all required fields"""
        skill = Skill.objects.create(
            name='Cooking',
            category='domestic'
        )
        
        self.assertEqual(skill.name, 'Cooking')
        self.assertEqual(skill.category, 'domestic')
        self.assertEqual(str(skill), 'Cooking')

    def test_skill_with_description(self):
        """Test creating a skill with optional description"""
        skill = Skill.objects.create(
            name='Advanced Cooking',
            category='professional',
            description='Expert cooking skills with international cuisine'
        )
        
        self.assertEqual(skill.name, 'Advanced Cooking')
        self.assertEqual(skill.category, 'professional')
        self.assertIn('international cuisine', skill.description.lower())

    def test_unique_skill_name(self):
        """Test that skill names must be unique"""
        Skill.objects.create(name='Cooking', category='domestic')
        
        # Creating another skill with the same name should raise an exception
        with self.assertRaises(Exception):
            Skill.objects.create(name='Cooking', category='professional')


class LanguageModelTest(TestCase):
    def test_language_creation(self):
        """Test creating a language with all required fields"""
        language = Language.objects.create(
            name='Amharic',
            code='am',
            is_local=True
        )
        
        self.assertEqual(language.name, 'Amharic')
        self.assertEqual(language.code, 'am')
        self.assertTrue(language.is_local)
        self.assertEqual(str(language), 'Amharic')

    def test_language_default_is_local_false(self):
        """Test that is_local defaults to False"""
        language = Language.objects.create(
            name='English',
            code='en'
        )
        
        self.assertEqual(language.name, 'English')
        self.assertEqual(language.code, 'en')
        self.assertFalse(language.is_local)

    def test_unique_language_name(self):
        """Test that language names must be unique"""
        Language.objects.create(name='Amharic', code='am')
        
        # Creating another language with the same name should raise an exception
        with self.assertRaises(Exception):
            Language.objects.create(name='Amharic', code='en')

    def test_unique_language_code(self):
        """Test that language codes must be unique"""
        Language.objects.create(name='Amharic', code='am')
        
        # Creating another language with the same code should raise an exception
        with self.assertRaises(Exception):
            Language.objects.create(name='Afaan Oromo', code='am')


class EducationLevelModelTest(TestCase):
    def test_education_level_creation(self):
        """Test creating an education level with all required fields"""
        education_level = EducationLevel.objects.create(
            name='Secondary Education',
            description='Completed secondary school education'
        )
        
        self.assertEqual(education_level.name, 'Secondary Education')
        self.assertIn('secondary school', education_level.description.lower())
        self.assertEqual(str(education_level), 'Secondary Education')

    def test_education_level_with_sort_order(self):
        """Test creating an education level with sort order"""
        education_level = EducationLevel.objects.create(
            name='Tertiary Education',
            description='College or university education',
            sort_order=3
        )
        
        self.assertEqual(education_level.name, 'Tertiary Education')
        self.assertEqual(education_level.sort_order, 3)

    def test_unique_education_level_name(self):
        """Test that education level names must be unique"""
        EducationLevel.objects.create(
            name='Secondary Education',
            description='Completed secondary school education'
        )
        
        # Creating another education level with the same name should raise an exception
        with self.assertRaises(Exception):
            EducationLevel.objects.create(
                name='Secondary Education',
                description='Another secondary education'
            )

    def test_education_level_ordering(self):
        """Test that education levels are ordered by sort_order"""
        # Create education levels with different sort orders
        level1 = EducationLevel.objects.create(
            name='Primary Education',
            sort_order=1
        )
        level3 = EducationLevel.objects.create(
            name='Tertiary Education',
            sort_order=3
        )
        level2 = EducationLevel.objects.create(
            name='Secondary Education',
            sort_order=2
        )
        
        # Get all education levels ordered by sort_order
        ordered_levels = EducationLevel.objects.all()
        
        # They should be in order: level1, level2, level3
        levels_list = list(ordered_levels)
        self.assertEqual(levels_list[0], level1)
        self.assertEqual(levels_list[1], level2)
        self.assertEqual(levels_list[2], level3)


class ReligionModelTest(TestCase):
    def test_religion_creation(self):
        """Test creating a religion with all required fields"""
        religion = Religion.objects.create(
            name='Ethiopian Orthodox',
            code='eth_orthodox'
        )
        
        self.assertEqual(religion.name, 'Ethiopian Orthodox')
        self.assertEqual(religion.code, 'eth_orthodox')
        self.assertEqual(str(religion), 'Ethiopian Orthodox')

    def test_unique_religion_name(self):
        """Test that religion names must be unique"""
        Religion.objects.create(name='Ethiopian Orthodox', code='eth_orthodox')
        
        # Creating another religion with the same name should raise an exception
        with self.assertRaises(Exception):
            Religion.objects.create(name='Ethiopian Orthodox', code='catholic')

    def test_unique_religion_code(self):
        """Test that religion codes must be unique"""
        Religion.objects.create(name='Ethiopian Orthodox', code='eth_orthodox')
        
        # Creating another religion with the same code should raise an exception
        with self.assertRaises(Exception):
            Religion.objects.create(name='Catholic', code='eth_orthodox')


class WorkingTimeModelTest(TestCase):
    def test_working_time_creation(self):
        """Test creating a working time preference with all required fields"""
        working_time = WorkingTime.objects.create(
            name='Full-time',
            code='full_time',
            description='Full-time employment (typically 40 hours per week)'
        )
        
        self.assertEqual(working_time.name, 'Full-time')
        self.assertEqual(working_time.code, 'full_time')
        self.assertIn('40 hours per week', working_time.description.lower())
        self.assertEqual(str(working_time), 'Full-time')

    def test_unique_working_time_name(self):
        """Test that working time names must be unique"""
        WorkingTime.objects.create(name='Full-time', code='full_time')
        
        # Creating another working time with the same name should raise an exception
        with self.assertRaises(Exception):
            WorkingTime.objects.create(name='Full-time', code='part_time')


class JobCategoryModelTest(TestCase):
    def test_job_category_creation(self):
        """Test creating a job category with all required fields"""
        category = JobCategory.objects.create(
            name='Domestic Work',
            description='Household and domestic services'
        )
        
        self.assertEqual(category.name, 'Domestic Work')
        self.assertIn('household', category.description.lower())
        self.assertEqual(str(category), 'Domestic Work')

    def test_unique_job_category_name(self):
        """Test that job category names must be unique"""
        JobCategory.objects.create(
            name='Domestic Work',
            description='Household and domestic services'
        )
        
        # Creating another job category with the same name should raise an exception
        with self.assertRaises(Exception):
            JobCategory.objects.create(
                name='Domestic Work',
                description='Another domestic services category'
            )


class WageUnitModelTest(TestCase):
    def test_wage_unit_creation(self):
        """Test creating a wage unit with all required fields"""
        wage_unit = WageUnit.objects.create(
            name='Per Month',
            code='per_month',
            description='Wage paid on a monthly basis'
        )
        
        self.assertEqual(wage_unit.name, 'Per Month')
        self.assertEqual(wage_unit.code, 'per_month')
        self.assertIn('monthly', wage_unit.description.lower())
        self.assertEqual(str(wage_unit), 'Per Month')

    def test_unique_wage_unit_name(self):
        """Test that wage unit names must be unique"""
        WageUnit.objects.create(name='Per Month', code='per_month')
        
        # Creating another wage unit with the same name should raise an exception
        with self.assertRaises(Exception):
            WageUnit.objects.create(name='Per Month', code='per_day')