import { create } from "zustand";
import type { NavStep } from "../types/api";

interface GuideState {
  isScanning: boolean;
  lastWarning: string;
  lastSeverity: "clear" | "caution" | "danger";

  isNavigating: boolean;
  routeId: string | null;
  navSteps: NavStep[];
  currentStep: number;
  totalDistance: string;
  totalDuration: string;

  setIsScanning: (scanning: boolean) => void;
  setLastWarning: (warning: string, severity: "clear" | "caution" | "danger") => void;
  setNavigation: (
    routeId: string,
    steps: NavStep[],
    totalDistance: string,
    totalDuration: string
  ) => void;
  setCurrentStep: (step: number) => void;
  setIsNavigating: (navigating: boolean) => void;
  clearNavigation: () => void;
}

export const useGuideStore = create<GuideState>((set) => ({
  isScanning: false,
  lastWarning: "Tap 'Start Scanning' to begin",
  lastSeverity: "clear",

  isNavigating: false,
  routeId: null,
  navSteps: [],
  currentStep: 0,
  totalDistance: "",
  totalDuration: "",

  setIsScanning: (scanning) => set({ isScanning: scanning }),
  setLastWarning: (warning, severity) =>
    set({ lastWarning: warning, lastSeverity: severity }),
  setNavigation: (routeId, steps, totalDistance, totalDuration) =>
    set({
      routeId,
      navSteps: steps,
      currentStep: 0,
      totalDistance,
      totalDuration,
      isNavigating: true,
    }),
  setCurrentStep: (step) => set({ currentStep: step }),
  setIsNavigating: (navigating) => set({ isNavigating: navigating }),
  clearNavigation: () =>
    set({
      isNavigating: false,
      routeId: null,
      navSteps: [],
      currentStep: 0,
      totalDistance: "",
      totalDuration: "",
    }),
}));
