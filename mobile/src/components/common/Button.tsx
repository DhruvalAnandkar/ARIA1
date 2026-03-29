import React from "react";
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from "react-native";
import { hapticLight } from "../../utils/haptics";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";

interface Props {
  title: string;
  onPress: () => void;
  variant?: "primary" | "danger" | "success" | "outline";
  loading?: boolean;
  disabled?: boolean;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export default function Button({
  title,
  onPress,
  variant = "primary",
  loading = false,
  disabled = false,
  accessibilityLabel,
  accessibilityHint,
  style,
  textStyle,
}: Props) {
  const handlePress = async () => {
    await hapticLight();
    onPress();
  };

  const variantStyles = {
    primary: { bg: colors.primary, text: colors.text },
    danger: { bg: colors.danger, text: colors.text },
    success: { bg: colors.successBorder, text: colors.text },
    outline: { bg: "transparent", text: colors.primary },
  };

  const { bg, text: textColor } = variantStyles[variant];

  return (
    <TouchableOpacity
      style={[
        styles.btn,
        { backgroundColor: bg },
        variant === "outline" && { borderWidth: 1, borderColor: colors.primary },
        disabled && styles.disabled,
        style,
      ]}
      onPress={handlePress}
      disabled={disabled || loading}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled: disabled || loading }}
    >
      {loading ? (
        <ActivityIndicator color={textColor} />
      ) : (
        <Text style={[styles.text, { color: textColor }, textStyle]}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: {
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48, // Minimum touch target for accessibility
  },
  text: {
    fontSize: fontSize.xl,
    fontWeight: "600",
  },
  disabled: {
    opacity: 0.5,
  },
});
