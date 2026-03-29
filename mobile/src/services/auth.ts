import api from "./api";
import type { TokenResponse } from "../types/api";

export async function registerUser(
  email: string,
  password: string,
  name: string
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/register", {
    email,
    password,
    name,
  });
  return response.data;
}

export async function loginUser(
  email: string,
  password: string
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/login", {
    email,
    password,
  });
  return response.data;
}
