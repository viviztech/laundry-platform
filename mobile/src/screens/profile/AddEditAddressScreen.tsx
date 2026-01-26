import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import { createAddress, updateAddress, Address } from '../../store/slices/addressSlice';
import { colors } from '../../constants/colors';

const ADDRESS_LABELS = ['Home', 'Work', 'Other'];

export default function AddEditAddressScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const dispatch = useAppDispatch();
  const { isLoading } = useAppSelector((state) => state.address);

  // Check if we're editing an existing address
  const editingAddress = (route.params as any)?.address as Address | undefined;
  const isEditing = !!editingAddress;

  const [label, setLabel] = useState(editingAddress?.label || 'Home');
  const [addressLine1, setAddressLine1] = useState(editingAddress?.address_line1 || '');
  const [addressLine2, setAddressLine2] = useState(editingAddress?.address_line2 || '');
  const [city, setCity] = useState(editingAddress?.city || '');
  const [state, setState] = useState(editingAddress?.state || '');
  const [pincode, setPincode] = useState(editingAddress?.pincode || '');
  const [isDefault, setIsDefault] = useState(editingAddress?.is_default || false);

  useEffect(() => {
    navigation.setOptions({
      title: isEditing ? 'Edit Address' : 'Add Address',
    });
  }, [isEditing, navigation]);

  const validateForm = () => {
    if (!addressLine1.trim()) {
      Alert.alert('Error', 'Address Line 1 is required');
      return false;
    }
    if (!city.trim()) {
      Alert.alert('Error', 'City is required');
      return false;
    }
    if (!state.trim()) {
      Alert.alert('Error', 'State is required');
      return false;
    }
    if (!pincode.trim()) {
      Alert.alert('Error', 'PIN code is required');
      return false;
    }
    if (!/^\d{6}$/.test(pincode.trim())) {
      Alert.alert('Error', 'Please enter a valid 6-digit PIN code');
      return false;
    }
    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    const addressData = {
      label: label.toLowerCase(),
      address_line1: addressLine1.trim(),
      address_line2: addressLine2.trim() || undefined,
      city: city.trim(),
      state: state.trim(),
      pincode: pincode.trim(),
      is_default: isDefault,
    };

    try {
      if (isEditing && editingAddress) {
        await dispatch(updateAddress({ id: editingAddress.id, data: addressData })).unwrap();
        Alert.alert('Success', 'Address updated successfully');
      } else {
        await dispatch(createAddress(addressData)).unwrap();
        Alert.alert('Success', 'Address added successfully');
      }
      navigation.goBack();
    } catch (error: any) {
      Alert.alert('Error', error || `Failed to ${isEditing ? 'update' : 'add'} address`);
    }
  };

  const handleUseCurrentLocation = () => {
    Alert.alert(
      'Current Location',
      'Location feature will be available in the next update',
      [{ text: 'OK' }]
    );
    // TODO: Implement location picker with map
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Address Label Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Address Type</Text>
          <View style={styles.labelButtons}>
            {ADDRESS_LABELS.map((labelOption) => (
              <TouchableOpacity
                key={labelOption}
                style={[
                  styles.labelButton,
                  label === labelOption && styles.labelButtonActive,
                ]}
                onPress={() => setLabel(labelOption)}
              >
                <Ionicons
                  name={
                    labelOption === 'Home'
                      ? 'home'
                      : labelOption === 'Work'
                      ? 'briefcase'
                      : 'location'
                  }
                  size={20}
                  color={label === labelOption ? '#fff' : colors.textSecondary}
                />
                <Text
                  style={[
                    styles.labelButtonText,
                    label === labelOption && styles.labelButtonTextActive,
                  ]}
                >
                  {labelOption}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Location Button */}
        <TouchableOpacity
          style={styles.locationButton}
          onPress={handleUseCurrentLocation}
        >
          <Ionicons name="locate" size={20} color={colors.primary} />
          <Text style={styles.locationButtonText}>Use Current Location</Text>
        </TouchableOpacity>

        {/* Address Fields */}
        <View style={styles.section}>
          <Text style={styles.label}>Address Line 1 *</Text>
          <TextInput
            style={styles.input}
            value={addressLine1}
            onChangeText={setAddressLine1}
            placeholder="House/Flat No, Building Name"
            placeholderTextColor={colors.textSecondary}
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Address Line 2</Text>
          <TextInput
            style={styles.input}
            value={addressLine2}
            onChangeText={setAddressLine2}
            placeholder="Area, Street, Sector (Optional)"
            placeholderTextColor={colors.textSecondary}
          />
        </View>

        <View style={styles.row}>
          <View style={[styles.section, styles.halfWidth]}>
            <Text style={styles.label}>City *</Text>
            <TextInput
              style={styles.input}
              value={city}
              onChangeText={setCity}
              placeholder="City"
              placeholderTextColor={colors.textSecondary}
            />
          </View>

          <View style={[styles.section, styles.halfWidth]}>
            <Text style={styles.label}>State *</Text>
            <TextInput
              style={styles.input}
              value={state}
              onChangeText={setState}
              placeholder="State"
              placeholderTextColor={colors.textSecondary}
            />
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>PIN Code *</Text>
          <TextInput
            style={styles.input}
            value={pincode}
            onChangeText={setPincode}
            placeholder="6-digit PIN code"
            placeholderTextColor={colors.textSecondary}
            keyboardType="number-pad"
            maxLength={6}
          />
        </View>

        {/* Default Address Toggle */}
        <TouchableOpacity
          style={styles.defaultToggle}
          onPress={() => setIsDefault(!isDefault)}
        >
          <View style={styles.defaultToggleLeft}>
            <Ionicons
              name={isDefault ? 'checkbox' : 'square-outline'}
              size={24}
              color={isDefault ? colors.primary : colors.textSecondary}
            />
            <Text style={styles.defaultToggleText}>Set as default address</Text>
          </View>
        </TouchableOpacity>
      </ScrollView>

      {/* Save Button */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.saveButtonText}>
              {isEditing ? 'Update Address' : 'Save Address'}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingBottom: 100,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 12,
  },
  labelButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  labelButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: colors.border,
  },
  labelButtonActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  labelButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
    marginLeft: 8,
  },
  labelButtonTextActive: {
    color: '#fff',
  },
  locationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: colors.primary,
    marginBottom: 24,
  },
  locationButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
    marginLeft: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 14,
    color: colors.text,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfWidth: {
    flex: 1,
  },
  defaultToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  defaultToggleLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  defaultToggleText: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
    marginLeft: 12,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    backgroundColor: colors.background,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  saveButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
