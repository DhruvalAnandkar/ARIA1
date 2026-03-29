import React from "react";
import { View, ActivityIndicator, Text, StyleSheet } from "react-native";
import { colors, fontSize } from "../../constants/theme";

interface Props {
  message?: string;
}

export default function LoadingOverlay({ message }: Props) {
  return (
    <View style={styles.overlay}>
      <ActivityIndicator size="large" color={colors.primary} />
      {message && <Text style={styles.text}>{message}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.7)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 100,
  },
  text: {
    color: colors.text,
    fontSize: fontSize.lg,
    marginTop: 16,
  },
});
