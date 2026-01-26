/**
 * Order Detail Screen
 * Detailed view of an order
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function OrderDetailScreen({ route }: any) {
  const { orderId } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Order Details</Text>
      <Text>Order ID: {orderId}</Text>
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
