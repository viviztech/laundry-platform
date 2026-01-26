/**
 * Payment Redux Slice
 * Manages payment methods, wallet, and transactions
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../api/client';

export interface PaymentMethod {
  id: string;
  type: 'card' | 'upi' | 'netbanking' | 'wallet';
  provider: string;
  last4?: string;
  upi_id?: string;
  is_default: boolean;
  created_at: string;
}

export interface Wallet {
  balance: number;
  currency: string;
  cashback?: number;
  rewards?: number;
}

export interface Transaction {
  id: string;
  type: 'credit' | 'debit' | 'refund';
  amount: number;
  description: string;
  status: string;
  created_at: string;
  order_id?: string;
}

export interface WalletTransaction {
  id: string;
  type: 'credit' | 'debit';
  amount: number;
  description: string;
  created_at: string;
}

export interface Payment {
  id: string;
  order_id: string;
  amount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  payment_method: PaymentMethod;
  created_at: string;
  updated_at: string;
}

export interface PaymentState {
  paymentMethods: PaymentMethod[];
  wallet: Wallet | null;
  transactions: Transaction[];
  currentPayment: Payment | null;
  loading: boolean;
  error: string | null;
  methodsLoading: boolean;
  walletLoading: boolean;
}

const initialState: PaymentState = {
  paymentMethods: [],
  wallet: null,
  transactions: [],
  currentPayment: null,
  loading: false,
  error: null,
  methodsLoading: false,
  walletLoading: false,
};

// Async Thunks

/**
 * Fetch all payment methods
 */
export const fetchPaymentMethods = createAsyncThunk(
  'payment/fetchMethods',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/payments/saved-methods/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch payment methods');
    }
  }
);

/**
 * Add a new payment method
 */
export const addPaymentMethod = createAsyncThunk(
  'payment/addMethod',
  async (methodData: { type: string; provider: string; details: any }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post('/payments/saved-methods/', methodData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to add payment method');
    }
  }
);

/**
 * Delete a payment method
 */
export const deletePaymentMethod = createAsyncThunk(
  'payment/deleteMethod',
  async (methodId: string, { rejectWithValue }) => {
    try {
      await apiClient.delete(`/payments/saved-methods/${methodId}/`);
      return methodId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete payment method');
    }
  }
);

/**
 * Set default payment method
 */
export const setDefaultPaymentMethod = createAsyncThunk(
  'payment/setDefault',
  async (methodId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.patch(`/payments/saved-methods/${methodId}/`, {
        is_default: true,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to set default payment method');
    }
  }
);

/**
 * Fetch wallet balance and transactions
 */
export const fetchWallet = createAsyncThunk(
  'payment/fetchWallet',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/payments/wallets/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch wallet');
    }
  }
);

/**
 * Fetch wallet transactions
 */
export const fetchTransactions = createAsyncThunk(
  'payment/fetchTransactions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/payments/wallets/transactions/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch transactions');
    }
  }
);

/**
 * Add money to wallet
 */
export const addMoneyToWallet = createAsyncThunk(
  'payment/addMoney',
  async ({ amount }: { amount: number }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post('/payments/wallets/add-money/', { amount });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to add money to wallet');
    }
  }
);

/**
 * Create payment for order
 */
