import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings as SettingsIcon } from "lucide-react";

export function OwnerSettings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Platform Settings</h1>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SettingsIcon className="h-5 w-5" />
              General Settings
            </CardTitle>
            <CardDescription>Configure platform-wide settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Platform Name</Label>
              <Input defaultValue="TutorConnect Hub" />
            </div>
            <div className="space-y-2">
              <Label>Support Email</Label>
              <Input defaultValue="support@tutorconnect.com" />
            </div>
            <div className="space-y-2">
              <Label>Platform Fee (%)</Label>
              <Input type="number" defaultValue="15" min="0" max="50" />
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Notification Settings</CardTitle>
            <CardDescription>Configure email notifications</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              "New tutor registration",
              "Session booked",
              "Session completed",
              "Payment processed",
              "Dispute raised",
            ].map((item) => (
              <label key={item} className="flex items-center justify-between">
                <span className="text-sm">{item}</span>
                <input type="checkbox" defaultChecked className="h-4 w-4 rounded border-border text-primary-500 focus:ring-primary-500" />
              </label>
            ))}
            <Button>Save Preferences</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
