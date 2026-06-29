import { ReactNode } from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';
import { colors } from '../theme/colors';

type Props = {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  icon?: ReactNode;
  disabled?: boolean;
};

export function AppButton({ label, onPress, variant = 'primary', icon, disabled }: Props) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.button,
        styles[variant],
        pressed && styles.pressed,
        disabled && styles.disabled,
      ]}
    >
      {icon}
      <Text style={[styles.label, variant !== 'primary' && styles.darkLabel]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 50,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 8,
    paddingHorizontal: 16,
  },
  primary: { backgroundColor: colors.ink },
  secondary: { backgroundColor: colors.softAccent },
  ghost: { backgroundColor: 'transparent' },
  pressed: { opacity: 0.82 },
  disabled: { opacity: 0.5 },
  label: { color: colors.surface, fontWeight: '800', fontSize: 15 },
  darkLabel: { color: colors.ink },
});

