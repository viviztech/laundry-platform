import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import {
  fetchAddresses,
  deleteAddress,
  setDefaultAddress,
  selectAddress,
  Address,
} from '../../store/slices/addressSlice';
import { colors } from '../../constants/colors';

export default function AddressListScreen() {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { addresses, selectedAddress, isLoading } = useAppSelector((state) => state.address);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchAddresses());
  }, [dispatch]);

  const handleAddAddress = () => {
    navigation.navigate('AddAddress' as never);
  };

  const handleEditAddress = (address: Address) => {
    navigation.navigate('EditAddress' as never, { address } as never);
  };

  const handleDeleteAddress = (id: string) => {
    Alert.alert(
      'Delete Address',
      'Are you sure you want to delete this address?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            setDeletingId(id);
            try {
              await dispatch(deleteAddress(id)).unwrap();
            } catch (error: any) {
              Alert.alert('Error', error || 'Failed to delete address');
            } finally {
              setDeletingId(null);
            }
          },
        },
      ]
    );
  };

  const handleSetDefault = async (id: string) => {
    try {
      await dispatch(setDefaultAddress(id)).unwrap();
    } catch (error: any) {
      Alert.alert('Error', error || 'Failed to set default address');
    }
  };

  const handleSelectAddress = (address: Address) => {
    dispatch(selectAddress(address));
    navigation.goBack();
  };

  const renderAddressItem = ({ item }: { item: Address }) => {
    const isDeleting = deletingId === item.id;

    return (
      <TouchableOpacity
        style={[
          styles.addressCard,
          item.is_default && styles.defaultAddressCard,
        ]}
        onPress={() => handleSelectAddress(item)}
        disabled={isDeleting}
      >
        <View style={styles.addressHeader}>
          <View style={styles.labelContainer}>
            <Ionicons
              name={
                item.label.toLowerCase() === 'home'
                  ? 'home'
                  : item.label.toLowerCase() === 'work' || item.label.toLowerCase() === 'office'
                  ? 'briefcase'
                  : 'location'
              }
              size={20}
              color={item.is_default ? colors.primary : colors.textSecondary}
            />
            <Text
              style={[
                styles.labelText,
                item.is_default && styles.defaultLabelText,
              ]}
            >
              {item.label.charAt(0).toUpperCase() + item.label.slice(1)}
            </Text>
            {item.is_default && (
              <View style={styles.defaultBadge}>
                <Text style={styles.defaultBadgeText}>Default</Text>
              </View>
            )}
          </View>
          <View style={styles.actions}>
            <TouchableOpacity
              onPress={() => handleEditAddress(item)}
              style={styles.actionButton}
              disabled={isDeleting}
            >
              <Ionicons name="pencil" size={18} color={colors.primary} />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => handleDeleteAddress(item.id)}
              style={styles.actionButton}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <ActivityIndicator size="small" color={colors.error} />
              ) : (
                <Ionicons name="trash-outline" size={18} color={colors.error} />
              )}
            </TouchableOpacity>
          </View>
        </View>

        <Text style={styles.addressText}>{item.address_line1}</Text>
        {item.address_line2 && (
          <Text style={styles.addressText}>{item.address_line2}</Text>
        )}
        <Text style={styles.addressText}>
          {item.city}, {item.state} {item.pincode}
        </Text>

        {!item.is_default && (
          <TouchableOpacity
            style={styles.setDefaultButton}
            onPress={() => handleSetDefault(item.id)}
            disabled={isDeleting}
          >
            <Text style={styles.setDefaultText}>Set as Default</Text>
          </TouchableOpacity>
        )}
      </TouchableOpacity>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="location-outline" size={64} color={colors.textSecondary} />
      <Text style={styles.emptyTitle}>No Addresses</Text>
      <Text style={styles.emptyText}>
        Add your delivery addresses to get started
      </Text>
    </View>
  );

  if (isLoading && addresses.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={addresses}
        renderItem={renderAddressItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmptyState}
      />
      <TouchableOpacity style={styles.addButton} onPress={handleAddAddress}>
        <Ionicons name="add" size={24} color="#fff" />
        <Text style={styles.addButtonText}>Add New Address</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 16,
    paddingBottom: 100,
  },
  addressCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  defaultAddressCard: {
    borderColor: colors.primary,
    borderWidth: 2,
  },
  addressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  labelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  labelText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginLeft: 8,
  },
  defaultLabelText: {
    color: colors.primary,
  },
  defaultBadge: {
    backgroundColor: colors.primary,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginLeft: 8,
  },
  defaultBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    padding: 4,
  },
  addressText: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  setDefaultButton: {
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.primary,
    alignSelf: 'flex-start',
  },
  setDefaultText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: '600',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginTop: 16,
  },
  emptyText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 8,
    textAlign: 'center',
  },
  addButton: {
    position: 'absolute',
    bottom: 24,
    left: 16,
    right: 16,
    backgroundColor: colors.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});
