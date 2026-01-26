/**
 * Service Detail Screen
 * Detailed view of a service item
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function ServiceDetailScreen({ route }: any) {
  const { serviceId } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Service Details</Text>
      <Text>Service ID: {serviceId}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 16,
  },
});
