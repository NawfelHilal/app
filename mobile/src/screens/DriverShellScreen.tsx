import * as Location from 'expo-location';
import Feather from '@expo/vector-icons/Feather';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Alert, FlatList, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getGpsSocket } from '../api/gps';
import { BottomTabs, TabItem } from '../components/BottomTabs';
import { MapCanvas } from '../components/MapCanvas';
import { SectionHeader } from '../components/SectionHeader';
import { RootStackParamList } from '../navigation/RootNavigator';
import { useAuthStore } from '../store/auth';
import { useRideStore } from '../store/rides';
import { colors } from '../theme/colors';
import { formatEuro, statusLabel } from '../theme/format';

type DriverTab = 'drive' | 'requests' | 'earnings' | 'account';
type Props = Readonly<NativeStackScreenProps<RootStackParamList, 'DriverShell'>>;

const tabs: TabItem<DriverTab>[] = [
  { key: 'drive', label: 'Accueil', icon: <Feather name="navigation" size={18} color={colors.ink} /> },
  { key: 'requests', label: 'Courses', icon: <Feather name="clock" size={18} color={colors.ink} /> },
  { key: 'earnings', label: 'Gains', icon: <Feather name="bar-chart-2" size={18} color={colors.ink} /> },
  { key: 'account', label: 'Compte', icon: <Feather name="user" size={18} color={colors.ink} /> },
];

export function DriverShellScreen({ navigation }: Props) {
  const [activeTab, setActiveTab] = useState<DriverTab>('drive');
  const [online, setOnline] = useState(false);
  const { rides, loadRides, acceptRide, simulateNearbyRequest } = useRideStore();
  const tracking = useRef<Location.LocationSubscription | undefined>(undefined);
  const activeRideId = rides.find((ride) => ride.status === 'ACCEPTED' || ride.status === 'IN_PROGRESS')?.id;
  const activeRideIdRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    loadRides();
  }, [loadRides]);

  useEffect(() => {
    activeRideIdRef.current = activeRideId;
    if (activeRideId) {
      getGpsSocket()?.emit('ride:join', { rideId: activeRideId });
    }
  }, [activeRideId]);

  useEffect(() => () => tracking.current?.remove(), []);

  useEffect(() => {
    if (!online) {
      return undefined;
    }
    const timer = setInterval(() => loadRides().catch(() => undefined), 10000);
    return () => clearInterval(timer);
  }, [loadRides, online]);

  async function toggleOnline() {
    if (online) {
      tracking.current?.remove();
      tracking.current = undefined;
      setOnline(false);
      return;
    }

    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('GPS bloque', 'Autorise la localisation pour passer en ligne.');
      return;
    }

    const socket = getGpsSocket();
    if (!socket) {
      Alert.alert('GPS indisponible', 'Reconnecte-toi avant de passer en ligne.');
      return;
    }

    const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
    await emitPosition(socket, location, activeRideIdRef.current);
    tracking.current = await Location.watchPositionAsync(
      { accuracy: Location.Accuracy.High, distanceInterval: 10, timeInterval: 5000 },
      (nextLocation) => {
        emitPosition(socket, nextLocation, activeRideIdRef.current).catch(() => undefined);
      },
    );
    setOnline(true);
    await loadRides();
  }

  return (
    <SafeAreaView style={styles.shell} edges={['top']}>
      <View style={styles.content}>
        {activeTab === 'drive' ? (
          <DriverHome
            online={online}
            rides={rides}
            onToggleOnline={toggleOnline}
            onSimulateNearbyRequest={async () => {
              try {
                await simulateNearbyRequest();
                await loadRides();
                setActiveTab('requests');
              } catch {
                Alert.alert('Simulation impossible', 'Vérifie que le mode démo backend est activé.');
              }
            }}
            onOpenRide={(rideId) => navigation.navigate('ActiveRide', { rideId })}
          />
        ) : null}
        {activeTab === 'requests' ? (
          <DriverRequests
            rides={rides}
            onAccept={async (rideId) => {
              const ride = await acceptRide(rideId);
              navigation.navigate('ActiveRide', { rideId: ride.id });
            }}
            onOpenRide={(rideId) => navigation.navigate('ActiveRide', { rideId })}
          />
        ) : null}
        {activeTab === 'earnings' ? <DriverEarnings rides={rides} /> : null}
        {activeTab === 'account' ? <DriverAccount /> : null}
      </View>
      <BottomTabs tabs={tabs} active={activeTab} onChange={setActiveTab} />
    </SafeAreaView>
  );
}

