# DISPATCH: F-017 — Remove editMode Toggle

## Objective
Remove the `editMode` toggle from `uiStore` and replace all references with role-based checks (`isAdmin()`). After this change:
- **Admin users** always see inline editing controls (no toggle needed)
- **Read-only users** never see inline editing controls (immutable view always)

## Current Architecture

The editMode pattern works like this:
1. `uiStore.ts` defines `editMode: boolean` and `toggleEditMode()`
2. `Navbar.tsx` renders a toggle button (pencil icon) when `isAdmin() && !isDashboard`
3. Components check `editMode` to conditionally show/allow inline editing

The existing `isAdmin()` check already gates the toggle button, so turning the toggle on by default for admins is a straightforward replacement.

## Files to Change

| File | Edit Required |
|------|---------------|
| **`store/uiStore.ts`** | Remove `editMode: boolean`, `toggleEditMode: () => void` from both the interface and the store implementation |
| **`components/layout/Navbar.tsx`** | Remove the edit toggle button (lines 77-107, the `<button>` with `onClick={toggleEditMode}`). Remove `editMode, toggleEditMode` from the `useUIStore` destructure on line 34 |
| **`routes/_app.holdings.tsx`** | Line 40: remove `const editMode = useUIStore((s) => s.editMode);`. Line 57-63: replace the `useEffect` dependency on `editMode` — instead always clear `editingRowId`/`addDrawerOpen` when the component mounts or user changes. Lines 170, 225: replace `editMode` checks with the existing `isAdmin` variable (already defined on line 39) |
| **`components/registrars/RegistrarList.tsx`** | Replace `editMode` references with `useAuthStore((s) => s.isAdmin)()` |
| **`components/registrars/RegistrarDetails.tsx`** | Same — replace `editMode` with `isAdmin()` |
| **`components/registrars/RegistrarRequirements.tsx`** | Same — replace `editMode` with `isAdmin()` |

**Note:** `InlineEditRow.tsx` does NOT reference `editMode` itself — it's purely a rendering component whose visibility is controlled by its parent. No change needed.

## Desired Behaviour

- Admin user visits Holdings page → sees inline edit pencil icon on each row, can click to edit
- Admin user visits Registrar pages → sees edit/delete controls on each item
- Read-only user visits Holdings page → table is read-only (no edit controls)
- Navbar: no "Viewing/Editing" toggle button anywhere (removed entirely)

## Acceptance Criteria

After this change, run these commands from the project root:

```bash
grep -rn "editMode" estate-portfolio-manager/src/ --include="*.tsx" --include="*.ts"
grep -rn "toggleEditMode" estate-portfolio-manager/src/ --include="*.tsx" --include="*.ts"
```

Both must return **zero output**. Expected output is empty (no matches).

## Build & Verify

```bash
cd estate-portfolio-manager
npm run build
```

Must succeed with no TypeScript errors. The `editMode` type/interface will be gone from `UIStore`, so any remaining references to it will cause a TypeScript error — fix them all.

## Risk Notes

- `InlineEditRow.tsx` is controlled by its parent via `editingRowId` state, not `editMode` — no change needed there
- The `useEffect` cleanup in `_app.holdings.tsx` (lines 57-63) that resets editing state when `editMode` toggles off is no longer needed since admins are always in edit mode. Replace the effect with a simpler cleanup on unmount or remove it entirely
- The `Pencil` icon import in `Navbar.tsx` can be removed if no other usage exists in that file
