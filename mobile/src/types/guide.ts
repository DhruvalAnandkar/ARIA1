export interface ObstacleWarning {
  warning: string;
  severity: "clear" | "caution" | "danger";
  timestamp: string;
}

// Guide WebSocket messages
export interface WSLocationUpdate {
  type: "location_update";
  lat: number;
  lng: number;
}

export interface WSNextStep {
  type: "next_step";
  step_index: number;
  instruction: string;
  audio_url: string;
}

export interface WSOffRoute {
  type: "off_route";
  message: string;
}

export interface WSArrived {
  type: "arrived";
  message: string;
}

export type WSGuideServerMessage = WSNextStep | WSOffRoute | WSArrived;
