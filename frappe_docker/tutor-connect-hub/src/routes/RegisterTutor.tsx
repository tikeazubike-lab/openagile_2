import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { frappeApi } from "@/lib/frappe-api";
import { SUBJECTS } from "@/lib/constants";
import { BookOpen } from "lucide-react";

export function RegisterTutor() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
    subjects: [] as string[],
    hourly_rate: "",
    experience_years: "",
    qualifications: "",
    bio: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const toggleSubject = (subject: string) => {
    setForm((prev) => ({
      ...prev,
      subjects: prev.subjects.includes(subject)
        ? prev.subjects.filter((s) => s !== subject)
        : [...prev.subjects, subject],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.subjects.length === 0) {
      setError("Please select at least one subject");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await frappeApi.call("tutor_hub.tutor_hub.api.register_tutor", {
        full_name: form.full_name,
        email: form.email,
        phone: form.phone,
        password: form.password,
        subjects: form.subjects.join(", "),
        hourly_rate: parseFloat(form.hourly_rate),
        experience_years: parseInt(form.experience_years) || 0,
        qualifications: form.qualifications,
        bio: form.bio,
      });
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <Card className="w-full max-w-lg">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary-100">
              <BookOpen className="h-6 w-6 text-primary-600" />
            </div>
            <CardTitle className="text-2xl">Apply as Tutor</CardTitle>
            <CardDescription>Share your expertise and help students succeed</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input id="full_name" name="full_name" value={form.full_name} onChange={handleChange} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" name="phone" type="tel" value={form.phone} onChange={handleChange} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" name="password" type="password" value={form.password} onChange={handleChange} required minLength={6} />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Subjects</Label>
                <div className="flex flex-wrap gap-2">
                  {SUBJECTS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => toggleSubject(s)}
                      className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
                        form.subjects.includes(s)
                          ? "bg-primary-500 text-white border-primary-500"
                          : "bg-white text-muted-foreground border-border hover:border-primary-300"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hourly_rate">Hourly Rate (NGN)</Label>
                  <Input id="hourly_rate" name="hourly_rate" type="number" min="0" value={form.hourly_rate} onChange={handleChange} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="experience_years">Years of Experience</Label>
                  <Input id="experience_years" name="experience_years" type="number" min="0" value={form.experience_years} onChange={handleChange} required />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="qualifications">Qualifications</Label>
                <Input id="qualifications" name="qualifications" placeholder="e.g., B.Sc Mathematics, M.Ed" value={form.qualifications} onChange={handleChange} required />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <textarea
                  id="bio"
                  name="bio"
                  className="flex min-h-[80px] w-full rounded-lg border border-border bg-white px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                  placeholder="Tell students about your teaching style and experience..."
                  value={form.bio}
                  onChange={handleChange}
                  required
                />
              </div>

              {error && (
                <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full" loading={loading}>
                Submit Application
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link to="/login" className="font-medium text-primary-600 hover:underline">
                  Log in
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
