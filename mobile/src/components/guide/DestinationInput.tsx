import React from "react";
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from "react-native";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";
import { a11y } from "../../constants/accessibility";

interface Props {
  value: string;
  onChangeText: (text: string) => void;
  onSubmit: () => void;
}

export default function DestinationInput({ value, onChangeText, onSubmit }: Props) {
  return (
    <View style={styles.row}>
      <TextInput
        style={styles.input}
        placeholder="Enter destination..."
        placeholderTextColor={colors.textDim}
        value={value}
        onChangeText={onChangeText}
        returnKeyType="go"
        onSubmitEditing={onSubmit}
        accessibilityLabel={a11y.guide.destinationInput.label}
        accessibilityHint={a11y.guide.destinationInput.hint}
      />
      <TouchableOpacity
        style={styles.goBtn}
        onPress={onSubmit}
        accessibilityLabel={a11y.guide.goButton.label}
        accessibilityHint={a11y.guide.goButton.hint}
        accessibilityRole="button"
      >
        <Text style={styles.goBtnText}>Go</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    gap: spacing.sm + 2,
  },
  input: {
    flex: 1,
    backgroundColor: colors.surface,
    color: colors.text,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: fontSize.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  goBtn: {
    backgroundColor: colors.successBorder,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.xl,
    justifyContent: "center",
  },
  goBtnText: {
    color: colors.text,
    fontWeight: "700",
    fontSize: fontSize.lg,
  },
});
