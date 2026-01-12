/**
 * Payment Methods Screen
 * Manage saved payment methods
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import {
  fetchPaymentMethods,
  deletePaymentMethod,
  setDefaultPaymentMethod,
  selectPaymentMethods,
  selectMethodsLoading,
  selectPaymentError,
  PaymentMethod,
} from '../../store/slices/paymentSlice';
import { COLORS } from '../../constants/colors';

interface PaymentMethodsScreenProps {
  navigation: any;
}

const PaymentMethodsScreen: React.FC<PaymentMethodsScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const paymentMethods = useAppSelector(selectPaymentMethods);
  const loading = useAppSelector(selectMethodsLoading);
  const error = useAppSelector(selectPaymentError);

  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    React.useCallback(() => {
      dispatch(fetchPaymentMethods());
    }, [dispatch])
  );

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    await dispatch(fetchPaymentMethods());
    setRefreshing(false);
  }, [dispatch]);

  const handleSetDefault = async (methodId: string) => {
    try {
      await dispatch(setDefaultPaymentMethod(methodId)).unwrap();
    } catch (error: any) {
      Alert.alert('Error', error || 'Failed to set default payment method');
    }
  };

  const handleDelete = (methodId: string) => {
    Alert.alert(
      'Delete Payment Method',
      'Are you sure you want to remove this payment method?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(deletePaymentMethod(methodId)).unwrap();
            } catch (error: any) {
              Alert.alert('Error', error || 'Failed to delete payment method');
            }
          },
        },
      ]
    );
  };

  const getMethodIcon = (type: string) => {
    switch (type) {
      case 'card':
        return '💳';
      case 'upi':
        return '📱';
      case 'netbanking':
        return '🏦';
      case 'wallet':
        return '👛';
      default:
        return '💰';
    }
  };

  const renderPaymentMethod = ({ item }: { item: PaymentMethod }) => (
    <View style={styles.methodCard}>
      <View style={styles.methodHeader}>
        <View style={styles.methodInfo}>
          <Text style={styles.methodIcon}>{getMethodIcon(item.type)}</Text>
          <View style={styles.methodDetails}>
            <Text style={styles.methodProvider}>{item.provider}</Text>
            <Text style={styles.methodType}>
              {item.type.toUpperCase()}
              {item.last4 && ` •••• ${item.last4}`}
              {item.upi_id && ` • ${item.upi_id}`}
            </Text>
          </View>
        </View>
        {item.is_default && (
          <View style={styles.defaultBadge}>
            <Text style={styles.defaultBadgeText}>Default</Text>
          </View>
        )}
      </View>

      <View style={styles.methodActions}>
        {!item.is_default && (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => handleSetDefault(item.id)}
          >
            <Text style={styles.actionButtonText}>Set as Default</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[styles.actionButton, styles.deleteButton]}
          onPress={() => handleDelete(item.id)}
        >
          <Text style={[styles.actionButtonText, styles.deleteButtonText]}>
            Remove
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>💳</Text>
      <Text style={styles.emptyText}>No payment methods</Text>
      <Text style={styles.emptySubtext}>
        Add a payment method to make transactions faster
      </Text>
    </View>
  );

  if (loading && !refreshing && paymentMethods.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading payment methods...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={paymentMethods}
        renderItem={renderPaymentMethod}
        keyExtractor={(item) => item.id}
        contentContainerStyle={[
          styles.listContent,
          paymentMethods.length === 0 && styles.emptyListContent,
        ]}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[COLORS.primary]}
          />
        }
      />

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => navigation.navigate('AddPaymentMethod')}
      >
        <Text style={styles.addButtonText}>+ Add Payment Method</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  listContent: {
    padding: 16,
  },
  emptyListContent: {
    flex: 1,
    justifyContent: 'center',
  },
  methodCard: {
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  methodHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  methodInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  methodIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  methodDetails: {
    flex: 1,
  },
  methodProvider: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  methodType: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  defaultBadge: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  defaultBadgeText: {
    color: COLORS.white,
    fontSize: 12,
    fontWeight: '600',
  },
  methodActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: COLORS.background,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.primary,
  },
  deleteButton: {
    backgroundColor: 'transparent',
  },
  deleteButtonText: {
    color: COLORS.error,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textLight,
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: COLORS.textLight,
  },
  addButton: {
    backgroundColor: COLORS.primary,
    margin: 16,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  addButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
});

export default PaymentMethodsScreen;
