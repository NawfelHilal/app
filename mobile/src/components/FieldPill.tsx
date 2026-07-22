import { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors } from '../theme/colors';

type Props = {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  onPress?: () => void;
  accessibilityLabel?: string;
  accessibilityHint?: string;
};

export function FieldPill({ title, subtitle, icon, onPress, accessibilityLabel, accessibilityHint }: Props) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole={onPress ? 'button' : 'text'}
      accessibilityLabel={accessibilityLabel || `${title}${subtitle ? `, ${subtitle}` : ''}`}
      accessibilityHint={accessibilityHint}
      style={styles.container}
    >
      <View style={styles.icon} accessible={false}>{icon}</View>
      <View style={styles.texts}>
        <Text style={styles.title} numberOfLines={1}>{title}</Text>
        {subtitle ? <Text style={styles.subtitle} numberOfLines={1}>{subtitle}</Text> : null}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    minHeight: 58,
    borderRadius: 8,
    backgroundColor: colors.softAccent,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    gap: 12,
  },
  icon: {
    width: 28,
    alignItems: 'center',
  },
  texts: { flex: 1 },
  title: { color: colors.ink, fontWeight: '800', fontSize: 16 },
  subtitle: { color: colors.muted, marginTop: 2 },
});