function emitPosition(socket: NonNullable<ReturnType<typeof getGpsSocket>>, location: Location.LocationObject, rideId?: number): Promise<void> {
  return new Promise((resolve) => {
    socket.emit('driver:position', {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      heading: location.coords.heading,
      speed: location.coords.speed,
      rideId,
    }, () => resolve());
  });
}

function DriverHome({
  online,
  rides,
  onToggleOnline,
  onSimulateNearbyRequest,
  onOpenRide,
}: {
  online: boolean;
  rides: ReturnType<typeof useRideStore.getState>['rides'];
  onToggleOnline: () => void;
  onSimulateNearbyRequest: () => Promise<void>;
  onOpenRide: (rideId: number) => void;
}) {
  const activeRide = rides.find((ride) => ride.status === 'ACCEPTED' || ride.status === 'IN_PROGRESS');
  const demoSimulationEnabled = process.env.EXPO_PUBLIC_ENABLE_DEMO_SIMULATION === 'true';

  return (
    <View style={styles.home}>
      <MapCanvas ride={activeRide} />
      <View style={styles.sheet}>
        <View style={styles.statusRow}>
          <View>
            <Text style={styles.heroTitle}>{online ? 'Vous etes en ligne' : 'Vous etes hors ligne'}</Text>
            <Text style={styles.muted}>{online ? 'Les demandes proches peuvent arriver.' : 'Passez en ligne pour recevoir des courses.'}</Text>
          </View>
          <Pressable
            onPress={onToggleOnline}
            accessibilityRole="switch"
            accessibilityLabel="Disponibilité chauffeur"
            accessibilityHint={online ? 'Passe hors ligne et arrête le partage GPS' : 'Passe en ligne et active le partage GPS'}
            accessibilityState={{ checked: online }}
            style={[styles.powerButton, online && styles.powerButtonOn]}
          >
            <Feather name="power" size={24} color={colors.surface} />
          </Pressable>
        </View>
        <View style={styles.statsGrid}>
          <DriverStat label="Temps" value="0h42" />
          <DriverStat label="Courses" value="3" />
          <DriverStat label="Note" value="5.0" />
        </View>
        {demoSimulationEnabled ? (
          <Pressable
            onPress={onSimulateNearbyRequest}
            accessibilityRole="button"
            accessibilityLabel="Simuler une demande client proche"
            accessibilityHint="Crée une course démo proche pour vérifier le matching chauffeur"
            style={styles.demoButton}
          >
            <Feather name="plus-circle" size={18} color={colors.surface} />
            <Text style={styles.demoButtonText}>Simuler une demande client proche</Text>
          </Pressable>
        ) : null}
        {activeRide ? (
          <Pressable
            onPress={() => onOpenRide(activeRide.id)}
            accessibilityRole="button"
            accessibilityLabel={`Course active ${statusLabel(activeRide.status)}`}
            accessibilityHint={`${activeRide.pickup_label} vers ${activeRide.dropoff_label}`}
            style={styles.activeRideCard}
          >
            <View style={styles.rowBody}>
              <Text style={styles.cardTitle}>{statusLabel(activeRide.status)}</Text>
              <Text style={styles.muted}>{activeRide.pickup_label} vers {activeRide.dropoff_label}</Text>
            </View>
            <Feather name="chevron-right" size={22} color={colors.ink} />
          </Pressable>
        ) : null}
      </View>
    </View>
  );
}

