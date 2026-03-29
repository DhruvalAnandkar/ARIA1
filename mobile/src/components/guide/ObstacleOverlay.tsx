import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";

interface Props {
  warning: string;
  severity: "clear" | "caution" | "danger";
  isScanning: boolean;
}

const SEVERITY_COLORS = {
  clear: colors.success,
  caution: colors.warning,
  danger: colors.dangerLight,
};

export default function ObstacleOverlay({ warning, severity, isScanning }: Props) {
  const severityColor = SEVERITY_COLORS[severity];

  return (
    <View style={styles.overlay}>
      <View
        style={[styles.warningBanner, { borderColor: severityColor }]}
        accessibilityLabel={`Obstacle warning: ${warning}. Severity: ${severity}`}
        accessibilityLiveRegion="assertive"
      >
        <Text style={[styles.severityText, { color: severityColor }]}>
          {severity.toUpperCase()}
        </Text>
        <Text style={styles.warningText}>{warning}</Text>
      </View>

      {isScanning && (
        <View style={styles.scanIndicator}>
          <Text style={styles.scanDot}>●</Text>
          <Text style={styles.scanLabel}>Scanning for obstacles</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: "space-between",
    padding: spacing.lg,
  },
  warningBanner: {
    backgroundColor: "rgba(0,0,0,0.75)",
    borderRadius: borderRadius.md,
    padding: spacing.lg - 2,
    marginTop: spacing.sm,
    borderWidth: 1,
  },
  severityText: {
    fontSize: fontSize.xs,
    fontWeight: "700",
    letterSpacing: 1,
    marginBottom: spacing.xs,
  },
  warningText: {
    color: colors.text,
    fontSize: fontSize.xxl,
    fontWeight: "500",
    textAlign: "center",
  },
  scanIndicator: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
  scanDot: {
    color: colors.dangerLight,
    fontSize: fontSize.xl,
  },
  scanLabel: {
    color: colors.text,
    fontSize: fontSize.md,
    backgroundColor: "rgba(0,0,0,0.6)",
    paddingHorizontal: spacing.sm + 2,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
  },
});
