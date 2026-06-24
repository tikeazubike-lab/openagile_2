import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import {
  Users,
  Plus,
  Pencil,
  Trash2,
  Key,
  UserCheck,
  UserX,
  X,
} from "lucide-react";
import {
  useAdminUsers,
  useAdminCreateUser,
  useAdminUpdateUser,
  useAdminResetPassword,
  useAdminDeleteUser,
  type AdminUser,
} from "@/api/queries";
import { useAuthStore } from "@/store/authStore";

export const Route = createFileRoute("/_app/settings/users")({
  component: UsersPage,
});

function UsersPage() {
  const navigate = useNavigate();
  const isAdmin = useAuthStore((s) => s.isAdmin)();

  if (!isAdmin) {
    navigate({ to: "/dashboard" });
    return null;
  }

  const [includeInactive, setIncludeInactive] = useState(false);
  const { data: users, isLoading, isError, error } = useAdminUsers(includeInactive);

  const [showCreate, setShowCreate] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [resetUser, setResetUser] = useState<AdminUser | null>(null);
  const [deleteUser, setDeleteUser] = useState<AdminUser | null>(null);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-[var(--text-primary)]" />
          <h1 className="text-2xl font-semibold text-[var(--text-primary)]">
            User Management
          </h1>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--action-primary)] text-white hover:bg-[var(--action-primary-hover)] transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add User
        </button>
      </div>

      {/* Filters */}
      <div className="mb-4">
        <label className="inline-flex items-center gap-2 text-sm text-[var(--text-secondary)] cursor-pointer">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="rounded border-[var(--border-default)]"
          />
          Show inactive users
        </label>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-[var(--border-default)] bg-[var(--bg-surface)] overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border-default)] bg-[var(--bg-surface-alt)]">
              <th className="text-left px-4 py-3 font-medium text-[var(--text-secondary)]">
                Username
              </th>
              <th className="text-left px-4 py-3 font-medium text-[var(--text-secondary)]">
                Name
              </th>
              <th className="text-left px-4 py-3 font-medium text-[var(--text-secondary)]">
                Role
              </th>
              <th className="text-left px-4 py-3 font-medium text-[var(--text-secondary)]">
                Status
              </th>
              <th className="text-right px-4 py-3 font-medium text-[var(--text-secondary)]">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-[var(--text-muted)]">
                  Loading users...
                </td>
              </tr>
            )}
            {isError && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-red-500">
                  {error instanceof Error ? error.message : "Failed to load users"}
                </td>
              </tr>
            )}
            {!isLoading && !isError && users && users.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-[var(--text-muted)]">
                  No users found.
                </td>
              </tr>
            )}
            {users?.map((user) => (
              <tr
                key={user.id}
                className="border-b border-[var(--border-default)] last:border-b-0 hover:bg-[var(--bg-surface-hover)] transition-colors"
              >
                <td className="px-4 py-3 font-mono text-[var(--text-primary)]">
                  {user.username}
                </td>
                <td className="px-4 py-3 text-[var(--text-primary)]">
                  {user.name}
                </td>
                <td className="px-4 py-3">
                  <RoleBadge role={user.role} />
                </td>
                <td className="px-4 py-3">
                  <StatusBadge active={user.is_active} />
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="inline-flex items-center gap-1">
                    <button
                      onClick={() => setEditingUser(user)}
                      className="p-1.5 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                      title="Edit user"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setResetUser(user)}
                      className="p-1.5 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                      title="Reset password"
                    >
                      <Key className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeleteUser(user)}
                      className="p-1.5 rounded hover:bg-red-500/10 text-[var(--text-secondary)] hover:text-red-500 transition-colors"
                      title="Delete user"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create / Edit Modal */}
      {(showCreate || editingUser) && (
        <UserModal
          user={editingUser}
          onClose={() => {
            setShowCreate(false);
            setEditingUser(null);
          }}
        />
      )}

      {/* Reset Password Modal */}
      {resetUser && (
        <ResetPasswordModal
          user={resetUser}
          onClose={() => setResetUser(null)}
        />
      )}

      {/* Delete Confirmation */}
      {deleteUser && (
        <DeleteConfirmDialog
          user={deleteUser}
          onClose={() => setDeleteUser(null)}
        />
      )}
    </div>
  );
}

/* ─── Role Badge ──────────────────────────────────────────────────────────── */

function RoleBadge({ role }: { role: "admin" | "readonly" }) {
  if (role === "admin") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-purple-500/15 text-purple-400">
        <UserCheck className="w-3 h-3" />
        admin
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-500/15 text-slate-400">
      <UserX className="w-3 h-3" />
      readonly
    </span>
  );
}

/* ─── Status Badge ────────────────────────────────────────────────────────── */

