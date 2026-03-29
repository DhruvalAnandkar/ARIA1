import { create } from "zustand";
import { loginUser, registerUser } from "../services/auth";
import {
  getToken,
  getUser,
  removeToken,
  removeUser,
  saveToken,
  saveUser,
} from "../utils/storage";

interface AuthState {
  token: string | null;
  userId: string | null;
  userName: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  initialize: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userId: null,
  userName: null,
  isAuthenticated: false,
  isLoading: true,

  initialize: async () => {
    const token = await getToken();
    const user = await getUser();
    if (token && user) {
      set({
        token,
        userId: user.user_id,
        userName: user.name,
        isAuthenticated: true,
        isLoading: false,
      });
    } else {
      set({ isLoading: false });
    }
  },

  login: async (email, password) => {
    const res = await loginUser(email, password);
    await saveToken(res.token);
    await saveUser({ user_id: res.user_id, name: res.name, email });
    set({
      token: res.token,
      userId: res.user_id,
      userName: res.name,
      isAuthenticated: true,
    });
  },

  register: async (email, password, name) => {
    const res = await registerUser(email, password, name);
    await saveToken(res.token);
    await saveUser({ user_id: res.user_id, name: res.name, email });
    set({
      token: res.token,
      userId: res.user_id,
      userName: res.name,
      isAuthenticated: true,
    });
  },

  logout: async () => {
    await removeToken();
    await removeUser();
    set({
      token: null,
      userId: null,
      userName: null,
      isAuthenticated: false,
    });
  },
}));
