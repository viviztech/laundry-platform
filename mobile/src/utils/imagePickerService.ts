/**
 * Image Picker Service
 * Handles camera and gallery image selection with proper permissions
 */

import * as ImagePicker from 'expo-image-picker';
import { Alert, Platform } from 'react-native';

export interface ImageResult {
  uri: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  width: number;
  height: number;
}

class ImagePickerService {
  /**
   * Request camera permissions
   */
  async requestCameraPermission(): Promise<boolean> {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();

      if (status !== 'granted') {
        Alert.alert(
          'Camera Permission Required',
          'Please enable camera access in your device settings to take photos.',
          [{ text: 'OK' }]
        );
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error requesting camera permission:', error);
      return false;
    }
  }

  /**
   * Request media library permissions
   */
  async requestMediaLibraryPermission(): Promise<boolean> {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (status !== 'granted') {
        Alert.alert(
          'Gallery Permission Required',
          'Please enable photo library access in your device settings to select photos.',
          [{ text: 'OK' }]
        );
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error requesting media library permission:', error);
      return false;
    }
  }

  /**
   * Launch camera to take a photo
   */
  async takePhoto(options?: {
    allowsEditing?: boolean;
    aspect?: [number, number];
    quality?: number;
  }): Promise<ImageResult | null> {
    try {
      // Request permission
      const hasPermission = await this.requestCameraPermission();
      if (!hasPermission) {
        return null;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: options?.allowsEditing ?? true,
        aspect: options?.aspect ?? [4, 3],
        quality: options?.quality ?? 0.8,
        exif: false,
      });

      if (result.canceled || !result.assets || result.assets.length === 0) {
        return null;
      }

      const asset = result.assets[0];

      return {
        uri: asset.uri,
        fileName: asset.fileName || `photo_${Date.now()}.jpg`,
        fileSize: asset.fileSize || 0,
        mimeType: asset.mimeType || 'image/jpeg',
        width: asset.width,
        height: asset.height,
      };
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo. Please try again.');
      return null;
    }
  }

  /**
   * Pick an image from gallery
   */
  async pickFromGallery(options?: {
    allowsEditing?: boolean;
    aspect?: [number, number];
    quality?: number;
    allowsMultipleSelection?: boolean;
  }): Promise<ImageResult | ImageResult[] | null> {
    try {
      // Request permission
      const hasPermission = await this.requestMediaLibraryPermission();
      if (!hasPermission) {
        return null;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: options?.allowsEditing ?? true,
        aspect: options?.aspect ?? [4, 3],
        quality: options?.quality ?? 0.8,
        allowsMultipleSelection: options?.allowsMultipleSelection ?? false,
        exif: false,
      });

      if (result.canceled || !result.assets || result.assets.length === 0) {
        return null;
      }

      const images = result.assets.map(asset => ({
        uri: asset.uri,
        fileName: asset.fileName || `image_${Date.now()}.jpg`,
        fileSize: asset.fileSize || 0,
        mimeType: asset.mimeType || 'image/jpeg',
        width: asset.width,
        height: asset.height,
      }));

      return options?.allowsMultipleSelection ? images : images[0];
    } catch (error) {
      console.error('Error picking from gallery:', error);
      Alert.alert('Error', 'Failed to select image. Please try again.');
      return null;
    }
  }

  /**
   * Show action sheet to choose camera or gallery
   */
  async showImagePickerOptions(options?: {
    allowsEditing?: boolean;
    aspect?: [number, number];
    quality?: number;
    allowsMultipleSelection?: boolean;
  }): Promise<ImageResult | ImageResult[] | null> {
    return new Promise((resolve) => {
      Alert.alert(
        'Select Photo',
        'Choose where to get your photo from',
        [
          {
            text: 'Take Photo',
            onPress: async () => {
              const result = await this.takePhoto(options);
              resolve(result);
            },
          },
          {
            text: 'Choose from Gallery',
            onPress: async () => {
              const result = await this.pickFromGallery(options);
              resolve(result);
            },
          },
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => resolve(null),
          },
        ],
        { cancelable: true, onDismiss: () => resolve(null) }
      );
    });
  }

  /**
   * Validate image size (max 5MB by default)
   */
  validateImageSize(imageResult: ImageResult, maxSizeMB: number = 5): boolean {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;

    if (imageResult.fileSize > maxSizeBytes) {
      Alert.alert(
        'Image Too Large',
        `Please select an image smaller than ${maxSizeMB}MB. Current size: ${(
          imageResult.fileSize /
          1024 /
          1024
        ).toFixed(2)}MB`,
        [{ text: 'OK' }]
      );
      return false;
    }

    return true;
  }

  /**
   * Validate image dimensions
   */
  validateImageDimensions(
    imageResult: ImageResult,
    minWidth: number = 100,
    minHeight: number = 100
  ): boolean {
    if (imageResult.width < minWidth || imageResult.height < minHeight) {
      Alert.alert(
        'Image Too Small',
        `Please select an image at least ${minWidth}x${minHeight} pixels. Current size: ${imageResult.width}x${imageResult.height}`,
        [{ text: 'OK' }]
      );
      return false;
    }

    return true;
  }

  /**
   * Get image dimensions without loading the full image
   */
  async getImageInfo(uri: string): Promise<{ width: number; height: number } | null> {
    try {
      const info = await ImagePicker.getImageAsync(uri);
      return {
        width: info.width,
        height: info.height,
      };
    } catch (error) {
      console.error('Error getting image info:', error);
      return null;
    }
  }
}

// Export singleton instance
export default new ImagePickerService();
