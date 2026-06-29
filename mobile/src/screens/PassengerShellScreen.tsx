import { NativeStackScreenProps } from '@react-navigation/native-stack';
import Feather from '@expo/vector-icons/Feather';
import { useEffect, useState } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FlatList, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { BottomTabs, TabItem } from '../components/BottomTabs';
import { FieldPill } from '../components/FieldPill';
import { MapCanvas } from '../components/MapCanvas';
import { SectionHeader } from '../components/SectionHeader';
import { savedPlaces } from '../data/places';
import { RootStackParamList } from '../navigation/RootNavigator';
import { useAuthStore } from '../store/auth';
import { useRideStore } from '../store/rides';
import { colors } from '../theme/colors';
import { formatEuro, statusLabel } from '../theme/format';

type Props = NativeStackScreenProps<RootStackParamList, 'PassengerShell'>;
type PassengerTab = 'home' | 'activity' | 'wallet' | 'account';

const tabs: TabItem<PassengerTab>[] = [
  { key: 'home', label: 'Accueil', icon: <Feather name="home" size={18} color={colors.ink} /> },
  { key: 'activity', label: 'Activite', icon: <Feather name="clock" size={18} color={colors.ink} /> },
  { key: 'wallet', label: 'Paiement', icon: <Feather name="credit-card" size={18} color={colors.ink} /> },
  { key: 'account', label: 'Compte', icon: <Feather name="user" size={18} color={colors.ink} /> },
];

export function PassengerShellScreen({ navigation }: Props) {
  const [activeTab, setActiveTab] = useState<PassengerTab>('home');
  const { rides, loadRides } = useRideStore();

  useEffect(() => {
    loadRides();
  }, [loadRides]);

  return (
    <SafeAreaView style={styles.shell} edges={['top']}>
      <View style={styles.content}>
        {activeTab === 'home' ? <PassengerHome onRide={() => navigation.navigate('RideComposer')} /> : null}
        {activeTab === 'activity' ? <PassengerActivity rides={rides} onOpen={(rideId) => navigation.navigate('ActiveRide', { rideId })} /> : null}
        {activeTab === 'wallet' ? <PassengerWallet /> : null}
        {activeTab === 'account' ? <PassengerAccount /> : null}
      </View>
      <BottomTabs tabs={tabs} active={activeTab} onChange={setActiveTab} />
    </SafeAreaView>
  );
}

