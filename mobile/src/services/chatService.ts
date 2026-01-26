/**
 * WebSocket Chat Service
 * Handles real-time chat communication using Socket.IO
 */

import { io, Socket } from 'socket.io-client';
import { API_CONFIG, WEBSOCKET_EVENTS } from '../constants/api';
import apiClient from '../api/client';

export interface ChatMessage {
  id: string;
  room_id: string;
  sender: {
    id: string;
    name: string;
    user_type: 'customer' | 'partner';
  };
  message: string;
  image?: string;
  created_at: string;
  is_read: boolean;
}

export interface ChatRoom {
  id: string;
  order_id: string;
  customer: {
    id: string;
    name: string;
  };
  partner: {
    id: string;
    name: string;
  };
  last_message?: ChatMessage;
  unread_count: number;
  created_at: string;
}

export interface TypingStatus {
  user_id: string;
  user_name: string;
  is_typing: boolean;
}

class ChatService {
  private socket: Socket | null = null;
  private currentRoomId: string | null = null;
  private messageListeners: ((message: ChatMessage) => void)[] = [];
  private typingListeners: ((status: TypingStatus) => void)[] = [];
  private connectionListeners: ((connected: boolean) => void)[] = [];

  /**
   * Connect to WebSocket server with authentication
   */
  async connect(token: string): Promise<void> {
    if (this.socket?.connected) {
      console.log('Already connected to chat server');
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        this.socket = io(API_CONFIG.WS_URL, {
          auth: { token },
          transports: ['websocket'],
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionAttempts: 5,
        });

        this.socket.on(WEBSOCKET_EVENTS.CONNECT, () => {
          console.log('Connected to chat server');
          this.notifyConnectionListeners(true);
          resolve();
        });

        this.socket.on(WEBSOCKET_EVENTS.DISCONNECT, () => {
          console.log('Disconnected from chat server');
          this.notifyConnectionListeners(false);
        });

        this.socket.on(WEBSOCKET_EVENTS.ERROR, (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        });

        this.socket.on(WEBSOCKET_EVENTS.NEW_MESSAGE, (message: ChatMessage) => {
          console.log('New message received:', message);
          this.notifyMessageListeners(message);
        });

        this.socket.on(WEBSOCKET_EVENTS.TYPING_START, (data: { user_id: string; user_name: string }) => {
          this.notifyTypingListeners({ ...data, is_typing: true });
        });

        this.socket.on(WEBSOCKET_EVENTS.TYPING_STOP, (data: { user_id: string; user_name: string }) => {
          this.notifyTypingListeners({ ...data, is_typing: false });
        });
      } catch (error) {
        console.error('Failed to connect to chat server:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.currentRoomId = null;
    }
  }

  /**
   * Join a chat room
   */
  joinRoom(roomId: string): void {
    if (!this.socket?.connected) {
      console.error('Socket not connected');
      return;
    }

    if (this.currentRoomId === roomId) {
      console.log('Already in room:', roomId);
      return;
    }

    // Leave current room if any
    if (this.currentRoomId) {
      this.leaveRoom(this.currentRoomId);
    }

    this.socket.emit('join', { room_id: roomId });
    this.currentRoomId = roomId;
    console.log('Joined room:', roomId);
  }

  /**
   * Leave a chat room
   */
  leaveRoom(roomId: string): void {
    if (!this.socket?.connected) {
      return;
    }

    this.socket.emit('leave', { room_id: roomId });
    if (this.currentRoomId === roomId) {
      this.currentRoomId = null;
    }
    console.log('Left room:', roomId);
  }

  /**
   * Send a chat message
   */
  sendMessage(roomId: string, message: string): void {
    if (!this.socket?.connected) {
      console.error('Socket not connected');
      throw new Error('Not connected to chat server');
    }

    this.socket.emit(WEBSOCKET_EVENTS.CHAT_MESSAGE, {
      room_id: roomId,
      message,
    });
  }

  /**
   * Send typing indicator
   */
  sendTypingStart(roomId: string): void {
    if (!this.socket?.connected) return;
    this.socket.emit(WEBSOCKET_EVENTS.TYPING_START, { room_id: roomId });
  }

  /**
   * Stop typing indicator
   */
  sendTypingStop(roomId: string): void {
    if (!this.socket?.connected) return;
    this.socket.emit(WEBSOCKET_EVENTS.TYPING_STOP, { room_id: roomId });
  }

  /**
   * Mark message as read
   */
  markMessageAsRead(messageId: string): void {
    if (!this.socket?.connected) return;
    this.socket.emit(WEBSOCKET_EVENTS.MESSAGE_READ, { message_id: messageId });
  }

  /**
   * Get chat rooms (via REST API)
   */
  async getChatRooms(): Promise<ChatRoom[]> {
    try {
      const response = await apiClient.get('/chat/rooms/');
      return response.data;
    } catch (error) {
      console.error('Error fetching chat rooms:', error);
      throw error;
    }
  }

  /**
   * Get messages for a room (via REST API)
   */
  async getMessages(roomId: string, page: number = 1, limit: number = 50): Promise<ChatMessage[]> {
    try {
      const response = await apiClient.get(`/chat/rooms/${roomId}/messages/`, {
        params: { page, limit },
      });
      return response.data.results || response.data;
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  }

  /**
   * Upload image for chat (via REST API)
   */
  async uploadImage(imageUri: string): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'chat-image.jpg',
      } as any);

      const response = await apiClient.upload('/chat/upload/', formData);
      return response.data.url;
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error;
    }
  }

  /**
   * Register message listener
   */
  onMessage(callback: (message: ChatMessage) => void): () => void {
    this.messageListeners.push(callback);
    // Return unsubscribe function
    return () => {
      this.messageListeners = this.messageListeners.filter(cb => cb !== callback);
    };
  }

  /**
   * Register typing listener
   */
  onTyping(callback: (status: TypingStatus) => void): () => void {
    this.typingListeners.push(callback);
    return () => {
      this.typingListeners = this.typingListeners.filter(cb => cb !== callback);
    };
  }

  /**
   * Register connection listener
   */
  onConnectionChange(callback: (connected: boolean) => void): () => void {
    this.connectionListeners.push(callback);
    return () => {
      this.connectionListeners = this.connectionListeners.filter(cb => cb !== callback);
    };
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Get current room ID
   */
  getCurrentRoomId(): string | null {
    return this.currentRoomId;
  }

  // Private helper methods

  private notifyMessageListeners(message: ChatMessage): void {
    this.messageListeners.forEach(callback => {
      try {
        callback(message);
      } catch (error) {
        console.error('Error in message listener:', error);
      }
    });
  }

  private notifyTypingListeners(status: TypingStatus): void {
    this.typingListeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in typing listener:', error);
      }
    });
  }

  private notifyConnectionListeners(connected: boolean): void {
    this.connectionListeners.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('Error in connection listener:', error);
      }
    });
  }
}

// Export singleton instance
export default new ChatService();
