import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api, UserRole } from '../api/client';
import { RootStackParamList } from '../navigation/RootNavigator';
import { useAuthStore } from '../store/auth';
import { colors } from '../theme/colors';

type Props = Readonly<NativeStackScreenProps<RootStackParamList, 'Register'>>;

export function RegisterScreen({ navigation, route }: Props) {
  const [role, setRole] = useState<UserRole>(route.params.role);
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
        <Pressable
          onPress={() => setRole(role === 'PASSENGER' ? 'DRIVER' : 'PASSENGER')}
          accessibilityRole="button"
          accessibilityLabel={role === 'PASSENGER' ? 'Type de compte passager' : 'Type de compte chauffeur'}
          accessibilityHint="Change le type de compte à créer"
          style={styles.role}
        >
          <Text style={styles.roleText}>{role === 'PASSENGER' ? 'Compte passager' : 'Compte chauffeur'}</Text>
        </Pressable>
        <TextInput
          value={username}
          onChangeText={setUsername}
          placeholder="Identifiant"
          style={styles.input}
          autoCapitalize="none"
          accessibilityLabel="Identifiant"
          accessibilityHint="Saisissez le nom d'utilisateur du nouveau compte"
          textContentType="username"
        />
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="Email"
          style={styles.input}
          autoCapitalize="none"
          keyboardType="email-address"
          accessibilityLabel="Email"
          accessibilityHint="Saisissez l'adresse email du nouveau compte"
          textContentType="emailAddress"
        />
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="Mot de passe"
          style={styles.input}
          secureTextEntry
          accessibilityLabel="Mot de passe"
          accessibilityHint="Saisissez le mot de passe du nouveau compte"
          textContentType="newPassword"
        />
        {role === 'DRIVER' ? (
          <View style={styles.driverForm}>
            <Text style={styles.sectionTitle}>Informations professionnelles</Text>
            <TextInput value={licenseNumber} onChangeText={setLicenseNumber} placeholder="Numéro de permis" style={styles.input} accessibilityLabel="Numéro de permis" accessibilityHint="Saisissez le numéro de permis du chauffeur" />
            <TextInput value={professionalCardNumber} onChangeText={setProfessionalCardNumber} placeholder="Carte professionnelle VTC" style={styles.input} accessibilityLabel="Carte professionnelle VTC" accessibilityHint="Saisissez le numéro de carte professionnelle VTC" />
            <TextInput value={companyName} onChangeText={setCompanyName} placeholder="Entreprise / statut" style={styles.input} accessibilityLabel="Entreprise ou statut" accessibilityHint="Saisissez l'entreprise ou le statut professionnel" />
            <TextInput value={siretNumber} onChangeText={setSiretNumber} placeholder="SIRET" style={styles.input} keyboardType="number-pad" accessibilityLabel="SIRET" accessibilityHint="Saisissez le numéro SIRET" />
            <TextInput value={insurancePolicyNumber} onChangeText={setInsurancePolicyNumber} placeholder="Police d'assurance pro" style={styles.input} accessibilityLabel="Police d'assurance professionnelle" accessibilityHint="Saisissez la référence d'assurance professionnelle" />
            <Text style={styles.helper}>Éligibilité FleetHer : uniquement chauffeurs femmes.</Text>
            <View style={styles.choiceRow}>
              {[
                ['FEMALE', 'Femme'],
                ['MALE', 'Homme'],
                ['OTHER', 'Autre'],
              ].map(([value, label]) => (
                <Pressable
                  key={value}
                  onPress={() => setGender(value as typeof gender)}
                  accessibilityRole="button"
                  accessibilityLabel={`Genre ${label}`}
                  accessibilityHint="Sélectionne le genre utilisé pour vérifier l'éligibilité FleetHer"
                  accessibilityState={{ selected: gender === value }}
                  style={[styles.choice, gender === value && styles.choiceSelected]}
                >
                  <Text style={styles.choiceText}>{label}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.sectionTitle}>Véhicule</Text>
            <TextInput value={plateNumber} onChangeText={setPlateNumber} placeholder="Immatriculation" style={styles.input} autoCapitalize="characters" accessibilityLabel="Immatriculation" accessibilityHint="Saisissez l'immatriculation du véhicule" />
            <TextInput value={vehicleBrand} onChangeText={setVehicleBrand} placeholder="Marque" style={styles.input} accessibilityLabel="Marque du véhicule" accessibilityHint="Saisissez la marque du véhicule" />
            <TextInput value={vehicleModel} onChangeText={setVehicleModel} placeholder="Modèle" style={styles.input} accessibilityLabel="Modèle du véhicule" accessibilityHint="Saisissez le modèle du véhicule" />
            <TextInput value={vehicleColor} onChangeText={setVehicleColor} placeholder="Couleur" style={styles.input} accessibilityLabel="Couleur du véhicule" accessibilityHint="Saisissez la couleur du véhicule" />
            <TextInput value={vehicleSeats} onChangeText={setVehicleSeats} placeholder="Nombre de places" style={styles.input} keyboardType="number-pad" accessibilityLabel="Nombre de places" accessibilityHint="Saisissez le nombre de places disponibles" />
            <Pressable
              onPress={() => setIsPmrAdapted((value) => !value)}
              accessibilityRole="switch"
              accessibilityLabel="Véhicule adapté PMR"
              accessibilityHint="Indique si le véhicule permet de transporter une personne à mobilité réduite"
              accessibilityState={{ checked: isPmrAdapted }}
              style={[styles.toggle, isPmrAdapted && styles.toggleOn]}
            >
              <Text style={styles.toggleText}>{isPmrAdapted ? 'Véhicule adapté PMR : oui' : 'Véhicule adapté PMR : non'}</Text>
            </Pressable>
            {isPmrAdapted ? (
              <TextInput value={pmrCertificationReference} onChangeText={setPmrCertificationReference} placeholder="Référence adaptation / certificat PMR" style={styles.input} accessibilityLabel="Référence certificat PMR" accessibilityHint="Saisissez la référence de certification ou d'adaptation PMR" />
            ) : null}
          </View>
        ) : null}
        <Pressable
          onPress={register}
          disabled={loading}
          accessibilityRole="button"
          accessibilityLabel={loading ? 'Création du compte en cours' : 'Créer le compte'}
          accessibilityHint="Valide le formulaire d'inscription"
          accessibilityState={{ disabled: loading }}
          style={styles.button}
        >
          <Text style={styles.buttonText}>{loading ? 'Création...' : 'Créer le compte'}</Text>
        </Pressable>
        <Pressable
          onPress={() => navigation.goBack()}
          accessibilityRole="button"
          accessibilityLabel="Retour à la connexion"
          accessibilityHint="Revient à l'écran de connexion"
        >
          <Text style={styles.back}>Retour à la connexion</Text>
        </Pressable>
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
