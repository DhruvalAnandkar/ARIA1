import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";
import type { NavStep } from "../../types/api";

interface Props {
  step: NavStep;
  currentIndex: number;
  totalSteps: number;
}

export default function NavigationStepCard({ step, currentIndex, totalSteps }: Props) {
  return (
    <View
      style={styles.card}
      accessibilityLabel={`Step ${currentIndex + 1} of ${totalSteps}: ${step.instruction}`}
    >
      <Text style={styles.stepNum}>
        Step {currentIndex + 1} of {totalSteps}
      </Text>
      <Text style={styles.stepText}>{step.instruction}</Text>
      <Text style={styles.stepMeta}>
        {step.distance} · {step.duration}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.successDark,
    borderRadius: borderRadius.md,
    padding: spacing.lg - 2,
    borderWidth: 1,
    borderColor: colors.successBorder,
  },
  stepNum: {
    color: colors.successBorder,
    fontSize: fontSize.sm,
    fontWeight: "600",
    marginBottom: spacing.xs,
  },
  stepText: {
    color: colors.text,
    fontSize: fontSize.xl,
    lineHeight: 24,
    marginBottom: spacing.xs,
  },
  stepMeta: {
    color: colors.textMuted,
    fontSize: fontSize.sm,
  },
});
