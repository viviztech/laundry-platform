/**
 * Services Screen
 * Browse and select laundry services
 */

import React, { useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import { fetchServiceCategories, fetchServiceItems } from '../../store/slices/servicesSlice';

export default function ServicesScreen({ navigation }: any) {
  const dispatch = useAppDispatch();
  const { categories, items, isLoading } = useAppSelector((state) => state.services);

  useEffect(() => {
    dispatch(fetchServiceCategories());
    dispatch(fetchServiceItems());
  }, []);

  const renderCategory = ({ item }: any) => (
    <TouchableOpacity style={styles.categoryCard}>
      <Text style={styles.categoryName}>{item.name}</Text>
      <Text style={styles.categoryDescription}>{item.description}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Our Services</Text>
      <FlatList
        data={categories}
        renderItem={renderCategory}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 16,
  },
  list: {
    paddingBottom: 16,
  },
  categoryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
  },
  categoryName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#212121',
    marginBottom: 4,
  },
  categoryDescription: {
    fontSize: 14,
    color: '#757575',
  },
});
