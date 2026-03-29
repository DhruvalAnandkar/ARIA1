import api from "./api";
import type { UserPreferences, UserProfile } from "../types/api";

export async function getProfile(): Promise<UserProfile> {
  const response = await api.get<UserProfile>("/user/profile");
  return response.data;
}

export async function updateProfile(
  updates: Partial<Pick<UserProfile, "name">>
): Promise<UserProfile> {
  const response = await api.patch<UserProfile>("/user/profile", updates);
  return response.data;
}

export async function getPreferences(): Promise<UserPreferences> {
  const response = await api.get<UserPreferences>("/user/preferences");
  return response.data;
}

export async function updatePreferences(
  updates: Partial<UserPreferences>
): Promise<UserPreferences> {
  const response = await api.patch<UserPreferences>(
    "/user/preferences",
    updates
  );
  return response.data;
}
