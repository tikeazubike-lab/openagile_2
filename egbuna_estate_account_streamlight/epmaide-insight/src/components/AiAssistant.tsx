import { useEffect, useRef, useState } from "react";
import { Sparkles, ArrowUp, X } from "lucide-react";
import { cn } from "@/lib/utils";

type Stage = "launcher" | "input" | "panel";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  chart?: ChartData;
};

type ChartData =
  | { kind: "bars"; title: string; items: { label: string; value: number; color?: string }[] }
  | { kind: "spark"; title: string; points: number[] };

const SUGGESTIONS = [
  "What's my biggest holding?",
  "Show my sector allocation",
  "Any dividends due this month?",
];

// Read-only canned responses
function answer(q: string): Message {
  const id = crypto.randomUUID();
  const lower = q.toLowerCase();
  if (lower.includes("biggest") || lower.includes("top")) {
    return {
      id,
      role: "assistant",
      text: "Your largest position is NESTLE at ₦29.4M (≈59% of portfolio value), followed by VITAFOAM and UACN.",
      chart: {
        kind: "bars",
        title: "Top holdings (₦M)",
        items: [
          { label: "NESTLE", value: 29.4 },
          { label: "VITAFOAM", value: 8.1 },
          { label: "UACN", value: 4.3 },
          { label: "OKOMUOIL", value: 3.2 },
        ],
      },
    };
  }
  if (lower.includes("sector") || lower.includes("allocation")) {
    return {
      id,
      role: "assistant",
      text: "Consumer Goods dominates at 78.6%. Conglomerate (7.5%) and Industrials (7.3%) round out the next tier; everything else is under 6%.",
      chart: {
        kind: "bars",
        title: "Sector allocation",
        items: [
          { label: "Consumer Goods", value: 78.6 },
          { label: "Conglomerate", value: 7.5 },
          { label: "Industrials", value: 7.3 },
          { label: "Agriculture", value: 5.4 },
          { label: "Other", value: 1.2 },
        ],
      },
    };
  }
  if (lower.includes("dividend")) {
    return {
      id,
      role: "assistant",
      text: "No dividends are scheduled in the next 30 days. The most recent declared payout was from NESTLE on 2025-11-18.",
    };
  }
  if (lower.includes("gain") || lower.includes("loss") || lower.includes("performance")) {
    return {
      id,
      role: "assistant",
      text: "Unrealised gain stands at +₦49.48M against a ₦0 cost basis (legacy holdings). Recent 7-day NAV trend below.",
      chart: { kind: "spark", title: "NAV — 7d", points: [44.1, 45.2, 46.0, 47.1, 47.9, 48.6, 49.48] },
    };
  }
  return {
    id,
    role: "assistant",
    text: "I can answer questions about your holdings, sector allocation, dividends, and recent transactions. Try one of the suggestions, or ask about a specific ticker.",
  };
}