function StatusBadge({ active }: { active: boolean }) {
  return active ? (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-500">
      <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
      Active
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-500">
      <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
      Inactive
    </span>
  );
}

/* ─── Modal Overlay ────────────────────────────────────────────────────────── */

function ModalOverlay({
  onClose,
  children,
}: {
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}

/* ─── User Modal (Create / Edit) ──────────────────────────────────────────── */

function UserModal({
  user,
  onClose,
}: {
  user: AdminUser | null;
  onClose: () => void;
}) {
  const createUser = useAdminCreateUser();
  const updateUser = useAdminUpdateUser();

  const [username, setUsername] = useState(user?.username ?? "");
  const [name, setName] = useState(user?.name ?? "");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"admin" | "readonly">(user?.role ?? "readonly");
  const [error, setError] = useState<string | null>(null);

  const isEditing = user !== null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (isEditing) {
        await updateUser.mutateAsync({
          id: user.id,
          payload: { name, role, is_active: user.is_active },
        });
      } else {
        if (!username || !password) {
          setError("Username and password are required.");
          return;
        }
        await createUser.mutateAsync({ username, name, password, role });
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred.");
    }
  };

  return (
    <ModalOverlay onClose={onClose}>
      <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-default)]">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          {isEditing ? "Edit User" : "Create User"}
        </h2>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-secondary)]"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isEditing}
            className="w-full px-3 py-2 rounded-lg border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--action-primary)] disabled:opacity-50 font-mono"
            placeholder="e.g. jsmith"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--action-primary)]"
            placeholder="Full name"
          />
        </div>

        {!isEditing && (
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
              Password
            </label>
            <input
              type="text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--action-primary)]"
              placeholder="Set initial password"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
            Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as "admin" | "readonly")}
            className="w-full px-3 py-2 rounded-lg border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--action-primary)]"
          >
            <option value="admin">Admin</option>
            <option value="readonly">Read-only</option>
          </select>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createUser.isPending || updateUser.isPending}
            className="px-4 py-2 rounded-lg bg-[var(--action-primary)] text-white hover:bg-[var(--action-primary-hover)] transition-colors disabled:opacity-50"
          >
            {createUser.isPending || updateUser.isPending
              ? "Saving..."
              : isEditing
                ? "Save Changes"
                : "Create User"}
          </button>
        </div>
      </form>
    </ModalOverlay>
  );
}

/* ─── Reset Password Modal ─────────────────────────────────────────────────── */

function ResetPasswordModal({
  user,
  onClose,
}: {
  user: AdminUser;
  onClose: () => void;
}) {
  const resetPassword = useAdminResetPassword();
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!newPassword) {
      setError("New password is required.");
      return;
    }

    try {
      await resetPassword.mutateAsync({ id: user.id, newPassword });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred.");
    }
  };

  return (
    <ModalOverlay onClose={onClose}>
      <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-default)]">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          Reset Password
        </h2>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-secondary)]"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        <p className="text-sm text-[var(--text-secondary)]">
          Resetting password for{" "}
          <span className="font-mono text-[var(--text-primary)]">
            {user.username}
          </span>
        </p>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
            New Password
          </label>
          <input
            type="text"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--action-primary)]"
            placeholder="Enter new password"
            autoFocus
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={resetPassword.isPending}
            className="px-4 py-2 rounded-lg bg-[var(--action-primary)] text-white hover:bg-[var(--action-primary-hover)] transition-colors disabled:opacity-50"
          >
            {resetPassword.isPending ? "Resetting..." : "Reset Password"}
          </button>
        </div>
      </form>
    </ModalOverlay>
  );
}

/* ─── Delete Confirmation Dialog ───────────────────────────────────────────── */

function DeleteConfirmDialog({
  user,
  onClose,
}: {
  user: AdminUser;
  onClose: () => void;
}) {
  const deleteUserMutation = useAdminDeleteUser();
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setError(null);
    try {
      await deleteUserMutation.mutateAsync(user.id);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete user.");
    }
  };

  return (
    <ModalOverlay onClose={onClose}>
      <div className="px-6 py-4 border-b border-[var(--border-default)]">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-full bg-red-500/10">
            <Trash2 className="w-5 h-5 text-red-500" />
          </div>
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            Delete User
          </h2>
        </div>
      </div>

      <div className="p-6 space-y-4">
        <p className="text-sm text-[var(--text-secondary)]">
          Delete user{" "}
          <span className="font-mono font-medium text-[var(--text-primary)]">
            {user.username}
          </span>
          ? This cannot be undone.
        </p>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteUserMutation.isPending}
            className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            {deleteUserMutation.isPending ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </ModalOverlay>
  );
}
