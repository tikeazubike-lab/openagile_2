// EPM Phase 2 — Shared TypeScript interfaces.
// Extracted from mock.ts (Claude note #4: do this before building any stub pages).
// These interfaces mirror the /api/v1/* JSON response shapes.
// When real API is live, these types are the contract between frontend and FastAPI.

// ─── Domain Types ──────────────────────────────────────────────────────────────

export type Sector =
  | "Banking"
  | "Consumer Goods"
  | "Oil & Gas"
  | "Industrials"
  | "Healthcare"
  | "Telecoms"
  | "Conglomerate"
  | "Insurance";

export type TransactionType = "BUY" | "SELL" | "BONUS" | "RIGHTS";

export type HoldingStatus = "LIVE" | "DRAFT";

export type TransactionStatus = "LIVE" | "DRAFT";

export type ActionSeverity = "amber" | "red";

// ─── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  username: string;
  name: string;
  role: "admin" | "readonly";
}

// ─── API Envelope ──────────────────────────────────────────────────────────────
// All /api/v1/* endpoints return this shape.

export interface ApiResponse<T> {
  data: T;
  meta: Record<string, unknown>;
  error: string | null;
}

// ─── Dashboard ─────────────────────────────────────────────────────────────────

export interface SectorAllocation {
  sector: Sector;
  value: number;
  pct: number;
}

export interface TopHolding {
  ticker: string;
  company: string;
  value: number;
  return_pct: number;
}

export interface RecentTransaction {
  date: string;
  ticker: string;
  type: TransactionType;
  shares: number;
  amount: number;
}

export interface ActionItem {
  id: string;
  label: string;
  count: number;
  severity: ActionSeverity;
  href: string;
}

export interface DashboardData {
  total_portfolio_value: number;
  total_invested: number;
  unrealised_gain_loss: number;
  unrealised_gain_pct: number;
  total_holdings: number;
  live_holdings: number;
  draft_holdings: number;
  sector_allocation: SectorAllocation[];
  top_holdings: TopHolding[];
  recent_transactions: RecentTransaction[];
  action_items: ActionItem[];
  last_updated: string;
}

// ─── Holdings ──────────────────────────────────────────────────────────────────

export interface Holding {
  id: number;
  ticker: string;
  company: string;
  sector: Sector;
  shares: number;
  avg_cost: number;
  curr_price: number;
  curr_value: number;
  cost_basis: number;
  return_pct: number;
  div_yield: number;
  status: HoldingStatus;
}

// ─── Companies ─────────────────────────────────────────────────────────────────

export interface Company {
  id: number;
  name: string;
  ticker: string;
  sector: Sector;
  isin?: string;
  status: "listed" | "merged" | "defunct" | "delisted";
  current_price: string | null;
  last_price_update?: string | null;
  registrar_id?: number;
  registrar_name?: string;
  deleted_at?: string | null;
}

export interface CompanyDetail extends Company {
  market_cap: string | null;
  outstanding_shares: number | null;
  date_listed: string | null;
  registrar: { id: number; name: string } | null;
}

// ─── Transactions ──────────────────────────────────────────────────────────────

export interface Transaction {
  id: number;
  date: string;
  ticker: string;
  company: string;
  type: TransactionType;
  shares: number;
  price_per_share: number;
  net_amount: number;
  broker_fee: number;
  reference_id?: string;
  linked_holding_id?: number;
  is_auto_generated: boolean;
  notes?: string;
  status: TransactionStatus;
  deleted_at?: string | null;
}

// ─── Dividends ─────────────────────────────────────────────────────────────────

export interface Dividend {
  id: number;
  company_id: number;
  ticker: string;
  company_name: string;
  declaration_date?: string;
  ex_dividend_date?: string;
  payment_date?: string;
  amount_per_share: number;
  shares_held?: number;
  gross_amount?: number;
  net_amount?: number;
  payment_method?: string;
  is_scrip: boolean;
  status: "declared" | "pending" | "paid" | "cancelled";
  notes?: string;
  deleted_at?: string | null;
}

// ─── Registrars ────────────────────────────────────────────────────────────────

export interface Registrar {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  website?: string;
  response_rating?: number;
  status: "active" | "inactive";
  company_count: number;
  notes?: string;
  deleted_at?: string | null;
}

// ─── Watchlist ─────────────────────────────────────────────────────────────────

export interface WatchlistItem {
  id: number;
  ticker: string;
  company: string;
  sector: Sector;
  current_price?: number;
  target_price?: number;
  gap_to_target_pct?: number;
  notes?: string;
  deleted_at?: string | null;
}

// ─── NAV History ───────────────────────────────────────────────────────────────

export interface NavSnapshot {
  id: number;
  snapshot_date: string;
  portfolio_value: number;
  total_invested: number;
  gain_loss: number;
  return_pct: number;
}

// ─── Rebalancing ───────────────────────────────────────────────────────────────

export interface SectorTarget {
  sector: Sector;
  target_pct: number;
}

export interface RebalancingRow {
  sector: Sector;
  current_value: number;
  current_pct: number;
  target_pct: number;
  gap_pct: number;
  recommendation: "Reduce" | "Increase" | "Hold";
}

// ─── Price Audit ───────────────────────────────────────────────────────────────

export type PriceSource = "manual" | "csv_upload" | "stooq_csv";

export interface PriceAuditEntry {
  id: number;
  ticker: string;
  old_price: number;
  new_price: number;
  change_pct: number;
  source: PriceSource;
  changed_at: string;
  changed_by: string;
}

// ─── Corporate Actions ─────────────────────────────────────────────────────────

export type CorporateActionType = "BONUS" | "RIGHTS" | "SPLIT" | "MERGER" | "DIVIDEND";

export interface CorporateAction {
  id: number;
  ticker: string;
  company: string;
  action_type: CorporateActionType;
  action_date: string;
  ratio?: string;
  notes?: string;
  auto_transaction_id?: number;
  deleted_at?: string | null;
}
