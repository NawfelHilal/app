import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
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
  const [professionalCardNumber, setProfessionalCardNumber] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [siretNumber, setSiretNumber] = useState('');
  const [insurancePolicyNumber, setInsurancePolicyNumber] = useState('');
  const [gender, setGender] = useState<'FEMALE' | 'MALE' | 'OTHER' | 'UNDISCLOSED'>('UNDISCLOSED');
  const [plateNumber, setPlateNumber] = useState('');
  const [vehicleBrand, setVehicleBrand] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [vehicleColor, setVehicleColor] = useState('');
  const [vehicleSeats, setVehicleSeats] = useState('4');
  const [isPmrAdapted, setIsPmrAdapted] = useState(false);
  const [pmrCertificationReference, setPmrCertificationReference] = useState('');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);

  async function register() {
    setLoading(true);
    try {
      await api.post('/accounts/', { username, email, password, role });
      await login(username, password);
      if (role === 'DRIVER') {
        await api.post('/driver-profiles/', {
          license_number: licenseNumber,
          professional_card_number: professionalCardNumber,
          company_name: companyName,
          siret_number: siretNumber,
          insurance_policy_number: insurancePolicyNumber,
          gender,
        });
        await api.post('/vehicles/', {
          plate_number: plateNumber,
          brand: vehicleBrand || 'À compléter',
          model: vehicleModel || 'À compléter',
          color: vehicleColor || 'À compléter',
          seats: Number(vehicleSeats) || 4,
          is_pmr_adapted: isPmrAdapted,
          pmr_certification_reference: isPmrAdapted ? pmrCertificationReference : '',
        });
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
        {role === 'DRIVER' ? (
          <View style={styles.driverForm}>
            <Text style={styles.sectionTitle}>Informations professionnelles</Text>
            <TextInput value={licenseNumber} onChangeText={setLicenseNumber} placeholder="Numéro de permis" style={styles.input} />
            <TextInput value={professionalCardNumber} onChangeText={setProfessionalCardNumber} placeholder="Carte professionnelle VTC" style={styles.input} />
            <TextInput value={companyName} onChangeText={setCompanyName} placeholder="Entreprise / statut" style={styles.input} />
            <TextInput value={siretNumber} onChangeText={setSiretNumber} placeholder="SIRET" style={styles.input} keyboardType="number-pad" />
            <TextInput value={insurancePolicyNumber} onChangeText={setInsurancePolicyNumber} placeholder="Police d'assurance pro" style={styles.input} />
            <Text style={styles.helper}>Éligibilité FleetHer : uniquement chauffeurs femmes.</Text>
            <View style={styles.choiceRow}>
              {[
                ['FEMALE', 'Femme'],
                ['MALE', 'Homme'],
                ['OTHER', 'Autre'],
              ].map(([value, label]) => (
                <Pressable key={value} onPress={() => setGender(value as typeof gender)} style={[styles.choice, gender === value && styles.choiceSelected]}>
                  <Text style={styles.choiceText}>{label}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.sectionTitle}>Véhicule</Text>
            <TextInput value={plateNumber} onChangeText={setPlateNumber} placeholder="Immatriculation" style={styles.input} autoCapitalize="characters" />
            <TextInput value={vehicleBrand} onChangeText={setVehicleBrand} placeholder="Marque" style={styles.input} />
            <TextInput value={vehicleModel} onChangeText={setVehicleModel} placeholder="Modèle" style={styles.input} />
            <TextInput value={vehicleColor} onChangeText={setVehicleColor} placeholder="Couleur" style={styles.input} />
            <TextInput value={vehicleSeats} onChangeText={setVehicleSeats} placeholder="Nombre de places" style={styles.input} keyboardType="number-pad" />
            <Pressable onPress={() => setIsPmrAdapted((value) => !value)} style={[styles.toggle, isPmrAdapted && styles.toggleOn]}>
              <Text style={styles.toggleText}>{isPmrAdapted ? 'Véhicule adapté PMR : oui' : 'Véhicule adapté PMR : non'}</Text>
            </Pressable>
            {isPmrAdapted ? (
              <TextInput value={pmrCertificationReference} onChangeText={setPmrCertificationReference} placeholder="Référence adaptation / certificat PMR" style={styles.input} />
            ) : null}
          </View>
        ) : null}
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
  driverForm: { gap: 12 },
  sectionTitle: { color: colors.ink, fontSize: 18, fontWeight: '900', marginTop: 6 },
  helper: { color: colors.muted, fontWeight: '700' },
  choiceRow: { flexDirection: 'row', gap: 8 },
  choice: { flex: 1, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.surface },
  choiceSelected: { borderColor: colors.ink, backgroundColor: colors.softAccent },
  choiceText: { color: colors.ink, textAlign: 'center', fontWeight: '800' },
  toggle: { padding: 14, borderRadius: 8, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.surface },
  toggleOn: { borderColor: colors.success, backgroundColor: colors.softAccent },
  toggleText: { color: colors.ink, fontWeight: '900', textAlign: 'center' },
  input: { height: 52, borderWidth: 1, borderColor: colors.line, borderRadius: 8, paddingHorizontal: 14, backgroundColor: colors.surface, color: colors.ink },
  button: { height: 52, borderRadius: 8, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.ink },
  buttonText: { color: colors.surface, fontWeight: '800' },
  back: { color: colors.ink, textAlign: 'center', fontWeight: '700' },
});
