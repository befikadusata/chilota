'use client';

import React from 'react';

interface ProfileCompletenessProps {
  completeness: number;
}

const ProfileCompleteness: React.FC<ProfileCompletenessProps> = ({ completeness }) => {
  // Determine color based on completeness percentage
  let color = 'bg-error'; // Low completeness
  if (completeness >= 50) color = 'bg-warning'; // Medium completeness
  if (completeness >= 80) color = 'bg-success'; // High completeness

  return (
    <div className="mb-4">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium">Profile Completeness</span>
        <span className="text-sm font-medium">{completeness}%</span>
      </div>
      <div className="w-full bg-muted rounded-full h-2.5" role="progressbar" aria-valuenow={completeness} aria-valuemin={0} aria-valuemax={100}>
        <div
          className={`h-2.5 rounded-full ${color}`}
          style={{ width: `${completeness}%` }}
        ></div>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        {completeness < 80
          ? 'Complete your profile to increase visibility to employers.'
          : 'Your profile is complete! Employers can now find you easily.'}
      </p>
    </div>
  );
};

export default ProfileCompleteness;