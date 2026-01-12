/**
 * Image Picker Button Component
 * Reusable button for taking photos or selecting from gallery
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Image,
} from 'react-native';
import imagePickerService, { ImageResult } from '../../utils/imagePickerService';
import { COLORS } from '../../constants/colors';

interface ImagePickerButtonProps {
  onImageSelected: (images: ImageResult[]) => void;
  maxImages?: number;
  buttonText?: string;
  buttonStyle?: any;
  disabled?: boolean;
}

const ImagePickerButton: React.FC<ImagePickerButtonProps> = ({
  onImageSelected,
  maxImages = 1,
  buttonText = 'Add Photo',
  buttonStyle,
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false);

  const handlePress = async () => {
    if (disabled || loading) return;

    setLoading(true);
    try {
      const result = await imagePickerService.showImagePickerOptions({
        allowsEditing: true,
        quality: 0.8,
        allowsMultipleSelection: maxImages > 1,
      });

      if (result) {
        const images = Array.isArray(result) ? result : [result];

        // Validate images
        const validImages = images.filter(img => {
          const sizeValid = imagePickerService.validateImageSize(img, 5);
          const dimensionsValid = imagePickerService.validateImageDimensions(img, 100, 100);
          return sizeValid && dimensionsValid;
        });

        if (validImages.length > 0) {
          onImageSelected(validImages.slice(0, maxImages));
        }
      }
    } catch (error) {
      console.error('Error picking image:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableOpacity
      style={[styles.button, buttonStyle, disabled && styles.buttonDisabled]}
      onPress={handlePress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator size="small" color={COLORS.white} />
      ) : (
        <>
          <Text style={styles.buttonIcon}>📷</Text>
          <Text style={styles.buttonText}>{buttonText}</Text>
        </>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: COLORS.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    minHeight: 48,
  },
  buttonDisabled: {
    backgroundColor: COLORS.textLight,
    opacity: 0.5,
  },
  buttonIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  buttonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ImagePickerButton;
