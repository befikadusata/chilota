import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";

export default function PasswordResetPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background">
      <Card>
        <CardHeader>Reset Password</CardHeader>
        <CardContent>
          <form>
            <div className="mb-4">
              <Label htmlFor="email">Email</Label>
              <Input type="email" id="email" />
            </div>
            <Button type="submit" className="w-full">
              Send Password Reset Email
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
