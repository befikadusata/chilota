//-
//- Types for Job Postings
//-

export interface Job {
    id: number;
    title: string;
    description: string;
    location: string;
    salary: number;
    skills: string[];
    created_at: string;
    updated_at: string;
    employer: number;
    status: string;
    applicants: any[];
}