function DriverRequests({
  rides,
  onAccept,
  onOpenRide,
}: {
  rides: ReturnType<typeof useRideStore.getState>['rides'];
  onAccept: (rideId: number) => Promise<void>;
  onOpenRide: (rideId: number) => void;
}) {
  const available = rides.filter((ride) => ride.status === 'REQUESTED');
  const active = rides.filter((ride) => ride.status === 'ACCEPTED' || ride.status === 'IN_PROGRESS');

  return (
    <View style={styles.page}>
      <Text style={styles.pageTitle}>Courses</Text>
      <FlatList
        data={[...active, ...available]}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.muted}>Aucune demande disponible.</Text>}
        renderItem={({ item }) => (
          <Pressable
            onPress={() => item.status === 'REQUESTED' ? undefined : onOpenRide(item.id)}
            accessibilityRole="button"
            accessibilityLabel={`Course ${statusLabel(item.status)} vers ${item.dropoff_label}`}
            accessibilityHint={`Départ ${item.pickup_label}, gain chauffeur ${formatEuro(item.driver_earnings_cents)}`}
            style={styles.requestCard}
          >
            <View style={styles.routeLine}>
              <Feather name="map-pin" size={20} color={colors.ink} />
              <View style={styles.routeBody}>
                <Text style={styles.cardTitle}>{item.pickup_label}</Text>
                <Text style={styles.muted}>{statusLabel(item.status)} vers {item.dropoff_label}</Text>
              </View>
            </View>
            <View style={styles.requestFooter}>
              <View>
                <Text style={styles.earning}>{formatEuro(item.driver_earnings_cents)}</Text>
                <Text style={styles.muted}>apres commission 15%</Text>
              </View>
              {item.status === 'REQUESTED' ? (
                <Pressable
                  onPress={() => onAccept(item.id)}
                  accessibilityRole="button"
                  accessibilityLabel="Accepter la course"
                  accessibilityHint={`Accepte la course vers ${item.dropoff_label}`}
                  style={styles.acceptButton}
                >
                  <Text style={styles.acceptText}>Accepter</Text>
                </Pressable>
              ) : (
                <Pressable
                  onPress={() => onOpenRide(item.id)}
                  accessibilityRole="button"
                  accessibilityLabel="Continuer la course"
                  accessibilityHint={`Ouvre le suivi vers ${item.dropoff_label}`}
                  style={styles.acceptButton}
                >
                  <Text style={styles.acceptText}>Continuer</Text>
                </Pressable>
              )}
            </View>
          </Pressable>
        )}
      />
    </View>
  );
}

