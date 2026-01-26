//-
//- Create Job Page
//-
import { Button } from '@/components/ui/Button';

export default function CreateJobPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Post a New Job</h1>
      <form className="bg-card rounded-lg shadow p-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="jobTitle" className="block text-sm font-medium text-foreground">
              Job Title
            </label>
            <input
              type="text"
              name="jobTitle"
              id="jobTitle"
              className="mt-1 block w-full rounded-md border-input shadow-sm focus:border-primary focus:ring-ring sm:text-sm"
              placeholder="e.g., Nanny, Housekeeper"
            />
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-foreground">
              Location
            </label>
            <input
              type="text"
              name="location"
              id="location"
              className="mt-1 block w-full rounded-md border-input shadow-sm focus:border-primary focus:ring-ring sm:text-sm"
              placeholder="e.g., Addis Ababa"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-foreground">
              Job Description
            </label>
            <textarea
              id="description"
              name="description"
              rows={4}
              className="mt-1 block w-full rounded-md border-input shadow-sm focus:border-primary focus:ring-ring sm:text-sm"
              placeholder="Describe the responsibilities and requirements for this role."
            />
          </div>

           <div>
            <label htmlFor="salary" className="block text-sm font-medium text-foreground">
              Salary (Optional)
            </label>
            <input
              type="text"
              name="salary"
              id="salary"
              className="mt-1 block w-full rounded-md border-input shadow-sm focus:border-primary focus:ring-ring sm:text-sm"
              placeholder="e.g., 5000 ETB/month"
            />
          </div>

        </div>
        <div className="mt-6 flex flex-col sm:flex-row justify-end">
          <Button type="button" variant="secondary" className="mb-2 sm:mb-0 sm:mr-2">
            Cancel
          </Button>
          <Button type="submit">
            Post Job
          </Button>
        </div>
      </form>
    </div>
  );
}
