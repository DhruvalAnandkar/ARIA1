import React from "react";
import { TouchableOpacity, Text, StyleSheet, Vibration } from "react-native";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";
import { a11y } from "../../constants/accessibility";

interface Props {
  onPress: () => void;
  active: boolean;
}

export default function SOSButton({ onPress, active }: Props) {
  const handlePress = () => {
    Vibration.vibrate([0, 300, 200, 300, 200, 300]);
    onPress();
  };

  return (
    <TouchableOpacity
      style={[styles.btn, active && styles.btnActive]}
      onPress={handlePress}
      accessibilityLabel={a11y.sign.sosButton.label}
      accessibilityHint={a11y.sign.sosButton.hint}
      accessibilityRole="button"
    >
      <Text style={[styles.text, active && styles.textActive]}>SOS</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    backgroundColor: colors.dangerDark,
    borderWidth: 2,
    borderColor: colors.danger,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.xxl,
    padding: spacing.lg,
    alignItems: "center",
  },
  btnActive: {
    backgroundColor: colors.danger,
  },
  text: {
    color: colors.danger,
    fontSize: fontSize.xl,
    fontWeight: "800",
    letterSpacing: 2,
  },
  textActive: {
    color: colors.text,
  },
});
