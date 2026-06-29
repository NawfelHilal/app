import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useEffect } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { useAuthStore } from '../store/auth';
import { ActiveRideScreen } from '../screens/ActiveRideScreen';
import { DriverShellScreen } from '../screens/DriverShellScreen';
import { LoginScreen } from '../screens/LoginScreen';
import { PassengerShellScreen } from '../screens/PassengerShellScreen';
import { RideComposerScreen } from '../screens/RideComposerScreen';
import { RegisterScreen } from '../screens/RegisterScreen';

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  PassengerShell: undefined;
  DriverShell: undefined;
  RideComposer: undefined;
  ActiveRide: { rideId: number };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootNavigator() {
  const role = useAuthStore((state) => state.role);
  const isLoggedIn = useAuthStore((state) => Boolean(state.accessToken));
  const initialized = useAuthStore((state) => state.initialized);
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  if (!initialized) {
    return <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><ActivityIndicator /></View>;
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isLoggedIn ? (
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
        </>
      ) : role === 'DRIVER' ? (
        <Stack.Screen name="DriverShell" component={DriverShellScreen} />
      ) : (
        <Stack.Screen name="PassengerShell" component={PassengerShellScreen} />
      )}
      <Stack.Screen name="RideComposer" component={RideComposerScreen} />
      <Stack.Screen name="ActiveRide" component={ActiveRideScreen} />
    </Stack.Navigator>
  );
}
