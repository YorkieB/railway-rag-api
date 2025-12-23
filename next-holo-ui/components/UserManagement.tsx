import { useState, useEffect } from "react";
import { User, listUsers, createUser, updateUser, deleteUser, resetUserPassword, setUserAdmin, apiBaseFromEnv } from "@/lib/api";

type Props = {
  apiBase: string;
  token: string;
};

export function UserManagement({ apiBase, token }: Props) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showResetPassword, setShowResetPassword] = useState<string | null>(null);

  // Form state
  const [formEmail, setFormEmail] = useState("");
  const [formPassword, setFormPassword] = useState("");
  const [formUsername, setFormUsername] = useState("");
  const [formIsAdmin, setFormIsAdmin] = useState(false);
  const [resetPasswordValue, setResetPasswordValue] = useState("");

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listUsers(apiBase, token);
      setUsers(data.users);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await createUser(apiBase, token, {
        email: formEmail,
        password: formPassword,
        username: formUsername || undefined,
        is_admin: formIsAdmin,
      });
      await loadUsers();
      setShowCreateForm(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || "Failed to create user");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    setError(null);
    setLoading(true);

    try {
      await updateUser(apiBase, token, editingUser.user_id, {
        email: formEmail,
        username: formUsername || undefined,
      });
      await loadUsers();
      setEditingUser(null);
      resetForm();
    } catch (err: any) {
      setError(err.message || "Failed to update user");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm("Are you sure you want to delete this user?")) {
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await deleteUser(apiBase, token, userId);
      await loadUsers();
    } catch (err: any) {
      setError(err.message || "Failed to delete user");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (userId: string) => {
    if (!resetPasswordValue || resetPasswordValue.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await resetUserPassword(apiBase, token, userId, resetPasswordValue);
      setShowResetPassword(null);
      setResetPasswordValue("");
      alert("Password reset successfully");
    } catch (err: any) {
      setError(err.message || "Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAdmin = async (userId: string, currentAdminStatus: boolean) => {
    setError(null);
    setLoading(true);

    try {
      await setUserAdmin(apiBase, token, userId, !currentAdminStatus);
      await loadUsers();
    } catch (err: any) {
      setError(err.message || "Failed to update admin status");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormEmail("");
    setFormPassword("");
    setFormUsername("");
    setFormIsAdmin(false);
  };

  const startEdit = (user: User) => {
    setEditingUser(user);
    setFormEmail(user.email);
    setFormUsername(user.username);
    setFormIsAdmin(user.is_admin);
    setShowCreateForm(false);
    setShowResetPassword(null);
  };

  const cancelEdit = () => {
    setEditingUser(null);
    setShowCreateForm(false);
    setShowResetPassword(null);
    resetForm();
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">User Management</h3>
        <button
          onClick={() => {
            setShowCreateForm(true);
            setEditingUser(null);
            resetForm();
          }}
          className="btn-primary px-4 py-2 text-sm"
          disabled={loading || showCreateForm || editingUser !== null}
        >
          Create User
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Create/Edit Form */}
      {(showCreateForm || editingUser) && (
        <div className="card p-4 space-y-4">
          <h4 className="font-semibold text-gray-900">
            {editingUser ? "Edit User" : "Create New User"}
          </h4>
          <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={formEmail}
                onChange={(e) => setFormEmail(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:border-primary"
              />
            </div>
            {!editingUser && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password"
                  value={formPassword}
                  onChange={(e) => setFormPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:border-primary"
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username (optional)</label>
              <input
                type="text"
                value={formUsername}
                onChange={(e) => setFormUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:border-primary"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="isAdmin"
                checked={formIsAdmin}
                onChange={(e) => setFormIsAdmin(e.target.checked)}
                className="mr-2 accent-primary"
              />
              <label htmlFor="isAdmin" className="text-sm text-gray-700">Admin</label>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary px-4 py-2 text-sm disabled:opacity-60"
              >
                {loading ? "Saving..." : editingUser ? "Update" : "Create"}
              </button>
              <button
                type="button"
                onClick={cancelEdit}
                className="btn-secondary px-4 py-2 text-sm"
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Users List */}
      <div className="card p-4">
        {loading && !users.length ? (
          <div className="text-center text-gray-500 py-4">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="text-center text-gray-500 py-4">No users found</div>
        ) : (
          <div className="space-y-2">
            {users.map((user) => (
              <div
                key={user.user_id}
                className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{user.email}</div>
                    <div className="text-sm text-gray-600">
                      {user.username} {user.is_admin && <span className="text-primary">(Admin)</span>}
                    </div>
                    {user.created_at && (
                      <div className="text-xs text-gray-500 mt-1">
                        Created: {new Date(user.created_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => startEdit(user)}
                      className="text-sm text-primary hover:text-primary/80"
                      disabled={loading}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => setShowResetPassword(showResetPassword === user.user_id ? null : user.user_id)}
                      className="text-sm text-primary hover:text-primary/80"
                      disabled={loading}
                    >
                      Reset Password
                    </button>
                    <button
                      onClick={() => handleToggleAdmin(user.user_id, user.is_admin)}
                      className="text-sm text-primary hover:text-primary/80"
                      disabled={loading}
                    >
                      {user.is_admin ? "Remove Admin" : "Make Admin"}
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.user_id)}
                      className="text-sm text-red-600 hover:text-red-800"
                      disabled={loading}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                {showResetPassword === user.user_id && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg space-y-2">
                    <input
                      type="password"
                      value={resetPasswordValue}
                      onChange={(e) => setResetPasswordValue(e.target.value)}
                      placeholder="New password (min 6 characters)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:border-primary"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleResetPassword(user.user_id)}
                        disabled={loading || !resetPasswordValue}
                        className="btn-primary px-3 py-1 text-sm disabled:opacity-60"
                      >
                        Reset
                      </button>
                      <button
                        onClick={() => {
                          setShowResetPassword(null);
                          setResetPasswordValue("");
                        }}
                        className="btn-secondary px-3 py-1 text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

