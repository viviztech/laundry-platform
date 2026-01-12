/**
 * Upload Service
 * Handles file uploads to backend
 */

import apiClient from '../api/client';
import { ImageResult } from '../utils/imagePickerService';

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface UploadedImage {
  url: string;
  id?: string;
  fileName: string;
  fileSize: number;
}

class UploadService {
  /**
   * Upload a single image
   */
  async uploadImage(
    image: ImageResult,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadedImage> {
    try {
      const formData = new FormData();

      // Append image to form data
      formData.append('image', {
        uri: image.uri,
        type: image.mimeType || 'image/jpeg',
        name: image.fileName || `image_${Date.now()}.jpg`,
      } as any);

      const response = await apiClient.upload('/mobile/upload-image/', formData, (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      });

      return {
        url: response.data.url || response.data.image_url,
        id: response.data.id,
        fileName: image.fileName,
        fileSize: image.fileSize,
      };
    } catch (error: any) {
      console.error('Error uploading image:', error);
      throw new Error(error.response?.data?.message || 'Failed to upload image');
    }
  }

  /**
   * Upload multiple images
   */
  async uploadImages(
    images: ImageResult[],
    onProgress?: (index: number, progress: UploadProgress) => void
  ): Promise<UploadedImage[]> {
    const uploadPromises = images.map((image, index) =>
      this.uploadImage(image, (progress) => {
        onProgress?.(index, progress);
      })
    );

    try {
      return await Promise.all(uploadPromises);
    } catch (error) {
      console.error('Error uploading multiple images:', error);
      throw error;
    }
  }

  /**
   * Upload images sequentially (one at a time)
   */
  async uploadImagesSequentially(
    images: ImageResult[],
    onProgress?: (index: number, progress: UploadProgress) => void,
    onComplete?: (index: number, result: UploadedImage) => void
  ): Promise<UploadedImage[]> {
    const results: UploadedImage[] = [];

    for (let i = 0; i < images.length; i++) {
      try {
        const result = await this.uploadImage(images[i], (progress) => {
          onProgress?.(i, progress);
        });
        results.push(result);
        onComplete?.(i, result);
      } catch (error) {
        console.error(`Error uploading image ${i + 1}:`, error);
        throw error;
      }
    }

    return results;
  }

  /**
   * Upload garment image specifically for orders
   */
  async uploadGarmentImage(
    image: ImageResult,
    orderId?: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadedImage> {
    try {
      const formData = new FormData();

      formData.append('image', {
        uri: image.uri,
        type: image.mimeType || 'image/jpeg',
        name: image.fileName || `garment_${Date.now()}.jpg`,
      } as any);

      if (orderId) {
        formData.append('order_id', orderId);
      }

      const response = await apiClient.upload(
        '/orders/upload-garment/',
        formData,
        (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress({
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage,
            });
          }
        }
      );

      return {
        url: response.data.url || response.data.image_url,
        id: response.data.id,
        fileName: image.fileName,
        fileSize: image.fileSize,
      };
    } catch (error: any) {
      console.error('Error uploading garment image:', error);
      throw new Error(error.response?.data?.message || 'Failed to upload garment image');
    }
  }

  /**
   * Delete an uploaded image
   */
  async deleteImage(imageId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/mobile/images/${imageId}/`);
      return true;
    } catch (error) {
      console.error('Error deleting image:', error);
      return false;
    }
  }
}

// Export singleton instance
export default new UploadService();
