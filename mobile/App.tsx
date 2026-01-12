/**
 * LaundryConnect Mobile App
 * Main application entry point
 */

import React, { useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { store } from './src/store/store';
import AppNavigator from './src/navigation/AppNavigator';
import ErrorBoundary from './src/components/ErrorBoundary';
import notificationService from './src/utils/notificationService';
import chatService from './src/services/chatService';
import { setConnected } from './src/store/slices/chatSlice';

function AppContent() {
  const notificationListener = useRef<Notifications.EventSubscription>();
  const responseListener = useRef<Notifications.EventSubscription>();

  useEffect(() => {
    // Register for push notifications
    const setupNotifications = async () => {
      try {
        const tokenData = await notificationService.registerForPushNotifications();

        if (tokenData) {
          console.log('Push notification token:', tokenData.token);

          // Send token to backend
          const success = await notificationService.sendTokenToBackend(tokenData.token);
          if (success) {
            console.log('Token registered with backend successfully');
          }
        }
      } catch (error) {
        console.error('Error setting up notifications:', error);
      }
    };

    // Initialize chat WebSocket connection
    const setupChat = async () => {
      try {
        const token = await AsyncStorage.getItem('access_token');
        if (token) {
          await chatService.connect(token);
          store.dispatch(setConnected(true));
          console.log('Chat service connected');

          // Listen for connection changes
          chatService.onConnectionChange((connected) => {
            store.dispatch(setConnected(connected));
          });
        }
      } catch (error) {
        console.error('Error setting up chat:', error);
      }
    };

    setupNotifications();
    setupChat();

    // Register notification listeners
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('Notification received:', notification);
        // Handle notification received while app is foregrounded
      }
    );

    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('Notification tapped:', response);
        // Handle user tapping on notification
        // Can navigate to specific screen based on notification data
        const data = response.notification.request.content.data;
        if (data?.orderId) {
          // TODO: Navigate to order details screen
          console.log('Navigate to order:', data.orderId);
        }
      }
    );

    // Cleanup
    return () => {
      if (notificationListener.current) {
        notificationListener.current.remove();
      }
      if (responseListener.current) {
        responseListener.current.remove();
      }
      // Disconnect chat service
      chatService.disconnect();
    };
  }, []);

  return (
    <>
      <AppNavigator />
      <StatusBar style="auto" />
    </>
  );
}

export default function App() {
  console.log('App component rendering...');

  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <Provider store={store}>
          <AppContent />
        </Provider>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
