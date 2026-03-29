import { useEffect, useRef } from "react";
import api from "../services/api";
import { HEALTH_CHECK_INTERVAL_MS } from "../constants/config";
import { useConnectionStore } from "../stores/useConnectionStore";

export function useBackendHealth() {
  const setBackendConnected = useConnectionStore(
    (s) => s.setBackendConnected
  );
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        await api.get("/health");
        setBackendConnected(true);
      } catch {
        setBackendConnected(false);
      }
    };

    check();
    intervalRef.current = setInterval(check, HEALTH_CHECK_INTERVAL_MS);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [setBackendConnected]);
}
