import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Alert,
} from "react-native";
import { useAuthStore } from "../../stores/useAuthStore";
import { useConnectionStore } from "../../stores/useConnectionStore";
import { BACKEND_URL as DEFAULT_BACKEND_URL } from "../../constants/config";
import {
  colors,
  spacing,
  borderRadius,
  fontSize,
} from "../../constants/theme";

export default function ProfileScreen() {
  const { userName, logout } = useAuthStore();
  const { backendUrl, backendConnected, backendChecked, setBackendUrl, resetBackendUrl } =
    useConnectionStore();
  const [urlInput, setUrlInput] = useState(backendUrl);
  const [saving, setSaving] = useState(false);

  const isCustomUrl = backendUrl !== DEFAULT_BACKEND_URL;

  const handleSaveUrl = async () => {
    const trimmed = urlInput.trim();
    if (!trimmed) {
      Alert.alert("Invalid URL", "Please enter a valid server URL.");
      return;
    }
    if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
      Alert.alert(
        "Invalid URL",
        "URL must start with http:// or https://"
      );
      return;
    }
    setSaving(true);
    await setBackendUrl(trimmed);
    setSaving(false);
  };

  const handleReset = async () => {
    await resetBackendUrl();
    setUrlInput(DEFAULT_BACKEND_URL);
  };

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

      <Text style={styles.sectionTitle}>Server Connection</Text>
      <Text style={styles.hint}>
        Enter your backend URL or tunnel URL (e.g. ngrok, cloudflared) to
        connect across different networks.
      </Text>

      <View style={styles.urlRow}>
        <TextInput
          style={styles.urlInput}
          value={urlInput}
          onChangeText={setUrlInput}
          placeholder="https://your-tunnel-url.trycloudflare.com"
          placeholderTextColor={colors.textPlaceholder}
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
        />
      </View>

      <View style={styles.urlActions}>
        <TouchableOpacity
          style={[styles.saveBtn, saving && styles.btnDisabled]}
          onPress={handleSaveUrl}
          disabled={saving}
          accessibilityRole="button"
          accessibilityLabel="Save server URL"
        >
          <Text style={styles.saveBtnText}>
            {saving ? "Saving..." : "Save"}
          </Text>
        </TouchableOpacity>

        {isCustomUrl && (
          <TouchableOpacity
            style={styles.resetBtn}
            onPress={handleReset}
            accessibilityRole="button"
            accessibilityLabel="Reset to default URL"
          >
            <Text style={styles.resetBtnText}>Reset</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.statusRow}>
        <View
          style={[
            styles.statusDot,
            backendChecked
              ? backendConnected
                ? styles.statusConnected
                : styles.statusDisconnected
              : styles.statusPending,
          ]}
        />
        <Text style={styles.statusText}>
          {!backendChecked
            ? "Checking..."
            : backendConnected
            ? "Connected"
            : "Disconnected"}
        </Text>
        {isCustomUrl && (
          <Text style={styles.customBadge}>TUNNEL</Text>
        )}
      </View>

      <Text style={styles.currentUrl} numberOfLines={1}>
        {backendUrl}
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
    marginBottom: spacing.xxl,
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
    marginBottom: spacing.sm,
  },
  hint: {
    fontSize: fontSize.md,
    color: colors.textMuted,
    marginBottom: spacing.lg,
    lineHeight: 18,
  },
  urlRow: {
    marginBottom: spacing.md,
  },
  urlInput: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    color: colors.text,
    fontSize: fontSize.lg,
  },
  urlActions: {
    flexDirection: "row",
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  saveBtn: {
    flex: 1,
    backgroundColor: colors.primaryDark,
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    alignItems: "center",
  },
  saveBtnText: {
    color: colors.primary,
    fontSize: fontSize.lg,
    fontWeight: "600",
  },
  resetBtn: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  resetBtnText: {
    color: colors.textSecondary,
    fontSize: fontSize.lg,
    fontWeight: "500",
  },
  btnDisabled: {
    opacity: 0.5,
  },
  statusRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.xs,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: spacing.sm,
  },
  statusConnected: {
    backgroundColor: colors.success,
  },
  statusDisconnected: {
    backgroundColor: colors.danger,
  },
  statusPending: {
    backgroundColor: colors.warning,
  },
  statusText: {
    fontSize: fontSize.lg,
    color: colors.textSecondary,
  },
  customBadge: {
    marginLeft: spacing.sm,
    fontSize: fontSize.xs,
    fontWeight: "700",
    color: colors.primary,
    backgroundColor: colors.primaryDark,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
    overflow: "hidden",
  },
  currentUrl: {
    fontSize: fontSize.sm,
    color: colors.textDim,
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
