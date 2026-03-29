import React, { useEffect } from "react";
import { ActivityIndicator, View } from "react-native";
import { useAuthStore } from "../stores/useAuthStore";
import { useConnectionStore } from "../stores/useConnectionStore";
import AuthNavigator from "./AuthNavigator";
import MainNavigator from "./MainNavigator";
import { colors } from "../constants/theme";

export default function RootNavigator() {
  const { isAuthenticated, isLoading, initialize } = useAuthStore();
  const loadBackendUrl = useConnectionStore((s) => s.loadBackendUrl);

  useEffect(() => {
    loadBackendUrl();
    initialize();
  }, [initialize, loadBackendUrl]);

  if (isLoading) {
    return (
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: colors.background,
        }}
      >
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return isAuthenticated ? <MainNavigator /> : <AuthNavigator />;
}
