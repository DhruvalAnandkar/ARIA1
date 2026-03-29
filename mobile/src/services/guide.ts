import api from "./api";
import type { NavigationResponse, ObstacleResponse } from "../types/api";

export async function sendObstacleFrame(
  frameBase64: string
): Promise<ObstacleResponse> {
  const response = await api.post<ObstacleResponse>("/guide/obstacle", {
    frame: frameBase64,
  });
  return response.data;
}

export async function getNavigation(
  lat: number,
  lng: number,
  destination: string
): Promise<NavigationResponse> {
  const response = await api.post<NavigationResponse>("/guide/navigate", {
    lat,
    lng,
    destination,
  });
  return response.data;
}
