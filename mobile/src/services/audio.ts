import { Audio } from "expo-av";
import { useConnectionStore } from "../stores/useConnectionStore";

let currentSound: Audio.Sound | null = null;

export async function initAudio(): Promise<void> {
  await Audio.setAudioModeAsync({
    allowsRecordingIOS: false,
    playsInSilentModeIOS: true,
    staysActiveInBackground: true,
  });
}

export async function playAudioFromUrl(audioUrl: string): Promise<void> {
  try {
    await stopAudio();

    // Build full URL if relative
    const fullUrl = audioUrl.startsWith("http")
      ? audioUrl
      : `${useConnectionStore.getState().backendUrl}${audioUrl}`;

    const { sound } = await Audio.Sound.createAsync({ uri: fullUrl });
    currentSound = sound;

    sound.setOnPlaybackStatusUpdate((status) => {
      if (status.isLoaded && status.didJustFinish) {
        sound.unloadAsync();
        if (currentSound === sound) {
          currentSound = null;
        }
      }
    });

    await sound.playAsync();
  } catch (error) {
    console.error("Audio playback error:", error);
  }
}

export async function stopAudio(): Promise<void> {
  if (currentSound) {
    try {
      await currentSound.stopAsync();
      await currentSound.unloadAsync();
    } catch {
      // Sound may already be unloaded
    }
    currentSound = null;
  }
}
