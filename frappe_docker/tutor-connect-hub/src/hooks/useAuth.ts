import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { frappeApi } from "@/lib/frappe-api";
import { ROLES } from "@/lib/constants";
import type { AuthState, User } from "@/types";

export function useAuth() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["auth"],
    queryFn: async () => {
      const res = await frappeApi.getSessionUser();
      if (!res.message) return null;

      // Fetch full user info including roles
      try {
        const userInfo = await frappeApi.get<{
          data: {
            name: string;
            email: string;
            full_name: string;
            roles?: { role: string }[];
          };
        }>(`/api/resource/User/${encodeURIComponent(res.message.user)}`);
        const u = userInfo.data;
        return {
          name: u.name,
          email: u.email,
          full_name: u.full_name || res.message.full_name,
          roles: u.roles?.map((r) => r.role) || res.message.roles || [],
        } as User;
      } catch {
        return {
          name: res.message.user,
          email: res.message.user,
          full_name: res.message.full_name,
          roles: res.message.roles || [],
        } as User;
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const authState: AuthState = {
    user: data ?? null,
    isAuthenticated: !!data,
    isLoading,
    roles: data?.roles ?? [],
  };

  const loginMutation = useMutation({
    mutationFn: async ({ usr, pwd }: { usr: string; pwd: string }) => {
      const res = await frappeApi.login(usr, pwd);
      if (res.message !== "Logged In") {
        throw new Error(res.message || "Login failed");
      }
      return res;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth"] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => frappeApi.logout(),
    onSuccess: () => {
      queryClient.setQueryData(["auth"], null);
      queryClient.clear();
    },
  });

  const hasRole = (role: string): boolean => {
    return authState.roles.includes(role);
  };

  const isOwner = hasRole(ROLES.OWNER) || hasRole(ROLES.ADMIN);
  const isTutor = hasRole(ROLES.TUTOR);
  const isStudent = hasRole(ROLES.STUDENT);

  const getDefaultRoute = (): string => {
    if (isOwner) return "/owner";
    if (isTutor) return "/tutor";
    if (isStudent) return "/student";
    return "/";
  };

  return {
    ...authState,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    loginError: loginMutation.error?.message || null,
    hasRole,
    isOwner,
    isTutor,
    isStudent,
    getDefaultRoute,
  };
}
