import React, { useRef, useEffect } from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { colors, spacing, borderRadius, fontSize } from "../../constants/theme";
import type { TranscriptEntry } from "../../types/sign";

interface Props {
  entries: TranscriptEntry[];
}

export default function TranscriptFeed({ entries }: Props) {
  const scrollRef = useRef<ScrollView>(null);

  useEffect(() => {
    scrollRef.current?.scrollToEnd({ animated: true });
  }, [entries]);

  return (
    <ScrollView ref={scrollRef} style={styles.container}>
      {entries.length === 0 ? (
        <Text style={styles.emptyHint}>
          Start signing in front of your phone camera. Your words will appear
          here.
        </Text>
      ) : (
        entries.map((entry) => {
          const emotionColor =
            colors.emotion[entry.emotion] || colors.emotion.neutral;
          const isSOS = entry.emotion === "sos";

          return (
            <View
              key={entry.id}
              style={[styles.entry, isSOS && styles.entrySOSPulse]}
              accessibilityLabel={`${entry.text}. Emotion: ${entry.emotion}. Time: ${entry.timestamp}`}
            >
              <Text style={styles.entryText}>{entry.text}</Text>
              <View style={styles.entryMeta}>
                <Text style={[styles.entryEmotion, { color: emotionColor }]}>
                  {entry.emotion}
                </Text>
                <Text style={styles.entryTime}>{entry.timestamp}</Text>
              </View>
            </View>
          );
        })
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginBottom: spacing.lg,
  },
  emptyHint: {
    color: colors.textPlaceholder,
    fontSize: fontSize.lg - 1,
    textAlign: "center",
    marginTop: 60,
    lineHeight: 24,
  },
  entry: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.lg - 2,
    marginBottom: spacing.sm + 2,
    borderWidth: 1,
    borderColor: colors.border,
  },
  entrySOSPulse: {
    borderColor: colors.danger,
    backgroundColor: colors.dangerDark,
  },
  entryText: {
    color: colors.text,
    fontSize: fontSize.xxl,
    fontWeight: "500",
    marginBottom: spacing.sm - 2,
    lineHeight: 26,
  },
  entryMeta: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  entryEmotion: {
    fontSize: fontSize.sm,
    fontWeight: "600",
    textTransform: "uppercase",
  },
  entryTime: {
    color: colors.textDim,
    fontSize: fontSize.sm,
  },
});
