import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "aria_auth_token";
const USER_KEY = "aria_user";
const BACKEND_URL_KEY = "aria_backend_url";

export async function saveToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function getToken(): Promise<string | null> {
  return await SecureStore.getItemAsync(TOKEN_KEY);
}

export async function removeToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}

export async function saveUser(user: { user_id: string; name: string; email?: string }): Promise<void> {
  await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
}

export async function getUser(): Promise<{ user_id: string; name: string; email?: string } | null> {
  const data = await SecureStore.getItemAsync(USER_KEY);
  return data ? JSON.parse(data) : null;
}

export async function removeUser(): Promise<void> {
  await SecureStore.deleteItemAsync(USER_KEY);
}

export async function saveBackendUrl(url: string): Promise<void> {
  await SecureStore.setItemAsync(BACKEND_URL_KEY, url);
}

export async function getBackendUrl(): Promise<string | null> {
  return await SecureStore.getItemAsync(BACKEND_URL_KEY);
}

export async function removeBackendUrl(): Promise<void> {
  await SecureStore.deleteItemAsync(BACKEND_URL_KEY);
}
