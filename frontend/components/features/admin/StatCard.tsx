//-
//- Stat Card Component
//-
interface StatCardProps {
  title: string;
  value: string | number;
}

export default function StatCard({ title, value }: StatCardProps) {
  return (
    <div className="bg-card rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-card-foreground">{title}</h2>
      <p className="text-3xl font-bold text-foreground mt-2">{value}</p>
    </div>
  );
}
