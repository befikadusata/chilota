'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { jobsApi } from '@/lib/api';
import { useAuth } from '@/lib/auth/auth-context';

import { Job } from '@/lib/types';



export default function JobListings() {

  const [jobs, setJobs] = useState<Job[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);



  const { user } = useAuth();

  useEffect(() => {

    const fetchJobs = async () => {
      try {
        if (!user) {
          setError('Not authenticated');
          return;
        }

        const data = await jobsApi.getByEmployer(user.id.toString()); // Pass the employer ID as string
        setJobs(data);
      } catch (err: any) {

        setError(err.message || 'Failed to load jobs');

        console.error(err);

      } finally {

        setLoading(false);

      }

    };



    fetchJobs();

  }, [user]);



  if (loading) {

    return <div>Loading jobs...</div>;

  }



  if (loading) {
    return <div>Loading jobs...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (jobs.length === 0) {

    return (

      <div>

        <p>You have not posted any jobs yet.</p>

        <Link href="/dashboard/employer/create-job">

            <Button className="mt-4">Post a Job</Button>

        </Link>

      </div>

    );

  }



  return (

    <div>

      <div className="flow-root">

        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">

          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">

                        <table className="min-w-full divide-y divide-border">

                          <thead>

                            <tr>

                              <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-foreground sm:pl-0">

                                Job Title

                              </th>

                              <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">

                                Applicants

                              </th>

                              <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-foreground">

                                Status

                              </th>

                              <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-0">

                                <span className="sr-only">Edit</span>

                              </th>

                            </tr>

                          </thead>

                          <tbody className="divide-y divide-border">

                            {jobs.map((job) => (

                              <tr key={job.id}>

                                <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-foreground sm:pl-0">

                                  {job.title}

                                  <p className="text-muted-foreground">{job.location}</p>

                                </td>

                                <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">{job.applications_count}</td>

                                <td className="whitespace-nowrap px-3 py-4 text-sm text-muted-foreground">

                                  <span

                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${

                                      job.status === 'active' ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'

                                    }`}

                                  >

                                    {job.status.charAt(0).toUpperCase() + job.status.slice(1)}

                                  </span>

                                </td>

                                <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">

                                  <a href="#" className="text-primary hover:text-primary-foreground/80">

                                    Manage

                                  </a>

                                </td>

                              </tr>

                            ))}

                          </tbody>

                        </table>

          </div>

        </div>

      </div>

    </div>

  );

}
