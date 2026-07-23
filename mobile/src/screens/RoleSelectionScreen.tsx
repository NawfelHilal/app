import Feather from '@expo/vector-icons/Feather';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../components/AppButton';
import { RootStackParamList } from '../navigation/RootNavigator';
import { colors } from '../theme/colors';

type Props = Readonly<NativeStackScreenProps<RootStackParamList, 'RoleSelection'>>;

export function RoleSelectionScreen({ navigation }: Props) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.logoMark}><Text style={styles.logoText}>F</Text></View>
      <Text style={styles.brand}>FleetPro</Text>
      <Text style={styles.subtitle}>
        Choisissez votre espace pour accéder directement à la connexion adaptée.
      </Text>
      <View style={styles.actions}>
        <AppButton
          label="Je suis passager"
          icon={<Feather name="user" size={18} color={colors.surface} />}
          onPress={() => navigation.navigate('Login', { role: 'PASSENGER' })}
          accessibilityHint="Ouvre la connexion passager avec accès au compte démo passager"
        />
        <AppButton
          label="Je suis chauffeur"
          icon={<Feather name="navigation" size={18} color={colors.ink} />}
          variant="secondary"
          onPress={() => navigation.navigate('Login', { role: 'DRIVER' })}
          accessibilityHint="Ouvre la connexion chauffeur avec accès au compte démo chauffeur"
        />
      </View>
      <Text style={styles.helper}>
        Vous pourrez ensuite créer un compte ou utiliser le compte de démonstration.
      </Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, gap: 16, backgroundColor: colors.background },
  logoMark: { width: 58, height: 58, borderRadius: 8, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  logoText: { color: colors.surface, fontSize: 30, fontWeight: '900' },
  brand: { fontSize: 40, fontWeight: '900', color: colors.ink, marginTop: 8 },
  subtitle: { color: colors.muted, fontSize: 16, lineHeight: 22, marginBottom: 8 },
  actions: { gap: 12 },
  helper: { color: colors.muted, textAlign: 'center', marginTop: 10, lineHeight: 20 },
});
