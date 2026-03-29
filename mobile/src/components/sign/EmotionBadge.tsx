import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";
import type { EmotionType } from "../../types/sign";

interface Props {
  emotion: EmotionType;
}

export default function EmotionBadge({ emotion }: Props) {
  const emotionColor = colors.emotion[emotion] || colors.emotion.neutral;

  return (
    <View style={styles.row}>
      <Text style={styles.label}>Detected emotion:</Text>
      <View
        style={[styles.badge, { backgroundColor: emotionColor + "33" }]}
        accessibilityLabel={`Current emotion: ${emotion}`}
      >
        <Text style={[styles.text, { color: emotionColor }]}>
          {emotion.toUpperCase()}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  label: {
    color: colors.textMuted,
    fontSize: fontSize.md,
    marginRight: spacing.sm,
  },
  badge: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
  },
  text: {
    fontSize: fontSize.sm,
    fontWeight: "700",
    letterSpacing: 1,
  },
});
