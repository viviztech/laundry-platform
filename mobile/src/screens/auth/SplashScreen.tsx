/**
 * Splash Screen
 * Displayed while app is loading
 */

import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

export default function SplashScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>LaundryConnect</Text>
      <Text style={styles.subtitle}>Your Laundry, Our Priority</Text>
      <ActivityIndicator size="large" color="#2196F3" style={styles.loader} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#757575',
    marginBottom: 40,
  },
  loader: {
    marginTop: 20,
  },
});