export const createPayment = createAsyncThunk(
  'payment/create',
  async (
    { orderId, methodId, amount }: { orderId: string; methodId: string; amount: number },
    { rejectWithValue }
  ) => {
    try {
      const response = await apiClient.post('/payments/payments/', {
        order_id: orderId,
        payment_method_id: methodId,
        amount,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create payment');
    }
  }
);

/**
 * Verify payment
 */
export const verifyPayment = createAsyncThunk(
  'payment/verify',
  async (
    { paymentId, verificationData }: { paymentId: string; verificationData: any },
    { rejectWithValue }
  ) => {
    try {
      const response = await apiClient.post(`/payments/payments/${paymentId}/verify/`, verificationData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Payment verification failed');
    }
  }
);

// Payment Slice

const paymentSlice = createSlice({
  name: 'payment',
  initialState,
  reducers: {
    /**
     * Clear current payment
     */
    clearCurrentPayment: (state) => {
      state.currentPayment = null;
    },

    /**
     * Set error
     */
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },

    /**
     * Clear error
     */
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Payment Methods
    builder
      .addCase(fetchPaymentMethods.pending, (state) => {
        state.methodsLoading = true;
        state.error = null;
      })
      .addCase(fetchPaymentMethods.fulfilled, (state, action) => {
        state.methodsLoading = false;
        state.paymentMethods = action.payload;
      })
      .addCase(fetchPaymentMethods.rejected, (state, action) => {
        state.methodsLoading = false;
        state.error = action.payload as string;
      });

    // Add Payment Method
    builder
      .addCase(addPaymentMethod.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addPaymentMethod.fulfilled, (state, action) => {
        state.loading = false;
        state.paymentMethods.push(action.payload);
      })
      .addCase(addPaymentMethod.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Delete Payment Method
    builder
      .addCase(deletePaymentMethod.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deletePaymentMethod.fulfilled, (state, action) => {
        state.loading = false;
        state.paymentMethods = state.paymentMethods.filter(
          (method) => method.id !== action.payload
        );
      })
      .addCase(deletePaymentMethod.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Set Default Payment Method
    builder
      .addCase(setDefaultPaymentMethod.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(setDefaultPaymentMethod.fulfilled, (state, action) => {
        state.loading = false;
        // Update all methods - set only the selected one as default
        state.paymentMethods = state.paymentMethods.map((method) => ({
          ...method,
          is_default: method.id === action.payload.id,
        }));
      })
      .addCase(setDefaultPaymentMethod.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Fetch Wallet
    builder
      .addCase(fetchWallet.pending, (state) => {
        state.walletLoading = true;
        state.error = null;
      })
      .addCase(fetchWallet.fulfilled, (state, action) => {
        state.walletLoading = false;
        state.wallet = action.payload;
      })
      .addCase(fetchWallet.rejected, (state, action) => {
        state.walletLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Transactions
    builder
      .addCase(fetchTransactions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTransactions.fulfilled, (state, action) => {
        state.loading = false;
        state.transactions = action.payload;
      })
      .addCase(fetchTransactions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Add Money to Wallet
    builder
      .addCase(addMoneyToWallet.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addMoneyToWallet.fulfilled, (state, action) => {
        state.loading = false;
        state.wallet = action.payload;
      })
      .addCase(addMoneyToWallet.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Create Payment
    builder
      .addCase(createPayment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createPayment.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPayment = action.payload;
      })
      .addCase(createPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Verify Payment
    builder
      .addCase(verifyPayment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyPayment.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPayment = action.payload;
      })
      .addCase(verifyPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// Export actions
export const { clearCurrentPayment, setError, clearError } = paymentSlice.actions;

// Export reducer
export default paymentSlice.reducer;

// Selectors
export const selectPaymentMethods = (state: { payment: PaymentState }) => state.payment.paymentMethods;
export const selectDefaultPaymentMethod = (state: { payment: PaymentState }) =>
  state.payment.paymentMethods.find((method) => method.is_default);
export const selectWallet = (state: { payment: PaymentState }) => state.payment.wallet;
export const selectTransactions = (state: { payment: PaymentState }) => state.payment.transactions;
export const selectCurrentPayment = (state: { payment: PaymentState }) => state.payment.currentPayment;
export const selectPaymentLoading = (state: { payment: PaymentState }) => state.payment.loading;
export const selectPaymentError = (state: { payment: PaymentState }) => state.payment.error;
export const selectMethodsLoading = (state: { payment: PaymentState }) => state.payment.methodsLoading;
export const selectWalletLoading = (state: { payment: PaymentState }) => state.payment.walletLoading;
