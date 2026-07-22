import { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors } from '../theme/colors';

export type TabItem<T extends string> = {
  key: T;
  label: string;
  icon: ReactNode;
};

type Props<T extends string> = {
  tabs: TabItem<T>[];
  active: T;
  onChange: (tab: T) => void;
};

export function BottomTabs<T extends string>({ tabs, active, onChange }: Props<T>) {
  return (
    <View style={styles.wrap}>
      {tabs.map((tab) => {
        const selected = tab.key === active;
        return (
          <Pressable
            key={tab.key}
            onPress={() => onChange(tab.key)}
            accessibilityRole="tab"
            accessibilityLabel={`Onglet ${tab.label}`}
            accessibilityHint={`Affiche la section ${tab.label}`}
            accessibilityState={{ selected }}
            style={styles.tab}
          >
            <View style={[styles.iconWrap, selected && styles.iconWrapActive]}>{tab.icon}</View>
            <Text style={[styles.label, selected && styles.labelActive]}>{tab.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    paddingTop: 8,
    paddingBottom: 10,
  },
  tab: { flex: 1, alignItems: 'center', gap: 4 },
  iconWrap: {
    width: 38,
    height: 28,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconWrapActive: { backgroundColor: colors.softAccent },
  label: { color: colors.muted, fontSize: 12, fontWeight: '700' },
  labelActive: { color: colors.ink },
});
