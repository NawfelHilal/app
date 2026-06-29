import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, TextInput } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api, UserRole } from '../api/client';
import { RootStackParamList } from '../navigation/RootNavigator';
import { useAuthStore } from '../store/auth';
import { colors } from '../theme/colors';

type Props = NativeStackScreenProps<RootStackParamList, 'Register'>;

export function RegisterScreen({ navigation }: Props) {
  const [role, setRole] = useState<UserRole>('PASSENGER');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [licenseNumber, setLicenseNumber] = useState('');
  const [plateNumber, setPlateNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);

  async function register() {
    setLoading(true);
    try {
      await api.post('/accounts/', { username, email, password, role });
      await login(username, password);
      if (role === 'DRIVER') {
        await api.post('/driver-profiles/', { license_number: licenseNumber });
        await api.post('/vehicles/', { plate_number: plateNumber, brand: 'À compléter', model: 'À compléter', color: 'À compléter', seats: 4 });
      }
    } catch {
      Alert.alert('Inscription impossible', 'Vérifie les informations et réessaie.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Créer un compte</Text>
        <Pressable onPress={() => setRole(role === 'PASSENGER' ? 'DRIVER' : 'PASSENGER')} style={styles.role}>
          <Text style={styles.roleText}>{role === 'PASSENGER' ? 'Compte passager' : 'Compte chauffeur'}</Text>
        </Pressable>
        <TextInput value={username} onChangeText={setUsername} placeholder="Identifiant" style={styles.input} autoCapitalize="none" />
        <TextInput value={email} onChangeText={setEmail} placeholder="Email" style={styles.input} autoCapitalize="none" keyboardType="email-address" />
        <TextInput value={password} onChangeText={setPassword} placeholder="Mot de passe" style={styles.input} secureTextEntry />
        {role === 'DRIVER' ? <TextInput value={licenseNumber} onChangeText={setLicenseNumber} placeholder="Numéro de permis" style={styles.input} /> : null}
        {role === 'DRIVER' ? <TextInput value={plateNumber} onChangeText={setPlateNumber} placeholder="Immatriculation" style={styles.input} autoCapitalize="characters" /> : null}
        <Pressable onPress={register} disabled={loading} style={styles.button}><Text style={styles.buttonText}>{loading ? 'Création...' : 'Créer le compte'}</Text></Pressable>
        <Pressable onPress={() => navigation.goBack()}><Text style={styles.back}>Retour à la connexion</Text></Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, gap: 14, justifyContent: 'center', flexGrow: 1 },
  title: { color: colors.ink, fontSize: 32, fontWeight: '900', marginBottom: 8 },
  role: { padding: 14, borderRadius: 8, backgroundColor: colors.softAccent },
  roleText: { color: colors.ink, fontWeight: '900', textAlign: 'center' },
  input: { height: 52, borderWidth: 1, borderColor: colors.line, borderRadius: 8, paddingHorizontal: 14, backgroundColor: colors.surface, color: colors.ink },
  button: { height: 52, borderRadius: 8, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.ink },
  buttonText: { color: colors.surface, fontWeight: '800' },
  back: { color: colors.ink, textAlign: 'center', fontWeight: '700' },
});
