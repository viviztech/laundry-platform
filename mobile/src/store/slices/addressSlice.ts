import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/apiClient';
import { API_ENDPOINTS } from '../../constants/api';

export interface Address {
  id: string;
  label: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  pincode: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  zone?: string;
  contact_name?: string;
  contact_phone?: string;
  is_default: boolean;
  is_active?: boolean;
  created_at?: string;
}

interface AddressState {
  addresses: Address[];
  selectedAddress: Address | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: AddressState = {
  addresses: [],
  selectedAddress: null,
  isLoading: false,
  error: null,
};

// Fetch all addresses
export const fetchAddresses = createAsyncThunk(
  'address/fetchAddresses',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<any>(API_ENDPOINTS.PROFILE.ADDRESSES);
      return response.data.results || response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch addresses');
    }
  }
);

// Create new address
export const createAddress = createAsyncThunk(
  'address/createAddress',
  async (addressData: Partial<Address>, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<Address>(API_ENDPOINTS.PROFILE.ADDRESSES, addressData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create address');
    }
  }
);

// Update address
export const updateAddress = createAsyncThunk(
  'address/updateAddress',
  async ({ id, data }: { id: string; data: Partial<Address> }, { rejectWithValue }) => {
    try {
      const response = await apiClient.put<Address>(API_ENDPOINTS.PROFILE.ADDRESS_DETAIL(id), data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update address');
    }
  }
);

// Delete address
export const deleteAddress = createAsyncThunk(
  'address/deleteAddress',
  async (id: string, { rejectWithValue }) => {
    try {
      await apiClient.delete(API_ENDPOINTS.PROFILE.ADDRESS_DETAIL(id));
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete address');
    }
  }
);

// Set default address
export const setDefaultAddress = createAsyncThunk(
  'address/setDefaultAddress',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.patch<Address>(
        API_ENDPOINTS.PROFILE.ADDRESS_DETAIL(id),
        { is_default: true }
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to set default address');
    }
  }
);

const addressSlice = createSlice({
  name: 'address',
  initialState,
  reducers: {
    selectAddress: (state, action: PayloadAction<Address | null>) => {
      state.selectedAddress = action.payload;
    },
    clearAddressError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch addresses
    builder
      .addCase(fetchAddresses.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAddresses.fulfilled, (state, action) => {
        state.isLoading = false;
        state.addresses = action.payload;
        // Auto-select default address if none selected
        if (!state.selectedAddress && action.payload.length > 0) {
          state.selectedAddress = action.payload.find((addr: Address) => addr.is_default) || action.payload[0];
        }
      })
      .addCase(fetchAddresses.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create address
    builder
      .addCase(createAddress.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createAddress.fulfilled, (state, action) => {
        state.isLoading = false;
        state.addresses.push(action.payload);
        // If it's the first address or marked as default, select it
        if (action.payload.is_default || state.addresses.length === 1) {
          state.selectedAddress = action.payload;
        }
      })
      .addCase(createAddress.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update address
    builder
      .addCase(updateAddress.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateAddress.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.addresses.findIndex((addr) => addr.id === action.payload.id);
        if (index !== -1) {
          state.addresses[index] = action.payload;
        }
        // Update selected address if it was updated
        if (state.selectedAddress?.id === action.payload.id) {
          state.selectedAddress = action.payload;
        }
      })
      .addCase(updateAddress.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Delete address
    builder
      .addCase(deleteAddress.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteAddress.fulfilled, (state, action) => {
        state.isLoading = false;
        state.addresses = state.addresses.filter((addr) => addr.id !== action.payload);
        // Clear selected address if it was deleted
        if (state.selectedAddress?.id === action.payload) {
          state.selectedAddress = state.addresses.find((addr) => addr.is_default) || state.addresses[0] || null;
        }
      })
      .addCase(deleteAddress.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Set default address
    builder
      .addCase(setDefaultAddress.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(setDefaultAddress.fulfilled, (state, action) => {
        state.isLoading = false;
        // Mark all addresses as non-default
        state.addresses = state.addresses.map((addr) => ({
          ...addr,
          is_default: addr.id === action.payload.id,
        }));
        state.selectedAddress = action.payload;
      })
      .addCase(setDefaultAddress.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { selectAddress, clearAddressError } = addressSlice.actions;
export default addressSlice.reducer;
