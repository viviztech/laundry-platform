/**
 * Wallet Screen
 * Display wallet balance and transaction history
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
  TextInput,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import {
  fetchWallet,
  fetchTransactions,
  addMoneyToWallet,
  selectWallet,
  selectTransactions,
  selectWalletLoading,
  selectPaymentError,
  Transaction,
} from '../../store/slices/paymentSlice';
import { COLORS } from '../../constants/colors';

interface WalletScreenProps {
  navigation: any;
}

const WalletScreen: React.FC<WalletScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const wallet = useAppSelector(selectWallet);
  const transactions = useAppSelector(selectTransactions);
  const loading = useAppSelector(selectWalletLoading);
  const error = useAppSelector(selectPaymentError);

  const [refreshing, setRefreshing] = useState(false);
  const [showAddMoney, setShowAddMoney] = useState(false);
  const [amount, setAmount] = useState('');

  useFocusEffect(
    React.useCallback(() => {
      dispatch(fetchWallet());
      dispatch(fetchTransactions());
    }, [dispatch])
  );

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    await Promise.all([
      dispatch(fetchWallet()),
      dispatch(fetchTransactions()),
    ]);
    setRefreshing(false);
  }, [dispatch]);

  const handleAddMoney = async () => {
    const amountValue = parseFloat(amount);
    if (isNaN(amountValue) || amountValue <= 0) {
      Alert.alert('Invalid Amount', 'Please enter a valid amount');
      return;
    }

    if (amountValue < 10) {
      Alert.alert('Minimum Amount', 'Minimum amount to add is ₹10');
      return;
    }

    if (amountValue > 10000) {
      Alert.alert('Maximum Amount', 'Maximum amount to add is ₹10,000');
      return;
    }

    try {
      const result = await dispatch(addMoneyToWallet({ amount: amountValue })).unwrap();

      // Navigate to payment gateway to complete transaction
      if (result.payment_url) {
        navigation.navigate('PaymentGateway', {
          url: result.payment_url,
          transactionId: result.transaction_id,
          amount: amountValue,
          type: 'wallet_topup',
        });
      }

      setAmount('');
      setShowAddMoney(false);
    } catch (error: any) {
      Alert.alert('Error', error || 'Failed to initiate payment');
    }
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'credit':
        return '💰';
      case 'debit':
        return '💸';
      case 'refund':
        return '↩️';
      default:
        return '💳';
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'credit':
      case 'refund':
        return COLORS.success;
      case 'debit':
        return COLORS.error;
      default:
        return COLORS.text;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    }
  };

  const renderTransaction = ({ item }: { item: Transaction }) => (
    <View style={styles.transactionCard}>
      <View style={styles.transactionHeader}>
        <View style={styles.transactionInfo}>
          <Text style={styles.transactionIcon}>{getTransactionIcon(item.type)}</Text>
          <View style={styles.transactionDetails}>
            <Text style={styles.transactionDescription}>{item.description}</Text>
            <Text style={styles.transactionDate}>{formatDate(item.created_at)}</Text>
          </View>
        </View>
        <View style={styles.transactionAmount}>
          <Text
            style={[
              styles.amountText,
              { color: getTransactionColor(item.type) },
            ]}
          >
            {item.type === 'credit' || item.type === 'refund' ? '+' : '-'}₹
            {item.amount.toFixed(2)}
          </Text>
          <Text style={styles.statusBadge}>{item.status}</Text>
        </View>
      </View>
      {item.order_id && (
        <TouchableOpacity
          style={styles.viewOrderButton}
          onPress={() => navigation.navigate('OrderDetail', { orderId: item.order_id })}
        >
          <Text style={styles.viewOrderText}>View Order</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>💰</Text>
      <Text style={styles.emptyText}>No transactions yet</Text>
      <Text style={styles.emptySubtext}>
        Your wallet transactions will appear here
      </Text>
    </View>
  );

  const renderHeader = () => (
    <View style={styles.walletCard}>
      <Text style={styles.walletLabel}>Wallet Balance</Text>
      <Text style={styles.walletBalance}>
        ₹{wallet?.balance.toFixed(2) || '0.00'}
      </Text>

      {showAddMoney ? (
        <View style={styles.addMoneyContainer}>
          <Text style={styles.addMoneyLabel}>Enter amount to add</Text>
          <TextInput
            style={styles.amountInput}
            placeholder="Enter amount"
            value={amount}
            onChangeText={setAmount}
            keyboardType="numeric"
            autoFocus
          />
          <View style={styles.quickAmountButtons}>
            {[100, 500, 1000, 2000].map((quickAmount) => (
              <TouchableOpacity
                key={quickAmount}
                style={styles.quickAmountButton}
                onPress={() => setAmount(quickAmount.toString())}
              >
                <Text style={styles.quickAmountText}>₹{quickAmount}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={() => {
                setShowAddMoney(false);
                setAmount('');
              }}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, styles.addButton]}
              onPress={handleAddMoney}
            >
              <Text style={styles.addButtonText}>Add Money</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <TouchableOpacity
          style={styles.addMoneyButton}
          onPress={() => setShowAddMoney(true)}
        >
          <Text style={styles.addMoneyButtonText}>+ Add Money</Text>
        </TouchableOpacity>
      )}

      <View style={styles.walletInfo}>
        <View style={styles.infoItem}>
          <Text style={styles.infoIcon}>💸</Text>
          <View>
            <Text style={styles.infoLabel}>Cashback</Text>
            <Text style={styles.infoValue}>₹{wallet?.cashback || '0.00'}</Text>
          </View>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoIcon}>🎁</Text>
          <View>
            <Text style={styles.infoLabel}>Rewards</Text>
            <Text style={styles.infoValue}>₹{wallet?.rewards || '0.00'}</Text>
          </View>
        </View>
      </View>
    </View>
  );

  if (loading && !refreshing && !wallet) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading wallet...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={transactions}
        renderItem={renderTransaction}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={[
          styles.listContent,
          transactions.length === 0 && styles.emptyListContent,
        ]}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[COLORS.primary]}
          />
        }
      />
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
  },
  walletCard: {
    backgroundColor: COLORS.primary,
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
  walletLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 8,
  },
  walletBalance: {
    fontSize: 36,
    fontWeight: 'bold',
    color: COLORS.white,
    marginBottom: 20,
  },
  addMoneyButton: {
    backgroundColor: COLORS.white,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  addMoneyButtonText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  addMoneyContainer: {
    marginBottom: 20,
  },
  addMoneyLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: 12,
  },
  amountInput: {
    backgroundColor: COLORS.white,
    borderRadius: 8,
    padding: 12,
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  quickAmountButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  quickAmountButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  quickAmountText: {
    color: COLORS.white,
    fontSize: 14,
    fontWeight: '600',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  cancelButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  addButton: {
    backgroundColor: COLORS.white,
  },
  addButtonText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  walletInfo: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  infoIcon: {
    fontSize: 24,
  },
  infoLabel: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.white,
  },
  transactionCard: {
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
  transactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  transactionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  transactionIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  transactionDetails: {
    flex: 1,
  },
  transactionDescription: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  transactionAmount: {
    alignItems: 'flex-end',
  },
  amountText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statusBadge: {
    fontSize: 12,
    color: COLORS.textLight,
    textTransform: 'capitalize',
  },
  viewOrderButton: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: COLORS.background,
  },
  viewOrderText: {
    fontSize: 14,
    color: COLORS.primary,
    fontWeight: '600',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
    marginTop: 40,
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
});

export default WalletScreen;
