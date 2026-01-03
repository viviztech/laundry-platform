/**
 * Orders Redux Slice
 * Manages order state and operations
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../api/client';
import { API_ENDPOINTS } from '../../constants/api';
import { OrdersState, Order } from '../../types';

const initialState: OrdersState = {
  orders: [],
  activeOrders: [],
  selectedOrder: null,
  isLoading: false,
  error: null,
};

// Async Thunks

export const fetchOrders = createAsyncThunk(
  'orders/fetchOrders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<Order[]>(API_ENDPOINTS.ORDERS.LIST);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch orders');
    }
  }
);

export const fetchOrderDetail = createAsyncThunk(
  'orders/fetchOrderDetail',
  async (orderId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<Order>(API_ENDPOINTS.ORDERS.DETAIL(orderId));
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch order details');
    }
  }
);

export const createOrder = createAsyncThunk(
  'orders/createOrder',
  async (orderData: Partial<Order>, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<Order>(API_ENDPOINTS.ORDERS.CREATE, orderData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create order');
    }
  }
);

export const cancelOrder = createAsyncThunk(
  'orders/cancelOrder',
  async ({ orderId, reason }: { orderId: string; reason?: string }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<Order>(API_ENDPOINTS.ORDERS.CANCEL(orderId), {
        reason,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to cancel order');
    }
  }
);

export const trackOrder = createAsyncThunk(
  'orders/trackOrder',
  async (orderId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<Order>(API_ENDPOINTS.ORDERS.TRACK(orderId));
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to track order');
    }
  }
);

// Slice
const ordersSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    setSelectedOrder: (state, action: PayloadAction<Order | null>) => {
      state.selectedOrder = action.payload;
    },
    updateOrderStatus: (state, action: PayloadAction<{ orderId: string; status: string }>) => {
      const { orderId, status } = action.payload;

      // Update in orders array
      const orderIndex = state.orders.findIndex((order) => order.id === orderId);
      if (orderIndex >= 0) {
        state.orders[orderIndex].status = status as any;
      }

      // Update in active orders
      const activeOrderIndex = state.activeOrders.findIndex((order) => order.id === orderId);
      if (activeOrderIndex >= 0) {
        state.activeOrders[activeOrderIndex].status = status as any;
      }

      // Update selected order
      if (state.selectedOrder?.id === orderId) {
        state.selectedOrder.status = status as any;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Orders
    builder
      .addCase(fetchOrders.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.isLoading = false;
        state.orders = action.payload;
        state.activeOrders = action.payload.filter(
          (order) =>
            !['delivered', 'cancelled'].includes(order.status)
        );
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Order Detail
    builder
      .addCase(fetchOrderDetail.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchOrderDetail.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedOrder = action.payload;

        // Update in orders array if exists
        const index = state.orders.findIndex((order) => order.id === action.payload.id);
        if (index >= 0) {
          state.orders[index] = action.payload;
        }
      })
      .addCase(fetchOrderDetail.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create Order
    builder
      .addCase(createOrder.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.isLoading = false;
        state.orders.unshift(action.payload);
        state.activeOrders.unshift(action.payload);
        state.selectedOrder = action.payload;
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Cancel Order
    builder
      .addCase(cancelOrder.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(cancelOrder.fulfilled, (state, action) => {
        state.isLoading = false;

        // Update orders array
        const orderIndex = state.orders.findIndex((order) => order.id === action.payload.id);
        if (orderIndex >= 0) {
          state.orders[orderIndex] = action.payload;
        }

        // Remove from active orders
        state.activeOrders = state.activeOrders.filter(
          (order) => order.id !== action.payload.id
        );

        // Update selected order
        if (state.selectedOrder?.id === action.payload.id) {
          state.selectedOrder = action.payload;
        }
      })
      .addCase(cancelOrder.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Track Order
    builder
      .addCase(trackOrder.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(trackOrder.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedOrder = action.payload;
      })
      .addCase(trackOrder.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setSelectedOrder, updateOrderStatus, clearError } = ordersSlice.actions;
export default ordersSlice.reducer;
