import React from "react";
import { View, TouchableOpacity, Text, StyleSheet } from "react-native";
import { SUPPORTED_LANGUAGES } from "../../constants/config";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";

interface Props {
  selected: string;
  onSelect: (code: string) => void;
}

export default function LanguageSelector({ selected, onSelect }: Props) {
  return (
    <View style={styles.row}>
      {SUPPORTED_LANGUAGES.map((lang) => (
        <TouchableOpacity
          key={lang.code}
          style={[styles.btn, selected === lang.code && styles.btnActive]}
          onPress={() => onSelect(lang.code)}
          accessibilityLabel={`${lang.label} language`}
          accessibilityState={{ selected: selected === lang.code }}
          accessibilityRole="button"
        >
          <Text
            style={[
              styles.text,
              selected === lang.code && styles.textActive,
            ]}
          >
            {lang.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  btn: {
    paddingHorizontal: spacing.lg - 2,
    paddingVertical: spacing.sm - 2,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  btnActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  text: {
    color: colors.textMuted,
    fontSize: fontSize.md,
  },
  textActive: {
    color: colors.text,
  },
});
