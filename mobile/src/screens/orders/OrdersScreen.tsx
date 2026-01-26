/**
 * Orders Screen
 * List of user's orders
 */

import React, { useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import { fetchOrders } from '../../store/slices/ordersSlice';

export default function OrdersScreen({ navigation }: any) {
  const dispatch = useAppDispatch();
  const { orders, isLoading } = useAppSelector((state) => state.orders);

  useEffect(() => {
    dispatch(fetchOrders());
  }, []);

  const renderOrder = ({ item }: any) => (
    <TouchableOpacity
      style={styles.orderCard}
      onPress={() => navigation.navigate('OrderDetail', { orderId: item.id })}>
      <View>
        <Text style={styles.orderNumber}>#{item.order_number}</Text>
        <Text style={styles.orderDate}>
          {new Date(item.created_at).toLocaleDateString()}
        </Text>
        <Text style={styles.orderStatus}>{item.status.replace('_', ' ')}</Text>
      </View>
      <Text style={styles.orderAmount}>₹{item.total.toFixed(2)}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Orders</Text>
      <FlatList
        data={orders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No orders yet</Text>
          </View>
        }
      />
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
  list: {
    paddingBottom: 16,
  },
  orderCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 2,
  },
  orderNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: '#212121',
    marginBottom: 4,
  },
  orderDate: {
    fontSize: 12,
    color: '#9E9E9E',
    marginBottom: 4,
  },
  orderStatus: {
    fontSize: 14,
    color: '#757575',
    textTransform: 'capitalize',
  },
  orderAmount: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2196F3',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#9E9E9E',
  },
});