function PassengerHome({ onRide }: { onRide: () => void }) {
  return (
    <View style={styles.home}>
      <MapCanvas />
      <View style={styles.sheet}>
        <Text style={styles.heroTitle}>Ou allez-vous ?</Text>
        <FieldPill title="Destination" subtitle="Rechercher une adresse" icon={<Feather name="map-pin" size={20} color={colors.ink} />} onPress={onRide} />
        <View style={styles.shortcuts}>
          <FieldPill title="Travail" subtitle="12 min" icon={<Feather name="briefcase" size={18} color={colors.ink} />} onPress={onRide} />
          <FieldPill title="Maison" subtitle="16 min" icon={<Feather name="home" size={18} color={colors.ink} />} onPress={onRide} />
        </View>
        <SectionHeader title="Adresses recentes" />
        {savedPlaces.map((place) => (
          <Pressable key={place.id} onPress={onRide} style={styles.placeRow}>
            <View style={styles.dot} />
            <View style={styles.placeText}>
              <Text style={styles.placeTitle}>{place.label}</Text>
              <Text style={styles.placeAddress}>{place.address}</Text>
            </View>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

function PassengerActivity({ rides, onOpen }: { rides: ReturnType<typeof useRideStore.getState>['rides']; onOpen: (rideId: number) => void }) {
  return (
    <View style={styles.page}>
      <Text style={styles.pageTitle}>Activite</Text>
      <FlatList
        data={rides}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>Aucune course pour le moment.</Text>}
        renderItem={({ item }) => (
          <Pressable onPress={() => onOpen(item.id)} style={styles.rowCard}>
            <View style={styles.routeIcon}><Feather name="map-pin" size={18} color={colors.surface} /></View>
            <View style={styles.rowBody}>
              <Text style={styles.rowTitle}>{item.dropoff_label}</Text>
              <Text style={styles.rowMeta}>{statusLabel(item.status)} - {item.pickup_label}</Text>
            </View>
            <Text style={styles.price}>{formatEuro(item.final_fare_cents || item.estimated_fare_cents)}</Text>
          </Pressable>
        )}
      />
    </View>
  );
}

function PassengerWallet() {
  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.pageTitle}>Paiement</Text>
      <View style={styles.blackCard}>
        <Text style={styles.blackCardLabel}>Solde FleetPro</Text>
        <Text style={styles.blackCardValue}>0.00 EUR</Text>
      </View>
      <SectionHeader title="Moyens de paiement" action="Ajouter" />
      <View style={styles.rowCard}>
        <Feather name="credit-card" size={22} color={colors.ink} />
        <View style={styles.rowBody}>
          <Text style={styles.rowTitle}>Carte test Stripe</Text>
          <Text style={styles.rowMeta}>4242 4242 4242 4242</Text>
        </View>
      </View>
      <SectionHeader title="Promotions" />
      <View style={styles.rowCard}>
        <View style={styles.promoBadge}><Text style={styles.promoText}>15%</Text></View>
        <View style={styles.rowBody}>
          <Text style={styles.rowTitle}>Commission transparente</Text>
          <Text style={styles.rowMeta}>La plateforme garde 15%, le reste revient au chauffeur.</Text>
        </View>
      </View>
    </ScrollView>
  );
}

function PassengerAccount() {
  const { username, logout } = useAuthStore();

  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.pageTitle}>Compte</Text>
      <View style={styles.profileHeader}>
        <View style={styles.avatar}><Text style={styles.avatarText}>{username.slice(0, 1).toUpperCase()}</Text></View>
        <View>
          <Text style={styles.profileName}>{username}</Text>
          <Text style={styles.rowMeta}>Passager FleetPro</Text>
        </View>
      </View>
      {['Messages', 'Securite', 'Confidentialite', 'Aide'].map((item) => (
        <View key={item} style={styles.rowCard}>
          <Text style={styles.rowTitle}>{item}</Text>
        </View>
      ))}
      <Pressable onPress={logout} style={styles.logout}>
        <Text style={styles.logoutText}>Se deconnecter</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  shell: { flex: 1, backgroundColor: colors.background },
  content: { flex: 1 },
  home: { flex: 1 },
  sheet: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: colors.surface,
    borderTopLeftRadius: 8,
    borderTopRightRadius: 8,
    padding: 18,
    gap: 14,
  },
  heroTitle: { color: colors.ink, fontSize: 28, fontWeight: '900' },
  shortcuts: { flexDirection: 'row', gap: 10 },
  placeRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 9 },
  dot: { width: 9, height: 9, borderRadius: 5, backgroundColor: colors.ink },
  placeText: { flex: 1 },
  placeTitle: { color: colors.ink, fontWeight: '800' },
  placeAddress: { color: colors.muted, marginTop: 2 },
  page: { flex: 1, backgroundColor: colors.background, padding: 18 },
  pageTitle: { color: colors.ink, fontSize: 32, fontWeight: '900', marginBottom: 18 },
  list: { gap: 10, paddingBottom: 24 },
  empty: { color: colors.muted },
  rowCard: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.line,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  routeIcon: { width: 38, height: 38, borderRadius: 8, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  rowBody: { flex: 1 },
  rowTitle: { color: colors.ink, fontWeight: '800', fontSize: 16 },
  rowMeta: { color: colors.muted, marginTop: 3 },
  price: { color: colors.ink, fontWeight: '900' },
  scrollContent: { gap: 14, paddingBottom: 28 },
  blackCard: { backgroundColor: colors.ink, borderRadius: 8, padding: 18 },
  blackCardLabel: { color: '#c7c7c7', fontWeight: '700' },
  blackCardValue: { color: colors.surface, fontSize: 34, fontWeight: '900', marginTop: 8 },
  promoBadge: { width: 44, height: 44, borderRadius: 8, backgroundColor: colors.softAccent, alignItems: 'center', justifyContent: 'center' },
  promoText: { color: colors.ink, fontWeight: '900' },
  profileHeader: { flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 8 },
  avatar: { width: 58, height: 58, borderRadius: 8, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: colors.surface, fontSize: 24, fontWeight: '900' },
  profileName: { color: colors.ink, fontWeight: '900', fontSize: 22 },
  logout: { backgroundColor: colors.softAccent, borderRadius: 8, minHeight: 50, alignItems: 'center', justifyContent: 'center' },
  logoutText: { color: colors.ink, fontWeight: '800' },
});
