import { useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { AxiosError } from 'axios';
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { apiUrl } from '../api/client';
import { useAuthStore } from '../store/auth';
import { colors } from '../theme/colors';
import { RootStackParamList } from '../navigation/RootNavigator';

type Props = Readonly<NativeStackScreenProps<RootStackParamList, 'Login'>>;

export function LoginScreen({ navigation, route }: Props) {
  const selectedRole = route.params.role;
  const isDriver = selectedRole === 'DRIVER';
  const demoUsername = isDriver ? 'driver' : 'passenger';
  const demoPassword = process.env.EXPO_PUBLIC_DEMO_PASSWORD || '';
  const [username, setUsername] = useState(demoUsername);
  const [password, setPassword] = useState(demoPassword);
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    setUsername(demoUsername);
    setPassword(demoPassword);
  }, [demoPassword, demoUsername]);

  async function submit(credentials?: { username: string; password: string }) {
    setLoading(true);
    try {
      await login((credentials?.username || username).trim(), credentials?.password || password);
    } catch (error) {
      const axiosError = error as AxiosError;
      const detail = axiosError.response
        ? `HTTP ${axiosError.response.status} depuis ${apiUrl}`
        : `${axiosError.message || 'Erreur reseau'} depuis ${apiUrl}`;
      Alert.alert('Connexion impossible', detail);
    } finally {
      setLoading(false);
    }
  }

  function submitDemo(demoUsername: string) {
    if (!demoPassword) {
      Alert.alert('Démo non configurée', 'Définis EXPO_PUBLIC_DEMO_PASSWORD pour activer la connexion démo.');
      return;
    }
    submit({ username: demoUsername, password: demoPassword });
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.logoMark}><Text style={styles.logoText}>F</Text></View>
      <Text style={styles.brand}>FleetPro</Text>
      <Text style={styles.subtitle}>
        {isDriver ? 'Connexion chauffeur partenaire FleetPro.' : 'Connexion passager pour commander une course FleetPro.'}
      </Text>
      <TextInput
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        placeholder="Identifiant"
        placeholderTextColor={colors.muted}
        style={styles.input}
        accessibilityLabel="Identifiant"
        accessibilityHint="Saisissez votre nom d'utilisateur FleetPro"
        textContentType="username"
      />
      <TextInput
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        placeholder="Mot de passe"
        placeholderTextColor={colors.muted}
        style={styles.input}
        accessibilityLabel="Mot de passe"
        accessibilityHint="Saisissez votre mot de passe"
        textContentType="password"
      />
      <Pressable
        onPress={() => submit()}
        disabled={loading}
        accessibilityRole="button"
        accessibilityLabel={loading ? 'Connexion en cours' : 'Se connecter'}
        accessibilityHint="Valide les identifiants saisis"
        accessibilityState={{ disabled: loading }}
        style={styles.button}
      >
        <Text style={styles.buttonText}>{loading ? 'Connexion...' : 'Se connecter'}</Text>
      </Pressable>
      <View style={styles.demoRow}>
        <Pressable
          onPress={() => submitDemo(demoUsername)}
          disabled={loading}
          accessibilityRole="button"
          accessibilityLabel={isDriver ? 'Connexion chauffeur démo' : 'Connexion passager démo'}
          accessibilityHint={isDriver ? 'Connecte automatiquement le compte chauffeur de démonstration' : 'Connecte automatiquement le compte passager de démonstration'}
          accessibilityState={{ disabled: loading }}
          style={styles.demoButton}
        >
          <Text style={styles.demoText}>{isDriver ? 'Chauffeur démo' : 'Passager démo'}</Text>
        </Pressable>
      </View>
      <Pressable
        onPress={() => navigation.navigate('Register', { role: selectedRole })}
        accessibilityRole="button"
        accessibilityLabel={isDriver ? 'Créer un compte chauffeur' : 'Créer un compte passager'}
        accessibilityHint="Ouvre le formulaire d'inscription adapté au rôle choisi"
      >
        <Text style={styles.register}>{isDriver ? 'Créer un compte chauffeur' : 'Créer un compte passager'}</Text>
      </Pressable>
      <Pressable
        onPress={() => navigation.navigate('RoleSelection')}
        accessibilityRole="button"
        accessibilityLabel="Changer de profil"
        accessibilityHint="Revient au choix passager ou chauffeur"
      >
        <Text style={styles.register}>Changer de profil</Text>
      </Pressable>
      <Text style={styles.helper}>
        {demoPassword ? `Compte démo disponible : ${demoUsername}` : 'Connexion démo désactivée sans variable EXPO_PUBLIC_DEMO_PASSWORD'}
      </Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, gap: 14, backgroundColor: colors.background },
  logoMark: { width: 58, height: 58, borderRadius: 8, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  logoText: { color: colors.surface, fontSize: 30, fontWeight: '900' },
  brand: { fontSize: 40, fontWeight: '900', color: colors.ink, marginTop: 8 },
  subtitle: { color: colors.muted, fontSize: 16, marginBottom: 14, lineHeight: 22 },
  input: { height: 52, borderWidth: 1, borderColor: colors.line, borderRadius: 8, paddingHorizontal: 14, backgroundColor: colors.surface, color: colors.ink },
  button: { height: 52, borderRadius: 8, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.ink },
  buttonText: { color: 'white', fontWeight: '700' },
  demoRow: { flexDirection: 'row', gap: 10 },
  demoButton: { flex: 1, minHeight: 44, borderRadius: 8, backgroundColor: colors.softAccent, alignItems: 'center', justifyContent: 'center' },
  demoText: { color: colors.ink, fontWeight: '800' },
  helper: { color: colors.muted, textAlign: 'center', marginTop: 8 },
  register: { color: colors.ink, textAlign: 'center', fontWeight: '800' },
});
