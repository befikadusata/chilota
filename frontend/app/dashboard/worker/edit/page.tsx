'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/auth-context';
import { Button } from '@/components/ui/Button';

export default function EditWorkerProfile() {
  const router = useRouter();
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    fayda_id: '',
    full_name: '',
    age: '',
    place_of_birth: '',
    region_of_origin: '',
    current_location: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    languages: [],
    education_level: '',
    religion: '',
    working_time: '',
    skills: [],
    years_experience: '',
  });

  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [profileLoaded, setProfileLoaded] = useState(false);

  // Ethiopian languages and skills (these would come from the backend in a real app)
  const ethiopianLanguages = [
    'Amharic', 'Oromo', 'Tigrinya', 'Afar', 'Somali', 'Gedeo',
    'Sidama', 'Wolaytta', 'Hadiyya', 'Afaan', 'Gamo', 'Gurage'
  ];

  const ethiopianSkills = [
    'Cooking', 'Cleaning', 'Childcare', 'Elderly Care', 'Gardening',
    'Driving', 'Laundry', 'Ironing', 'Housekeeping', 'Pet Care'
  ];

  const educationLevels = [
    'primary', 'secondary', 'tertiary', 'vocational', 'none'
  ];

  const religions = [
    'eth_orthodox', 'islam', 'protestant', 'catholic', 'traditional', 'other'
  ];

  const workingTimeOptions = [
    'full_time', 'part_time', 'live_in'
  ];

  // Validation functions
  const validateField = (name: string, value: string) => {
    let errorMsg = '';

    switch (name) {
      case 'fayda_id':
        if (!value.trim()) {
          errorMsg = 'Fayda ID is required';
        } else if (!/^[A-Z0-9]+$/.test(value)) {
          errorMsg = 'Fayda ID can only contain letters and numbers';
        }
        break;
      case 'full_name':
        if (!value.trim()) {
          errorMsg = 'Full name is required';
        } else if (value.trim().length < 2) {
          errorMsg = 'Full name must be at least 2 characters';
        }
        break;
      case 'age':
        const age = parseInt(value);
        if (!value) {
          errorMsg = 'Age is required';
        } else if (isNaN(age) || age < 16 || age > 65) {
          errorMsg = 'Age must be between 16 and 65';
        }
        break;
      case 'place_of_birth':
        if (!value.trim()) {
          errorMsg = 'Place of birth is required';
        }
        break;
      case 'region_of_origin':
        if (!value.trim()) {
          errorMsg = 'Region of origin is required';
        }
        break;
      case 'current_location':
        if (!value.trim()) {
          errorMsg = 'Current location is required';
        }
        break;
      case 'emergency_contact_name':
        if (!value.trim()) {
          errorMsg = 'Emergency contact name is required';
        }
        break;
      case 'emergency_contact_phone':
        if (!value.trim()) {
          errorMsg = 'Emergency contact phone is required';
        } else if (!/^\+?[0-9\s\-\(\)]+$/.test(value)) {
          errorMsg = 'Please enter a valid phone number';
        }
        break;
      case 'education_level':
        if (!value) {
          errorMsg = 'Education level is required';
        }
        break;
      case 'religion':
        if (!value) {
          errorMsg = 'Religion is required';
        }
        break;
      case 'working_time':
        if (!value) {
          errorMsg = 'Working time preference is required';
        }
        break;
      case 'years_experience':
        const exp = parseInt(value);
        if (!value) {
          errorMsg = 'Years of experience is required';
        } else if (isNaN(exp) || exp < 0) {
          errorMsg = 'Years of experience must be a non-negative number';
        }
        break;
      default:
        break;
    }

    setErrors(prev => ({
      ...prev,
      [name]: errorMsg
    }));

    return errorMsg;
  };

  useEffect(() => {
    const fetchWorkerProfile = async () => {
      try {
        const response = await fetch('/api/workers/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setFormData({
            fayda_id: data.fayda_id || '',
            full_name: data.full_name || '',
            age: data.age ? data.age.toString() : '',
            place_of_birth: data.place_of_birth || '',
            region_of_origin: data.region_of_origin || '',
            current_location: data.current_location || '',
            emergency_contact_name: data.emergency_contact_name || '',
            emergency_contact_phone: data.emergency_contact_phone || '',
            languages: data.languages || [],
            education_level: data.education_level || '',
            religion: data.religion || '',
            working_time: data.working_time || '',
            skills: data.skills || [],
            years_experience: data.years_experience ? data.years_experience.toString() : '',
          });

          // Set languages
          const langs = data.languages.map((lang: any) =>
            typeof lang === 'string' ? lang : lang.language
          );
          setSelectedLanguages(langs);

          // Set skills
          setSelectedSkills(data.skills);
          setProfileLoaded(true);
        } else {
          router.push('/dashboard/worker');
        }
      } catch (error) {
        console.error('Error fetching worker profile:', error);
        router.push('/dashboard/worker');
      }
    };

    if (user?.role === 'worker') {
      fetchWorkerProfile();
    } else {
      router.push('/login');
    }
  }, [user, router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;

    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Validate field on change
    validateField(name, value);
  };

  const handleLanguageChange = (language: string) => {
    if (selectedLanguages.includes(language)) {
      setSelectedLanguages(selectedLanguages.filter(lang => lang !== language));
    } else {
      setSelectedLanguages([...selectedLanguages, language]);
    }
  };

  const handleSkillChange = (skill: string) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const validateForm = () => {
    let isValid = true;
    const newErrors: Record<string, string> = {};

    // Validate all fields
    Object.entries(formData).forEach(([key, value]) => {
      if (typeof value === 'string') {
        const errorMsg = validateField(key, value);
        if (errorMsg) {
          newErrors[key] = errorMsg;
          isValid = false;
        }
      }
    });

    // Validate languages
    if (selectedLanguages.length === 0) {
      newErrors.languages = 'Please select at least one language';
      isValid = false;
    }

    // Validate skills
    if (selectedSkills.length === 0) {
      newErrors.skills = 'Please select at least one skill';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const profileData = {
        ...formData,
        languages: selectedLanguages.map(lang => ({ language: lang, proficiency: 'intermediate' })),
        skills: selectedSkills,
        age: parseInt(formData.age),
        years_experience: parseInt(formData.years_experience),
      };

      const response = await fetch('/api/workers/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        router.push('/dashboard/worker');
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update profile');
      }
    } catch (err) {
      setError('An error occurred while updating the profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (user?.role !== 'worker' || !profileLoaded) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Edit Worker Profile</h1>

      {error && <div className="bg-error/10 border border-error/50 text-error px-4 py-3 rounded mb-4">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Fayda ID</label>
            <input
              type="text"
              name="fayda_id"
              value={formData.fayda_id}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.fayda_id ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.fayda_id && <p className="text-error text-xs mt-1">{errors.fayda_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.full_name ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.full_name && <p className="text-error text-xs mt-1">{errors.full_name}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Age</label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleInputChange}
              required
              min="16"
              max="65"
              className={`w-full p-2 border ${errors.age ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.age && <p className="text-error text-xs mt-1">{errors.age}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Place of Birth</label>
            <input
              type="text"
              name="place_of_birth"
              value={formData.place_of_birth}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.place_of_birth ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.place_of_birth && <p className="text-error text-xs mt-1">{errors.place_of_birth}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Region of Origin</label>
            <input
              type="text"
              name="region_of_origin"
              value={formData.region_of_origin}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.region_of_origin ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.region_of_origin && <p className="text-error text-xs mt-1">{errors.region_of_origin}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Current Location</label>
            <input
              type="text"
              name="current_location"
              value={formData.current_location}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.current_location ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.current_location && <p className="text-error text-xs mt-1">{errors.current_location}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Emergency Contact Name</label>
            <input
              type="text"
              name="emergency_contact_name"
              value={formData.emergency_contact_name}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.emergency_contact_name ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.emergency_contact_name && <p className="text-error text-xs mt-1">{errors.emergency_contact_name}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Emergency Contact Phone</label>
            <input
              type="text"
              name="emergency_contact_phone"
              value={formData.emergency_contact_phone}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.emergency_contact_phone ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.emergency_contact_phone && <p className="text-error text-xs mt-1">{errors.emergency_contact_phone}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Education Level</label>
            <select
              name="education_level"
              value={formData.education_level}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.education_level ? 'border-error' : 'border-input'} rounded`}
            >
              <option value="">Select Education Level</option>
              {educationLevels.map(level => (
                <option key={level} value={level}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </option>
              ))}
            </select>
            {errors.education_level && <p className="text-error text-xs mt-1">{errors.education_level}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Religion</label>
            <select
              name="religion"
              value={formData.religion}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.religion ? 'border-error' : 'border-input'} rounded`}
            >
              <option value="">Select Religion</option>
              {religions.map(rel => (
                <option key={rel} value={rel}>
                  {rel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
            {errors.religion && <p className="text-error text-xs mt-1">{errors.religion}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Working Time Preference</label>
            <select
              name="working_time"
              value={formData.working_time}
              onChange={handleInputChange}
              required
              className={`w-full p-2 border ${errors.working_time ? 'border-error' : 'border-input'} rounded`}
            >
              <option value="">Select Working Time</option>
              {workingTimeOptions.map(time => (
                <option key={time} value={time}>
                  {time.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
            {errors.working_time && <p className="text-error text-xs mt-1">{errors.working_time}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Years of Experience</label>
            <input
              type="number"
              name="years_experience"
              value={formData.years_experience}
              onChange={handleInputChange}
              required
              min="0"
              className={`w-full p-2 border ${errors.years_experience ? 'border-error' : 'border-input'} rounded`}
            />
            {errors.years_experience && <p className="text-error text-xs mt-1">{errors.years_experience}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Languages</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {ethiopianLanguages.map(lang => (
              <label key={lang} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedLanguages.includes(lang)}
                  onChange={() => handleLanguageChange(lang)}
                  className="mr-2"
                />
                {lang}
              </label>
            ))}
          </div>
          {errors.languages && <p className="text-error text-xs mt-1">{errors.languages}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Skills</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {ethiopianSkills.map(skill => (
              <label key={skill} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedSkills.includes(skill)}
                  onChange={() => handleSkillChange(skill)}
                  className="mr-2"
                />
                {skill}
              </label>
            ))}
          </div>
          {errors.skills && <p className="text-error text-xs mt-1">{errors.skills}</p>}
        </div>

        <div className="flex justify-end space-x-4">
          <Button type="button" onClick={() => router.back()}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Updating...' : 'Update Profile'}
          </Button>
        </div>
      </form>
    </div>
  );
}