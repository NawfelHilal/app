import { useState } from 'react';
import { AxiosError } from 'axios';
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { apiUrl } from '../api/client';
import { useAuthStore } from '../store/auth';
import { colors } from '../theme/colors';

export function LoginScreen() {
  const [username, setUsername] = useState('passenger');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);

  async function submit() {
    setLoading(true);
    try {
      await login(username, password);
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

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.logoMark}><Text style={styles.logoText}>F</Text></View>
      <Text style={styles.brand}>FleetPro</Text>
      <Text style={styles.subtitle}>Courses VTC ethiques, commission fixe et experience chauffeur claire.</Text>
      <TextInput value={username} onChangeText={setUsername} autoCapitalize="none" placeholder="Identifiant" placeholderTextColor={colors.muted} style={styles.input} />
      <TextInput value={password} onChangeText={setPassword} secureTextEntry placeholder="Mot de passe" placeholderTextColor={colors.muted} style={styles.input} />
      <Pressable onPress={submit} disabled={loading} style={styles.button}>
        <Text style={styles.buttonText}>{loading ? 'Connexion...' : 'Se connecter'}</Text>
      </Pressable>
      <Text style={styles.helper}>passenger / password123 ou driver / password123</Text>
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
  helper: { color: colors.muted, textAlign: 'center', marginTop: 8 },
});
