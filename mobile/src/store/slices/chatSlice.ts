/**
 * Chat Redux Slice
 * Manages chat state including rooms, messages, and typing indicators
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import chatService, { ChatMessage, ChatRoom, TypingStatus } from '../../services/chatService';

export interface ChatState {
  rooms: ChatRoom[];
  currentRoomId: string | null;
  messages: Record<string, ChatMessage[]>; // roomId -> messages
  typingUsers: Record<string, TypingStatus[]>; // roomId -> typing users
  isConnected: boolean;
  loading: boolean;
  error: string | null;
  roomsLoading: boolean;
  messagesLoading: Record<string, boolean>; // roomId -> loading
}

const initialState: ChatState = {
  rooms: [],
  currentRoomId: null,
  messages: {},
  typingUsers: {},
  isConnected: false,
  loading: false,
  error: null,
  roomsLoading: false,
  messagesLoading: {},
};

// Async Thunks

/**
 * Fetch all chat rooms
 */
export const fetchChatRooms = createAsyncThunk(
  'chat/fetchRooms',
  async (_, { rejectWithValue }) => {
    try {
      const rooms = await chatService.getChatRooms();
      return rooms;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch chat rooms');
    }
  }
);

/**
 * Fetch messages for a specific room
 */
export const fetchMessages = createAsyncThunk(
  'chat/fetchMessages',
  async ({ roomId, page = 1 }: { roomId: string; page?: number }, { rejectWithValue }) => {
    try {
      const messages = await chatService.getMessages(roomId, page);
      return { roomId, messages };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch messages');
    }
  }
);

/**
 * Send a chat message
 */
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ roomId, message }: { roomId: string; message: string }, { rejectWithValue }) => {
    try {
      chatService.sendMessage(roomId, message);
      return { roomId, message };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to send message');
    }
  }
);

/**
 * Upload and send image
 */
export const sendImage = createAsyncThunk(
  'chat/sendImage',
  async ({ roomId, imageUri }: { roomId: string; imageUri: string }, { rejectWithValue }) => {
    try {
      const imageUrl = await chatService.uploadImage(imageUri);
      chatService.sendMessage(roomId, imageUrl);
      return { roomId, imageUrl };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to send image');
    }
  }
);

// Chat Slice

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    /**
     * Set connection status
     */
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },

    /**
     * Set current room
     */
    setCurrentRoom: (state, action: PayloadAction<string | null>) => {
      state.currentRoomId = action.payload;
    },

    /**
     * Add a new message to a room
     */
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      const message = action.payload;
      const roomId = message.room_id;

      if (!state.messages[roomId]) {
        state.messages[roomId] = [];
      }

      // Check if message already exists
      const exists = state.messages[roomId].some(m => m.id === message.id);
      if (!exists) {
        state.messages[roomId].push(message);

        // Update last message in room
        const room = state.rooms.find(r => r.id === roomId);
        if (room) {
          room.last_message = message;

          // Increment unread count if not current room
          if (state.currentRoomId !== roomId) {
            room.unread_count += 1;
          }
        }
      }
    },

    /**
     * Add typing user to room
     */
    setTypingUser: (state, action: PayloadAction<{ roomId: string; status: TypingStatus }>) => {
      const { roomId, status } = action.payload;

      if (!state.typingUsers[roomId]) {
        state.typingUsers[roomId] = [];
      }

      if (status.is_typing) {
        // Add or update typing user
        const existingIndex = state.typingUsers[roomId].findIndex(u => u.user_id === status.user_id);
        if (existingIndex >= 0) {
          state.typingUsers[roomId][existingIndex] = status;
        } else {
          state.typingUsers[roomId].push(status);
        }
      } else {
        // Remove typing user
        state.typingUsers[roomId] = state.typingUsers[roomId].filter(
          u => u.user_id !== status.user_id
        );
      }
    },

    /**
     * Mark room messages as read
     */
    markRoomAsRead: (state, action: PayloadAction<string>) => {
      const roomId = action.payload;
      const room = state.rooms.find(r => r.id === roomId);
      if (room) {
        room.unread_count = 0;
      }

      // Mark all messages as read
      if (state.messages[roomId]) {
        state.messages[roomId].forEach(message => {
          message.is_read = true;
        });
      }
    },

    /**
     * Clear messages for a room
     */
    clearRoomMessages: (state, action: PayloadAction<string>) => {
      const roomId = action.payload;
      delete state.messages[roomId];
    },

    /**
     * Clear all chat state
     */
    clearChat: (state) => {
      state.rooms = [];
      state.currentRoomId = null;
      state.messages = {};
      state.typingUsers = {};
      state.isConnected = false;
      state.error = null;
    },

    /**
     * Set error
     */
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch Rooms
    builder
      .addCase(fetchChatRooms.pending, (state) => {
        state.roomsLoading = true;
        state.error = null;
      })
      .addCase(fetchChatRooms.fulfilled, (state, action) => {
        state.roomsLoading = false;
        state.rooms = action.payload;
      })
      .addCase(fetchChatRooms.rejected, (state, action) => {
        state.roomsLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Messages
    builder
      .addCase(fetchMessages.pending, (state, action) => {
        const roomId = action.meta.arg.roomId;
        state.messagesLoading[roomId] = true;
        state.error = null;
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        const { roomId, messages } = action.payload;
        state.messagesLoading[roomId] = false;
        state.messages[roomId] = messages;
      })
      .addCase(fetchMessages.rejected, (state, action) => {
        const roomId = action.meta.arg.roomId;
        state.messagesLoading[roomId] = false;
        state.error = action.payload as string;
      });

    // Send Message
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
      })
      .addCase(sendMessage.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Send Image
    builder
      .addCase(sendImage.pending, (state) => {
        state.loading = true;
      })
      .addCase(sendImage.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(sendImage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// Export actions
export const {
  setConnected,
  setCurrentRoom,
  addMessage,
  setTypingUser,
  markRoomAsRead,
  clearRoomMessages,
  clearChat,
  setError,
} = chatSlice.actions;

// Export reducer
export default chatSlice.reducer;

// Selectors
export const selectChatRooms = (state: { chat: ChatState }) => state.chat.rooms;
export const selectCurrentRoomId = (state: { chat: ChatState }) => state.chat.currentRoomId;
export const selectMessages = (roomId: string) => (state: { chat: ChatState }) =>
  state.chat.messages[roomId] || [];
export const selectTypingUsers = (roomId: string) => (state: { chat: ChatState }) =>
  state.chat.typingUsers[roomId] || [];
export const selectIsConnected = (state: { chat: ChatState }) => state.chat.isConnected;
export const selectChatLoading = (state: { chat: ChatState }) => state.chat.loading;
export const selectRoomsLoading = (state: { chat: ChatState }) => state.chat.roomsLoading;
export const selectMessagesLoading = (roomId: string) => (state: { chat: ChatState }) =>
  state.chat.messagesLoading[roomId] || false;
export const selectChatError = (state: { chat: ChatState }) => state.chat.error;
export const selectUnreadCount = (state: { chat: ChatState}) =>
  state.chat.rooms.reduce((total, room) => total + room.unread_count, 0);
