/**
 * Add Payment Method Screen
 * Form to add new payment methods
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAppDispatch } from '../../store/store';
import { addPaymentMethod } from '../../store/slices/paymentSlice';
import { COLORS } from '../../constants/colors';

interface AddPaymentMethodScreenProps {
  navigation: any;
}

type PaymentType = 'card' | 'upi' | 'netbanking' | 'wallet';

const AddPaymentMethodScreen: React.FC<AddPaymentMethodScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();

  const [selectedType, setSelectedType] = useState<PaymentType>('card');
  const [loading, setLoading] = useState(false);

  // Card fields
  const [cardNumber, setCardNumber] = useState('');
  const [cardHolder, setCardHolder] = useState('');
  const [expiryMonth, setExpiryMonth] = useState('');
  const [expiryYear, setExpiryYear] = useState('');
  const [cvv, setCvv] = useState('');

  // UPI fields
  const [upiId, setUpiId] = useState('');

  // Net Banking fields
  const [bankName, setBankName] = useState('');

  // Wallet fields
  const [walletProvider, setWalletProvider] = useState('');
  const [walletNumber, setWalletNumber] = useState('');

  const [setAsDefault, setSetAsDefault] = useState(false);

  const paymentTypes = [
    { type: 'card' as PaymentType, label: 'Card', icon: '💳' },
    { type: 'upi' as PaymentType, label: 'UPI', icon: '📱' },
    { type: 'netbanking' as PaymentType, label: 'Net Banking', icon: '🏦' },
    { type: 'wallet' as PaymentType, label: 'Wallet', icon: '👛' },
  ];

  const validateCard = () => {
    if (cardNumber.length < 13 || cardNumber.length > 19) {
      Alert.alert('Invalid Card', 'Please enter a valid card number');
      return false;
    }
    if (!cardHolder.trim()) {
      Alert.alert('Invalid Name', 'Please enter cardholder name');
      return false;
    }
    if (!expiryMonth || parseInt(expiryMonth) < 1 || parseInt(expiryMonth) > 12) {
      Alert.alert('Invalid Expiry', 'Please enter valid expiry month (01-12)');
      return false;
    }
    if (!expiryYear || expiryYear.length !== 2) {
      Alert.alert('Invalid Expiry', 'Please enter valid expiry year (YY)');
      return false;
    }
    if (cvv.length < 3 || cvv.length > 4) {
      Alert.alert('Invalid CVV', 'Please enter valid CVV (3-4 digits)');
      return false;
    }
    return true;
  };

  const validateUPI = () => {
    const upiRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$/;
    if (!upiRegex.test(upiId)) {
      Alert.alert('Invalid UPI', 'Please enter a valid UPI ID (e.g., user@paytm)');
      return false;
    }
    return true;
  };

  const validateNetBanking = () => {
    if (!bankName.trim()) {
      Alert.alert('Invalid Bank', 'Please select a bank');
      return false;
    }
    return true;
  };

  const validateWallet = () => {
    if (!walletProvider.trim()) {
      Alert.alert('Invalid Wallet', 'Please select a wallet provider');
      return false;
    }
    if (walletNumber && walletNumber.length !== 10) {
      Alert.alert('Invalid Number', 'Please enter a valid mobile number');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    let isValid = false;
    let methodData: any = {
      type: selectedType,
      is_default: setAsDefault,
    };

    switch (selectedType) {
      case 'card':
        isValid = validateCard();
        if (isValid) {
          methodData = {
            ...methodData,
            card_number: cardNumber,
            card_holder: cardHolder,
            expiry_month: expiryMonth,
            expiry_year: expiryYear,
            cvv: cvv,
          };
        }
        break;

      case 'upi':
        isValid = validateUPI();
        if (isValid) {
          methodData = {
            ...methodData,
            upi_id: upiId,
          };
        }
        break;

      case 'netbanking':
        isValid = validateNetBanking();
        if (isValid) {
          methodData = {
            ...methodData,
            bank_name: bankName,
          };
        }
        break;

      case 'wallet':
        isValid = validateWallet();
        if (isValid) {
          methodData = {
            ...methodData,
            wallet_provider: walletProvider,
            wallet_number: walletNumber,
          };
        }
        break;
    }

    if (!isValid) return;

    setLoading(true);
    try {
      await dispatch(addPaymentMethod(methodData)).unwrap();
      Alert.alert('Success', 'Payment method added successfully', [
        {
          text: 'OK',
          onPress: () => navigation.goBack(),
        },
      ]);
    } catch (error: any) {
      Alert.alert('Error', error || 'Failed to add payment method');
    } finally {
      setLoading(false);
    }
  };

  const renderCardForm = () => (
    <View style={styles.formSection}>
      <Text style={styles.sectionTitle}>Card Details</Text>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Card Number</Text>
        <TextInput
          style={styles.input}
          placeholder="1234 5678 9012 3456"
          value={cardNumber}
          onChangeText={(text) => setCardNumber(text.replace(/\s/g, ''))}
          keyboardType="numeric"
          maxLength={19}
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>Cardholder Name</Text>
        <TextInput
          style={styles.input}
          placeholder="John Doe"
          value={cardHolder}
          onChangeText={setCardHolder}
          autoCapitalize="words"
        />
      </View>

      <View style={styles.row}>
        <View style={[styles.inputGroup, styles.flex1]}>
          <Text style={styles.label}>Expiry Month</Text>
          <TextInput
            style={styles.input}
            placeholder="MM"
            value={expiryMonth}
            onChangeText={setExpiryMonth}
            keyboardType="numeric"
            maxLength={2}
          />
        </View>

        <View style={[styles.inputGroup, styles.flex1]}>
          <Text style={styles.label}>Expiry Year</Text>
          <TextInput
            style={styles.input}
            placeholder="YY"
            value={expiryYear}
            onChangeText={setExpiryYear}
            keyboardType="numeric"
            maxLength={2}
          />
        </View>

        <View style={[styles.inputGroup, styles.flex1]}>
          <Text style={styles.label}>CVV</Text>
          <TextInput
            style={styles.input}
            placeholder="123"
            value={cvv}
            onChangeText={setCvv}
            keyboardType="numeric"
            maxLength={4}
            secureTextEntry
          />
        </View>
      </View>
    </View>
  );

  const renderUPIForm = () => (
    <View style={styles.formSection}>
      <Text style={styles.sectionTitle}>UPI Details</Text>

      <View style={styles.inputGroup}>
        <Text style={styles.label}>UPI ID</Text>
        <TextInput
          style={styles.input}
          placeholder="yourname@paytm"
          value={upiId}
          onChangeText={setUpiId}
          keyboardType="email-address"
          autoCapitalize="none"
        />
      </View>

      <Text style={styles.helperText}>
        Enter your UPI ID (e.g., mobile@paytm, user@oksbi)
      </Text>
    </View>
  );

  const renderNetBankingForm = () => {
    const banks = [
      'State Bank of India',
      'HDFC Bank',
      'ICICI Bank',
      'Axis Bank',
      'Punjab National Bank',
      'Bank of Baroda',
      'Canara Bank',
      'Union Bank of India',
    ];

    return (
      <View style={styles.formSection}>
        <Text style={styles.sectionTitle}>Select Your Bank</Text>

        {banks.map((bank) => (
          <TouchableOpacity
            key={bank}
            style={[
              styles.bankOption,
              bankName === bank && styles.bankOptionSelected,
            ]}
            onPress={() => setBankName(bank)}
          >
            <View style={styles.radioButton}>
              {bankName === bank && <View style={styles.radioButtonInner} />}
            </View>
            <Text style={styles.bankName}>{bank}</Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  const renderWalletForm = () => {
    const wallets = [
      { name: 'Paytm', icon: '📱' },
      { name: 'PhonePe', icon: '💜' },
      { name: 'Google Pay', icon: '🔵' },
      { name: 'Amazon Pay', icon: '🟡' },
      { name: 'Mobikwik', icon: '🔴' },
    ];

    return (
      <View style={styles.formSection}>
        <Text style={styles.sectionTitle}>Select Wallet Provider</Text>

        <View style={styles.walletGrid}>
          {wallets.map((wallet) => (
            <TouchableOpacity
              key={wallet.name}
              style={[
                styles.walletOption,
                walletProvider === wallet.name && styles.walletOptionSelected,
              ]}
              onPress={() => setWalletProvider(wallet.name)}
            >
              <Text style={styles.walletIcon}>{wallet.icon}</Text>
              <Text style={styles.walletName}>{wallet.name}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {walletProvider && (
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Mobile Number (Optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="10-digit mobile number"
              value={walletNumber}
              onChangeText={setWalletNumber}
              keyboardType="phone-pad"
              maxLength={10}
            />
          </View>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.typeSelector}>
          {paymentTypes.map((type) => (
            <TouchableOpacity
              key={type.type}
              style={[
                styles.typeButton,
                selectedType === type.type && styles.typeButtonSelected,
              ]}
              onPress={() => setSelectedType(type.type)}
            >
              <Text style={styles.typeIcon}>{type.icon}</Text>
              <Text
                style={[
                  styles.typeLabel,
                  selectedType === type.type && styles.typeLabelSelected,
                ]}
              >
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {selectedType === 'card' && renderCardForm()}
        {selectedType === 'upi' && renderUPIForm()}
        {selectedType === 'netbanking' && renderNetBankingForm()}
        {selectedType === 'wallet' && renderWalletForm()}

        <TouchableOpacity
          style={styles.defaultCheckbox}
          onPress={() => setSetAsDefault(!setAsDefault)}
        >
          <View style={styles.checkbox}>
            {setAsDefault && <Text style={styles.checkmark}>✓</Text>}
          </View>
          <Text style={styles.checkboxLabel}>Set as default payment method</Text>
        </TouchableOpacity>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator size="small" color={COLORS.white} />
          ) : (
            <Text style={styles.submitButtonText}>Add Payment Method</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  typeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  typeButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    marginHorizontal: 4,
    backgroundColor: COLORS.white,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  typeButtonSelected: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(0, 122, 255, 0.05)',
  },
  typeIcon: {
    fontSize: 28,
    marginBottom: 4,
  },
  typeLabel: {
    fontSize: 12,
    color: COLORS.textLight,
    fontWeight: '500',
  },
  typeLabelSelected: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  formSection: {
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 16,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.text,
    marginBottom: 8,
  },
  input: {
    backgroundColor: COLORS.background,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  flex1: {
    flex: 1,
  },
  helperText: {
    fontSize: 12,
    color: COLORS.textLight,
    marginTop: 8,
  },
  bankOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginBottom: 8,
    backgroundColor: COLORS.background,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  bankOptionSelected: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(0, 122, 255, 0.05)',
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: COLORS.textLight,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioButtonInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.primary,
  },
  bankName: {
    fontSize: 16,
    color: COLORS.text,
  },
  walletGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  walletOption: {
    width: '48%',
    alignItems: 'center',
    padding: 16,
    backgroundColor: COLORS.background,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  walletOptionSelected: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(0, 122, 255, 0.05)',
  },
  walletIcon: {
    fontSize: 36,
    marginBottom: 8,
  },
  walletName: {
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.text,
  },
  defaultCheckbox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: COLORS.textLight,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmark: {
    fontSize: 16,
    color: COLORS.primary,
    fontWeight: 'bold',
  },
  checkboxLabel: {
    fontSize: 16,
    color: COLORS.text,
  },
  footer: {
    padding: 16,
    backgroundColor: COLORS.white,
    borderTopWidth: 1,
    borderTopColor: COLORS.background,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
});

export default AddPaymentMethodScreen;
