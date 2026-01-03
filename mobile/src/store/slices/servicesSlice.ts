/**
 * Services Redux Slice
 * Manages service categories and items state
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import { API_ENDPOINTS } from '../../constants/api';
import { ServicesState, ServiceCategory, ServiceItem } from '../../types';

const initialState: ServicesState = {
  categories: [],
  items: [],
  selectedCategory: null,
  isLoading: false,
  error: null,
};

// Async Thunks

export const fetchServiceCategories = createAsyncThunk(
  'services/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<ServiceCategory[]>(API_ENDPOINTS.SERVICES.CATEGORIES);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch categories');
    }
  }
);

export const fetchServiceItems = createAsyncThunk(
  'services/fetchItems',
  async (categoryId?: string, { rejectWithValue }) => {
    try {
      const url = categoryId
        ? `${API_ENDPOINTS.SERVICES.ITEMS}?category=${categoryId}`
        : API_ENDPOINTS.SERVICES.ITEMS;
      const response = await apiClient.get<ServiceItem[]>(url);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch service items');
    }
  }
);

export const fetchServiceItemDetail = createAsyncThunk(
  'services/fetchItemDetail',
  async (itemId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<ServiceItem>(
        API_ENDPOINTS.SERVICES.ITEM_DETAIL(itemId)
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch item details');
    }
  }
);

// Slice
const servicesSlice = createSlice({
  name: 'services',
  initialState,
  reducers: {
    setSelectedCategory: (state, action: PayloadAction<string | null>) => {
      state.selectedCategory = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Categories
    builder
      .addCase(fetchServiceCategories.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchServiceCategories.fulfilled, (state, action) => {
        state.isLoading = false;
        state.categories = action.payload;
      })
      .addCase(fetchServiceCategories.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Items
    builder
      .addCase(fetchServiceItems.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchServiceItems.fulfilled, (state, action) => {
        state.isLoading = false;
        state.items = action.payload;
      })
      .addCase(fetchServiceItems.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Item Detail
    builder
      .addCase(fetchServiceItemDetail.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchServiceItemDetail.fulfilled, (state, action) => {
        state.isLoading = false;
        // Update or add item to items array
        const index = state.items.findIndex((item) => item.id === action.payload.id);
        if (index >= 0) {
          state.items[index] = action.payload;
        } else {
          state.items.push(action.payload);
        }
      })
      .addCase(fetchServiceItemDetail.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setSelectedCategory, clearError } = servicesSlice.actions;
export default servicesSlice.reducer;
