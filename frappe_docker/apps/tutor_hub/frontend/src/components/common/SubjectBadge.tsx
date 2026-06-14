interface SubjectBadgeProps {
  name: string;
}

export default function SubjectBadge({ name }: SubjectBadgeProps) {
  return (
    <span className="inline-flex items-center rounded-full border bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
      {name}
    </span>
  );
}
