'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { Button } from '@/components/ui/Button';
import ProfileCompleteness from '@/components/ui/ProfileCompleteness';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function WorkerDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [workerProfile, setWorkerProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.role !== 'worker') {
      router.push('/login');
      return;
    }

    // Fetch worker profile
    const fetchWorkerProfile = async () => {
      try {
        // Placeholder for actual API call
        // const response = await workersApi.getProfile();
        // setWorkerProfile(response.data);

        // For now, simulate the API call
        setTimeout(() => {
          setWorkerProfile({
            id: user.id,
            full_name: user.full_name || user.email,
            profession: 'Housekeeper',
            experience_years: 5,
            hourly_rate: 15,
            profile_completion_percentage: 75,
            avatar: null,
            fayda_id: 'FAYDA123456',
            age: 28,
            place_of_birth: 'Addis Ababa',
            region_of_origin: 'Oromia',
            current_location: 'Bole',
            education_level: 'High School',
            religion: 'Orthodox',
            working_time: 'Full-time',
            years_experience: 5,
            skills: ['Cleaning', 'Cooking', 'Childcare'],
            languages: ['Amharic', 'English'],
            emergency_contact_name: 'John Doe',
            emergency_contact_phone: '+251912345678',
            profile_photo: null,
            certifications: [],
            profile_completeness: 75,
          });
          setLoading(false);
        }, 500);
      } catch (err: any) {
        setError(err.message || 'Failed to load worker profile');
        console.error(err);

        if (err.message?.includes('404')) {
          // Worker profile doesn't exist, redirect to create profile
          router.push('/dashboard/worker/create');
        }
        setLoading(false);
      }
    };

    fetchWorkerProfile();
  }, [user, router]);

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  if (error) {
    return <div className="p-6">Error: {error}</div>;
  }

  if (!workerProfile) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-foreground">Worker Dashboard</h1>
        <p className="text-muted-foreground">You don't have a worker profile yet. Please create one to get started.</p>
        <Button onClick={() => router.push('/dashboard/worker/create')}>
          Create Profile
        </Button>
      </div>
    );
  }

  // Calculate progress for different sections
  const calculateSectionProgress = () => {
    if (!workerProfile) return {};

    const personalInfoComplete = workerProfile.fayda_id &&
                                 workerProfile.full_name &&
                                 workerProfile.age &&
                                 workerProfile.place_of_birth &&
                                 workerProfile.region_of_origin &&
                                 workerProfile.current_location;

    const contactInfoComplete = workerProfile.emergency_contact_name &&
                               workerProfile.emergency_contact_phone;

    const professionalInfoComplete = workerProfile.education_level &&
                                    workerProfile.religion &&
                                    workerProfile.working_time &&
                                    workerProfile.years_experience &&
                                    workerProfile.skills.length > 0;

    const profilePhotoComplete = !!workerProfile.profile_photo;

    const certificationComplete = !!workerProfile.certifications;

    return {
      personalInfo: personalInfoComplete ? 100 : 0,
      contactInfo: contactInfoComplete ? 100 : 0,
      professionalInfo: professionalInfoComplete ? 100 : 0,
      profilePhoto: profilePhotoComplete ? 100 : 0,
      certification: certificationComplete ? 100 : 0,
    };
  };

  const sectionProgress = calculateSectionProgress();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground">Worker Dashboard</h1>
      <div className="mt-4">
        <h2 className="text-xl font-semibold text-foreground">Your Profile</h2>

        <ProfileCompleteness completeness={workerProfile.profile_completeness} />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="p-4 bg-card rounded shadow">
            <h3 className="font-medium text-card-foreground">Personal Information</h3>
            <p className="text-muted-foreground"><span className="font-semibold">Name:</span> {workerProfile.full_name}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Fayda ID:</span> {workerProfile.fayda_id}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Age:</span> {workerProfile.age}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Place of Birth:</span> {workerProfile.place_of_birth}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Region:</span> {workerProfile.region_of_origin}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Location:</span> {workerProfile.current_location}</p>
            <div className="mt-2">
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-success h-2 rounded-full"
                  style={{ width: `${sectionProgress.personalInfo}%` }}
                ></div>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Personal Info: {sectionProgress.personalInfo}% Complete</p>
            </div>
          </div>

          <div className="p-4 bg-card rounded shadow">
            <h3 className="font-medium text-card-foreground">Professional Information</h3>
            <p className="text-muted-foreground"><span className="font-semibold">Education:</span> {workerProfile.education_level}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Religion:</span> {workerProfile.religion}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Working Time:</span> {workerProfile.working_time}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Experience:</span> {workerProfile.years_experience} years</p>
            <p className="text-muted-foreground"><span className="font-semibold">Skills:</span> {workerProfile.skills.join(', ')}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Languages:</span> {workerProfile.languages.map((lang: any) =>
              typeof lang === 'string' ? lang : lang.language
            ).join(', ')}</p>
            <div className="mt-2">
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${sectionProgress.professionalInfo}%` }}
                ></div>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Professional Info: {sectionProgress.professionalInfo}% Complete</p>
            </div>
          </div>

          <div className="p-4 bg-card rounded shadow">
            <h3 className="font-medium text-card-foreground">Contact Information</h3>
            <p className="text-muted-foreground"><span className="font-semibold">Emergency Contact:</span> {workerProfile.emergency_contact_name}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Emergency Phone:</span> {workerProfile.emergency_contact_phone}</p>
            <div className="mt-2">
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-warning h-2 rounded-full"
                  style={{ width: `${sectionProgress.contactInfo}%` }}
                ></div>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Contact Info: {sectionProgress.contactInfo}% Complete</p>
            </div>
          </div>

          <div className="p-4 bg-card rounded shadow">
            <h3 className="font-medium text-card-foreground">Media & Documents</h3>
            <p className="text-muted-foreground"><span className="font-semibold">Profile Photo:</span> {workerProfile.profile_photo ? 'Uploaded' : 'Not uploaded'}</p>
            <p className="text-muted-foreground"><span className="font-semibold">Certifications:</span> {workerProfile.certifications ? 'Uploaded' : 'Not uploaded'}</p>
            <div className="flex space-x-2 mt-2">
              <div className="w-1/2">
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-info h-2 rounded-full"
                    style={{ width: `${sectionProgress.profilePhoto}%` }}
                  ></div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">Photo: {sectionProgress.profilePhoto}% Complete</p>
              </div>
              <div className="w-1/2">
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-accent h-2 rounded-full"
                    style={{ width: `${sectionProgress.certification}%` }}
                  ></div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">Cert: {sectionProgress.certification}% Complete</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-4">
          <Button onClick={() => router.push('/dashboard/worker/edit')}>
            Edit Profile
          </Button>
          <Button onClick={() => router.push('/dashboard/worker/upload-photo')}>
            Upload Photo
          </Button>
          <Button onClick={() => router.push('/dashboard/worker/upload-certification')}>
            Upload Certification
          </Button>
        </div>
      </div>
    </div>
  );
}