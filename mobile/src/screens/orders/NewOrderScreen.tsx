/**
 * New Order Screen
 * Create a new laundry order with garment photos
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import {
  fetchPaymentMethods,
  selectPaymentMethods,
  selectDefaultPaymentMethod,
  PaymentMethod,
} from '../../store/slices/paymentSlice';
import ImagePickerButton from '../../components/common/ImagePickerButton';
import ImagePreviewGrid from '../../components/common/ImagePreviewGrid';
import { ImageResult } from '../../utils/imagePickerService';
import uploadService, { UploadProgress } from '../../services/uploadService';
import { COLORS } from '../../constants/colors';

interface NewOrderScreenProps {
  navigation: any;
  route: any;
}

const NewOrderScreen: React.FC<NewOrderScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const paymentMethods = useAppSelector(selectPaymentMethods);
  const defaultPaymentMethod = useAppSelector(selectDefaultPaymentMethod);

  const [garmentImages, setGarmentImages] = useState<ImageResult[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [notes, setNotes] = useState('');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<PaymentMethod | null>(null);
  const [estimatedAmount] = useState(299); // Mock estimated amount

  const maxImages = 5;

  useEffect(() => {
    dispatch(fetchPaymentMethods());
  }, [dispatch]);

  useEffect(() => {
    if (defaultPaymentMethod) {
      setSelectedPaymentMethod(defaultPaymentMethod);
    }
  }, [defaultPaymentMethod]);

  const handleImagesSelected = (newImages: ImageResult[]) => {
    const remainingSlots = maxImages - garmentImages.length;
    const imagesToAdd = newImages.slice(0, remainingSlots);
    setGarmentImages([...garmentImages, ...imagesToAdd]);
  };

  const handleRemoveImage = (index: number) => {
    const updatedImages = garmentImages.filter((_, i) => i !== index);
    setGarmentImages(updatedImages);
  };

  const handleSubmit = async () => {
    if (garmentImages.length === 0) {
      Alert.alert(
        'No Photos',
        'Please add at least one photo of your garment items.',
        [{ text: 'OK' }]
      );
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      // Upload images
      const uploadedImages = await uploadService.uploadImagesSequentially(
        garmentImages,
        (index, progress) => {
          // Calculate overall progress
          const imageProgress = (index / garmentImages.length) * 100;
          const currentImageProgress = (progress.percentage / garmentImages.length);
          setUploadProgress(Math.round(imageProgress + currentImageProgress));
        }
      );

      console.log('Images uploaded successfully:', uploadedImages);

      // Here you would create the order with the uploaded image URLs
      // const orderData = {
      //   images: uploadedImages.map(img => img.url),
      //   notes,
      //   ...otherOrderData
      // };
      // await createOrder(orderData);

      Alert.alert(
        'Success!',
        'Your order has been created successfully.',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error: any) {
      console.error('Error creating order:', error);
      Alert.alert(
        'Upload Failed',
        error.message || 'Failed to upload images. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const canAddMore = garmentImages.length < maxImages;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Garment Photos</Text>
        <Text style={styles.sectionDescription}>
          Take photos of your laundry items to help us provide better service
        </Text>

        {garmentImages.length > 0 && (
          <ImagePreviewGrid
            images={garmentImages}
            onRemove={handleRemoveImage}
            maxImages={maxImages}
            editable={!uploading}
          />
        )}

        {canAddMore && (
          <ImagePickerButton
            onImageSelected={handleImagesSelected}
            maxImages={maxImages - garmentImages.length}
            buttonText={garmentImages.length === 0 ? 'Add Photos' : 'Add More Photos'}
            disabled={uploading}
          />
        )}

        {garmentImages.length >= maxImages && (
          <Text style={styles.maxImagesText}>
            Maximum {maxImages} photos reached
          </Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Special Instructions</Text>
        <TextInput
          style={styles.notesInput}
          placeholder="Add any special instructions for your order..."
          placeholderTextColor={COLORS.textLight}
          value={notes}
          onChangeText={setNotes}
          multiline
          numberOfLines={4}
          textAlignVertical="top"
          editable={!uploading}
        />
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Payment Method</Text>
          <TouchableOpacity
            onPress={() => navigation.navigate('PaymentMethods')}
            disabled={uploading}
          >
            <Text style={styles.manageLink}>Manage</Text>
          </TouchableOpacity>
        </View>

        {selectedPaymentMethod ? (
          <TouchableOpacity
            style={styles.paymentMethodCard}
            onPress={() => navigation.navigate('PaymentMethods')}
            disabled={uploading}
          >
            <Text style={styles.paymentMethodIcon}>
              {selectedPaymentMethod.type === 'card' && '💳'}
              {selectedPaymentMethod.type === 'upi' && '📱'}
              {selectedPaymentMethod.type === 'netbanking' && '🏦'}
              {selectedPaymentMethod.type === 'wallet' && '👛'}
            </Text>
            <View style={styles.paymentMethodInfo}>
              <Text style={styles.paymentMethodProvider}>
                {selectedPaymentMethod.provider}
              </Text>
              <Text style={styles.paymentMethodDetails}>
                {selectedPaymentMethod.type.toUpperCase()}
                {selectedPaymentMethod.last4 && ` •••• ${selectedPaymentMethod.last4}`}
                {selectedPaymentMethod.upi_id && ` • ${selectedPaymentMethod.upi_id}`}
              </Text>
            </View>
            <Text style={styles.changeText}>Change</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={styles.addPaymentButton}
            onPress={() => navigation.navigate('AddPaymentMethod')}
            disabled={uploading}
          >
            <Text style={styles.addPaymentIcon}>+</Text>
            <Text style={styles.addPaymentText}>Add Payment Method</Text>
          </TouchableOpacity>
        )}

        <View style={styles.estimatedAmountContainer}>
          <Text style={styles.estimatedAmountLabel}>Estimated Amount</Text>
          <Text style={styles.estimatedAmount}>₹{estimatedAmount}</Text>
        </View>
      </View>

      {uploading && (
        <View style={styles.uploadingContainer}>
          <Text style={styles.uploadingText}>
            Uploading images... {uploadProgress}%
          </Text>
          <View style={styles.progressBarContainer}>
            <View
              style={[styles.progressBar, { width: `${uploadProgress}%` }]}
            />
          </View>
        </View>
      )}

      <TouchableOpacity
        style={[styles.submitButton, uploading && styles.submitButtonDisabled]}
        onPress={handleSubmit}
        disabled={uploading}
        activeOpacity={0.7}
      >
        {uploading ? (
          <ActivityIndicator size="small" color={COLORS.white} />
        ) : (
          <Text style={styles.submitButtonText}>Create Order</Text>
        )}
      </TouchableOpacity>

      <View style={styles.spacer} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  contentContainer: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
  },
  manageLink: {
    fontSize: 14,
    color: COLORS.primary,
    fontWeight: '600',
  },
  sectionDescription: {
    fontSize: 14,
    color: COLORS.textLight,
    marginBottom: 16,
    lineHeight: 20,
  },
  maxImagesText: {
    fontSize: 14,
    color: COLORS.textLight,
    textAlign: 'center',
    marginTop: 12,
    fontStyle: 'italic',
  },
  notesInput: {
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: COLORS.text,
    minHeight: 120,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  uploadingContainer: {
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  uploadingText: {
    fontSize: 16,
    color: COLORS.text,
    marginBottom: 12,
    textAlign: 'center',
    fontWeight: '600',
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: COLORS.background,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 4,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
  },
  submitButtonDisabled: {
    backgroundColor: COLORS.textLight,
    opacity: 0.5,
  },
  submitButtonText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: '600',
  },
  spacer: {
    height: 32,
  },
  paymentMethodCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  paymentMethodIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  paymentMethodInfo: {
    flex: 1,
  },
  paymentMethodProvider: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  paymentMethodDetails: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  changeText: {
    fontSize: 14,
    color: COLORS.primary,
    fontWeight: '600',
  },
  addPaymentButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: COLORS.primary,
    borderStyle: 'dashed',
  },
  addPaymentIcon: {
    fontSize: 24,
    color: COLORS.primary,
    marginRight: 8,
  },
  addPaymentText: {
    fontSize: 16,
    color: COLORS.primary,
    fontWeight: '600',
  },
  estimatedAmountContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
  },
  estimatedAmountLabel: {
    fontSize: 16,
    color: COLORS.text,
    fontWeight: '500',
  },
  estimatedAmount: {
    fontSize: 20,
    color: COLORS.primary,
    fontWeight: 'bold',
  },
});

export default NewOrderScreen;