function DriverEarnings({ rides }: { rides: ReturnType<typeof useRideStore.getState>['rides'] }) {
  const totals = useMemo(() => {
    const completed = rides.filter((ride) => ride.status === 'COMPLETED' || ride.status === 'ACCEPTED' || ride.status === 'IN_PROGRESS');
    return completed.reduce((sum, ride) => sum + ride.driver_earnings_cents, 0);
  }, [rides]);

  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.pageTitle}>Gains</Text>
      <View style={styles.blackCard}>
        <Text style={styles.blackCardLabel}>Aujourd'hui</Text>
        <Text style={styles.blackCardValue}>{formatEuro(totals)}</Text>
      </View>
      <View style={styles.statsGrid}>
        <DriverStat label="Net course" value="85%" />
        <DriverStat label="Commission" value="15%" />
        <DriverStat label="Versement" value="Test" />
      </View>
      <SectionHeader title="Dernieres courses" />
      {rides.slice(0, 4).map((ride) => (
        <View key={ride.id} style={styles.rowCard}>
          <View style={styles.rowBody}>
            <Text style={styles.cardTitle}>{ride.dropoff_label}</Text>
            <Text style={styles.muted}>{statusLabel(ride.status)}</Text>
          </View>
          <Text style={styles.earning}>{formatEuro(ride.driver_earnings_cents)}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

function DriverAccount() {
  const { username, logout } = useAuthStore();

  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.pageTitle}>Compte</Text>
      <View style={styles.profileHeader}>
        <View style={styles.avatar}><Text style={styles.avatarText}>{username.slice(0, 1).toUpperCase()}</Text></View>
        <View>
          <Text style={styles.profileName}>{username}</Text>
          <Text style={styles.muted}>Chauffeur partenaire</Text>
        </View>
      </View>
      {['Documents', 'Vehicule', 'Revenus', 'Aide chauffeur'].map((item) => (
        <View key={item} style={styles.rowCard}>
          <Text style={styles.cardTitle}>{item}</Text>
        </View>
      ))}
      <Pressable
        onPress={logout}
        accessibilityRole="button"
        accessibilityLabel="Se déconnecter"
        accessibilityHint="Ferme la session chauffeur"
        style={styles.logout}
      >
        <Text style={styles.logoutText}>Se deconnecter</Text>
      </Pressable>
    </ScrollView>
  );
}

function DriverStat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
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
    gap: 16,
  },
  statusRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 14 },
  heroTitle: { color: colors.ink, fontSize: 26, fontWeight: '900' },
  muted: { color: colors.muted, marginTop: 3 },
  powerButton: { width: 58, height: 58, borderRadius: 8, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  powerButtonOn: { backgroundColor: colors.success },
  statsGrid: { flexDirection: 'row', gap: 10 },
  stat: { flex: 1, backgroundColor: colors.softAccent, borderRadius: 8, padding: 14 },
  statValue: { color: colors.ink, fontWeight: '900', fontSize: 20 },
  statLabel: { color: colors.muted, marginTop: 4, fontWeight: '700' },
  demoButton: { backgroundColor: colors.ink, borderRadius: 8, padding: 14, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 },
  demoButtonText: { color: colors.surface, fontWeight: '900' },
  activeRideCard: { backgroundColor: colors.softAccent, borderRadius: 8, padding: 14, flexDirection: 'row', alignItems: 'center', gap: 12 },
  page: { flex: 1, backgroundColor: colors.background, padding: 18 },
  pageTitle: { color: colors.ink, fontSize: 32, fontWeight: '900', marginBottom: 18 },
  list: { gap: 12, paddingBottom: 24 },
  requestCard: { backgroundColor: colors.surface, borderRadius: 8, padding: 16, borderWidth: 1, borderColor: colors.line, gap: 18 },
  routeLine: { flexDirection: 'row', gap: 12 },
  routeBody: { flex: 1 },
  cardTitle: { color: colors.ink, fontWeight: '900', fontSize: 16 },
  requestFooter: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 14 },
  earning: { color: colors.ink, fontWeight: '900', fontSize: 17 },
  acceptButton: { backgroundColor: colors.ink, borderRadius: 8, minHeight: 44, paddingHorizontal: 18, alignItems: 'center', justifyContent: 'center' },
  acceptText: { color: colors.surface, fontWeight: '900' },
  scrollContent: { gap: 14, paddingBottom: 28 },
  blackCard: { backgroundColor: colors.ink, borderRadius: 8, padding: 18 },
  blackCardLabel: { color: '#c7c7c7', fontWeight: '700' },
  blackCardValue: { color: colors.surface, fontSize: 34, fontWeight: '900', marginTop: 8 },
  rowCard: { backgroundColor: colors.surface, borderRadius: 8, padding: 14, borderWidth: 1, borderColor: colors.line, flexDirection: 'row', alignItems: 'center', gap: 12 },
  rowBody: { flex: 1 },
  profileHeader: { flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 8 },
  avatar: { width: 58, height: 58, borderRadius: 8, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: colors.surface, fontSize: 24, fontWeight: '900' },
  profileName: { color: colors.ink, fontWeight: '900', fontSize: 22 },
  logout: { backgroundColor: colors.softAccent, borderRadius: 8, minHeight: 50, alignItems: 'center', justifyContent: 'center' },
  logoutText: { color: colors.ink, fontWeight: '800' },
});
