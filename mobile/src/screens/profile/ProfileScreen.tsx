import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useAuthStore } from "../../stores/useAuthStore";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";

export default function ProfileScreen() {
  const { userName, logout } = useAuthStore();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {userName?.charAt(0)?.toUpperCase() || "?"}
          </Text>
        </View>
        <Text style={styles.name}>{userName || "User"}</Text>
      </View>

      <Text style={styles.sectionTitle}>Preferences</Text>
      <Text style={styles.placeholder}>
        User preferences settings will be implemented in Phase 6.
      </Text>

      <TouchableOpacity
        style={styles.logoutBtn}
        onPress={logout}
        accessibilityRole="button"
        accessibilityLabel="Sign out"
      >
        <Text style={styles.logoutBtnText}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.xxl,
  },
  header: {
    alignItems: "center",
    marginTop: spacing.xxxl,
    marginBottom: spacing.xxxl,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primaryDark,
    borderWidth: 2,
    borderColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: "700",
    color: colors.primary,
  },
  name: {
    fontSize: fontSize.xxxl,
    fontWeight: "600",
    color: colors.text,
  },
  sectionTitle: {
    fontSize: fontSize.xxl,
    fontWeight: "600",
    color: colors.text,
    marginBottom: spacing.md,
  },
  placeholder: {
    fontSize: fontSize.lg,
    color: colors.textMuted,
    marginBottom: spacing.xxxl,
  },
  logoutBtn: {
    backgroundColor: colors.dangerDark,
    borderWidth: 1,
    borderColor: colors.danger,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: "center",
    marginTop: "auto",
  },
  logoutBtnText: {
    color: colors.danger,
    fontSize: fontSize.xl,
    fontWeight: "600",
  },
});
