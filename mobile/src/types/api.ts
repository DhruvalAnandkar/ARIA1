export interface TokenResponse {
  user_id: string;
  token: string;
  name: string;
}

export interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface UserPreferences {
  user_id: string;
  default_mode: "sign" | "guide";
  language: string;
  voice_style: string;
  tts_speed: number;
  obstacle_scan_interval_ms: number;
  high_contrast: boolean;
  large_text: boolean;
  sign_mode: {
    auto_speak: boolean;
    buffer_threshold: number;
  };
  guide_mode: {
    speak_clear_path: boolean;
    haptic_on_obstacle: boolean;
  };
}

export interface ObstacleResponse {
  warning: string;
  severity: "clear" | "caution" | "danger";
  audio_url: string;
}

export interface NavStep {
  instruction: string;
  distance: string;
  duration: string;
  lat?: number;
  lng?: number;
}

export interface NavigationResponse {
  route_id: string;
  steps: NavStep[];
  total_distance: string;
  total_duration: string;
}

export interface SpeakResponse {
  sentence: string;
  audio_url: string;
}
