import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Calendar, Plus, Trash2 } from "lucide-react";

interface Slot {
  id: string;
  day: string;
  startTime: string;
  endTime: string;
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const TIMES = [
  "08:00", "09:00", "10:00", "11:00", "12:00",
  "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
];

export function TutorSchedule() {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [day, setDay] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  const addSlot = () => {
    if (!day || !startTime || !endTime) return;
    setSlots((prev) => [
      ...prev,
      { id: crypto.randomUUID(), day, startTime, endTime },
    ]);
    setDay("");
    setStartTime("");
    setEndTime("");
  };

  const removeSlot = (id: string) => {
    setSlots((prev) => prev.filter((s) => s.id !== id));
  };

  const groupedByDay = DAYS.map((d) => ({
    day: d,
    slots: slots.filter((s) => s.day === d),
  })).filter((g) => g.slots.length > 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Availability Schedule</h1>

      <Card>
        <CardHeader>
          <CardTitle>Add Time Slot</CardTitle>
          <CardDescription>Set your weekly availability for students to book sessions.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Day</Label>
              <Select value={day} onValueChange={setDay}>
                <SelectTrigger>
                  <SelectValue placeholder="Select day" />
                </SelectTrigger>
                <SelectContent>
                  {DAYS.map((d) => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Start Time</Label>
              <Select value={startTime} onValueChange={setStartTime}>
                <SelectTrigger>
                  <SelectValue placeholder="From" />
                </SelectTrigger>
                <SelectContent>
                  {TIMES.slice(0, -1).map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>End Time</Label>
              <Select value={endTime} onValueChange={setEndTime}>
                <SelectTrigger>
                  <SelectValue placeholder="To" />
                </SelectTrigger>
                <SelectContent>
                  {TIMES.filter((t) => !startTime || t > startTime).map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={addSlot} disabled={!day || !startTime || !endTime} className="w-full">
                <Plus className="mr-1.5 h-4 w-4" />
                Add Slot
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {groupedByDay.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Your Schedule
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {groupedByDay.map((group) => (
              <div key={group.day}>
                <h3 className="text-sm font-semibold text-foreground mb-2">{group.day}</h3>
                <div className="flex flex-wrap gap-2">
                  {group.slots.map((slot) => (
                    <div
                      key={slot.id}
                      className="flex items-center gap-2 rounded-lg border border-border bg-gray-50 px-3 py-1.5 text-sm"
                    >
                      <span>{slot.startTime} - {slot.endTime}</span>
                      <button
                        onClick={() => removeSlot(slot.id)}
                        className="text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <Button className="mt-4">Save Schedule</Button>
          </CardContent>
        </Card>
      )}

      {groupedByDay.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <Calendar className="mx-auto h-10 w-10 mb-3 opacity-40" />
            <p>No availability set yet. Add time slots above to get started.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
