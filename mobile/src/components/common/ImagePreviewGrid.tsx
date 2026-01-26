/**
 * Image Preview Grid Component
 * Displays selected images with remove option
 */

import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Dimensions,
} from 'react-native';
import { ImageResult } from '../../utils/imagePickerService';
import { COLORS } from '../../constants/colors';

interface ImagePreviewGridProps {
  images: (ImageResult | string)[];
  onRemove?: (index: number) => void;
  maxImages?: number;
  editable?: boolean;
}

const { width: screenWidth } = Dimensions.get('window');
const imageSize = (screenWidth - 48) / 3; // 3 columns with padding

const ImagePreviewGrid: React.FC<ImagePreviewGridProps> = ({
  images,
  onRemove,
  maxImages,
  editable = true,
}) => {
  const getImageUri = (image: ImageResult | string): string => {
    return typeof image === 'string' ? image : image.uri;
  };

  if (images.length === 0) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>
          Photos {maxImages && `(${images.length}/${maxImages})`}
        </Text>
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {images.map((image, index) => (
          <View key={index} style={styles.imageContainer}>
            <Image
              source={{ uri: getImageUri(image) }}
              style={styles.image}
              resizeMode="cover"
            />
            {editable && onRemove && (
              <TouchableOpacity
                style={styles.removeButton}
                onPress={() => onRemove(index)}
                activeOpacity={0.7}
              >
                <Text style={styles.removeButtonText}>✕</Text>
              </TouchableOpacity>
            )}
            <View style={styles.imageNumberBadge}>
              <Text style={styles.imageNumberText}>{index + 1}</Text>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
  scrollContent: {
    paddingRight: 16,
  },
  imageContainer: {
    width: imageSize,
    height: imageSize,
    marginRight: 12,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: COLORS.background,
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  removeButton: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: 'bold',
  },
  imageNumberBadge: {
    position: 'absolute',
    bottom: 4,
    left: 4,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageNumberText: {
    color: COLORS.white,
    fontSize: 12,
    fontWeight: '600',
  },
});

export default ImagePreviewGrid;