export function AiAssistant() {
  const [stage, setStage] = useState<Stage>("launcher");
  const [value, setValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (stage === "input" || stage === "panel") inputRef.current?.focus();
  }, [stage]);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const submit = (text?: string) => {
    const q = (text ?? value).trim();
    if (!q) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text: q };
    const reply = answer(q);
    setMessages((m) => [...m, userMsg, reply]);
    setValue("");
    setStage("panel");
  };

  const close = () => {
    setStage("launcher");
  };

  return (
    <div className="fixed bottom-6 left-6 z-50">
      {/* Stage 1 — Launcher */}
      {stage === "launcher" && (
        <button
          onClick={() => setStage("input")}
          aria-label="Open assistant"
          className="group relative grid h-12 w-12 place-items-center rounded-full bg-primary text-primary-foreground shadow-[0_0_0_1px_oklch(0.78_0.10_295/0.5),0_8px_28px_-6px_oklch(0.78_0.10_295/0.6)] transition-all hover:scale-105 hover:shadow-[0_0_0_1px_oklch(0.78_0.10_295/0.7),0_12px_36px_-6px_oklch(0.78_0.10_295/0.8)]"
        >
          <span className="absolute inset-0 rounded-full bg-primary/40 blur-md -z-10 animate-pulse" />
          <Sparkles className="h-5 w-5" strokeWidth={2.2} />
        </button>
      )}

      {/* Stage 2 — Input only */}
      {stage === "input" && (
        <div className="animate-in slide-in-from-left-2 fade-in duration-200">
          <InputBar
            value={value}
            onChange={setValue}
            onSubmit={() => submit()}
            onClose={close}
            inputRef={inputRef}
            width={340}
          />
        </div>
      )}

      {/* Stage 3 — Full panel */}
      {stage === "panel" && (
        <div
          className="flex flex-col w-[380px] max-h-[70vh] rounded-2xl border border-border bg-card/95 backdrop-blur-md shadow-[0_20px_60px_-12px_rgba(0,0,0,0.6)] animate-in slide-in-from-bottom-2 fade-in duration-200"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <div className="flex items-center gap-2">
              <div className="grid h-6 w-6 place-items-center rounded-md bg-primary/15 text-primary">
                <Sparkles className="h-3.5 w-3.5" />
              </div>
              <span className="text-sm font-medium text-foreground">Assistant</span>
            </div>
            <button
              onClick={close}
              aria-label="Close assistant"
              className="grid h-7 w-7 place-items-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
          </div>

          {/* Suggestions (only before first message) */}
          {messages.length === 0 && (
            <div className="px-4 pb-2 flex flex-wrap gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => submit(s)}
                  className="text-xs px-2.5 py-1.5 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-primary/40 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Pinned input */}
          <div className="p-3 border-t border-border">
            <InputBar
              value={value}
              onChange={setValue}
              onSubmit={() => submit()}
              inputRef={inputRef}
              embedded
            />
          </div>
        </div>
      )}
    </div>
  );
}

function InputBar({
  value,
  onChange,
  onSubmit,
  onClose,
  inputRef,
  width,
  embedded,
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  onClose?: () => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
  width?: number;
  embedded?: boolean;
}) {
  return (
    <div
      style={width ? { width } : undefined}
      className={cn(
        "flex items-center gap-2 rounded-full bg-background/60 border border-primary/25 pl-4 pr-1.5 py-1.5",
        !embedded && "shadow-[0_0_0_1px_oklch(0.78_0.10_295/0.15),0_8px_24px_-8px_rgba(0,0,0,0.5)]"
      )}
    >
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") onSubmit();
          if (e.key === "Escape" && onClose) onClose();
        }}
        placeholder="Ask EPM a question..."
        className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground/70 outline-none py-1.5"
      />
      <button
        onClick={onSubmit}
        disabled={!value.trim()}
        aria-label="Send"
        className="grid h-8 w-8 place-items-center rounded-full bg-primary text-primary-foreground disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
      >
        <ArrowUp className="h-4 w-4" strokeWidth={2.5} />
      </button>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-primary/15 text-foreground px-3 py-2 text-sm border border-primary/20">
          {message.text}
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] space-y-2">
        <div className="text-sm text-foreground leading-relaxed">{message.text}</div>
        {message.chart && <InlineChart data={message.chart} />}
      </div>
    </div>
  );
}

function InlineChart({ data }: { data: ChartData }) {
  if (data.kind === "bars") {
    const max = Math.max(...data.items.map((i) => i.value));
    return (
      <div className="rounded-lg border border-border bg-background/40 p-3 space-y-1.5">
        <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{data.title}</div>
        {data.items.map((it) => (
          <div key={it.label} className="flex items-center gap-2 text-xs">
            <span className="w-24 truncate text-muted-foreground">{it.label}</span>
            <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary rounded-full"
                style={{ width: `${(it.value / max) * 100}%` }}
              />
            </div>
            <span className="tabular text-foreground w-10 text-right">{it.value}</span>
          </div>
        ))}
      </div>
    );
  }
  // sparkline
  const { points, title } = data;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const w = 280;
  const h = 50;
  const step = w / (points.length - 1);
  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${i * step} ${h - ((p - min) / range) * h}`)
    .join(" ");
  return (
    <div className="rounded-lg border border-border bg-background/40 p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">{title}</div>
      <svg width={w} height={h} className="overflow-visible">
        <path d={`${path} L ${w} ${h} L 0 ${h} Z`} fill="oklch(0.78 0.10 295 / 0.15)" />
        <path d={path} fill="none" stroke="oklch(0.78 0.10 295)" strokeWidth={1.5} />
      </svg>
    </div>
  );
}
