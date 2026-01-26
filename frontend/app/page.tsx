import { Button } from "@/components/ui/Button";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-primary p-24">
      <h1 className="text-6xl font-bold text-primary-foreground font-noto">
        ሰላም! Welcome to SurveAddis
      </h1>
      <p className="text-2xl text-primary-foreground mt-4">
        The platform connecting domestic workers with employers in Ethiopia.
      </p>
      <div className="mt-8 flex gap-4">
        <Link href="/login">
          <Button>Login</Button>
        </Link>
        <Link href="/register">
          <Button icon={<ArrowRight className="h-4 w-4" />}>Register</Button>
        </Link>
      </div>
    </main>
  );
}
