import { create } from "zustand";
import type { EmotionType, TranscriptEntry } from "../types/sign";

interface SignState {
  transcript: TranscriptEntry[];
  currentEmotion: EmotionType;
  currentBuffer: string;
  isListening: boolean;
  selectedLanguage: string;
  sosActive: boolean;

  addTranscriptEntry: (entry: TranscriptEntry) => void;
  setCurrentEmotion: (emotion: EmotionType) => void;
  setCurrentBuffer: (buffer: string) => void;
  setIsListening: (listening: boolean) => void;
  setSelectedLanguage: (lang: string) => void;
  setSosActive: (active: boolean) => void;
  clearTranscript: () => void;
}

export const useSignStore = create<SignState>((set) => ({
  transcript: [],
  currentEmotion: "neutral",
  currentBuffer: "",
  isListening: false,
  selectedLanguage: "en",
  sosActive: false,

  addTranscriptEntry: (entry) =>
    set((state) => ({ transcript: [...state.transcript, entry] })),
  setCurrentEmotion: (emotion) => set({ currentEmotion: emotion }),
  setCurrentBuffer: (buffer) => set({ currentBuffer: buffer }),
  setIsListening: (listening) => set({ isListening: listening }),
  setSelectedLanguage: (lang) => set({ selectedLanguage: lang }),
  setSosActive: (active) => set({ sosActive: active }),
  clearTranscript: () => set({ transcript: [] }),
}));
