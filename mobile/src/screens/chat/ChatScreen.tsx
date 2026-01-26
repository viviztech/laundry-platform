/**
 * Chat Screen
 * Real-time chat interface for messaging with partner
 */

import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../../store/store';
import {
  fetchMessages,
  sendMessage,
  setCurrentRoom,
  addMessage,
  setTypingUser,
  markRoomAsRead,
  selectMessages,
  selectMessagesLoading,
  selectTypingUsers,
  selectIsConnected,
} from '../../store/slices/chatSlice';
import { selectUser } from '../../store/slices/authSlice';
import chatService, { ChatMessage } from '../../services/chatService';
import { COLORS } from '../../constants/colors';

interface ChatScreenProps {
  route: any;
  navigation: any;
}

const ChatScreen: React.FC<ChatScreenProps> = ({ route, navigation }) => {
  const { roomId, orderId, partnerName } = route.params;

  const dispatch = useAppDispatch();
  const messages = useAppSelector(selectMessages(roomId));
  const loading = useAppSelector(selectMessagesLoading(roomId));
  const typingUsers = useAppSelector(selectTypingUsers(roomId));
  const isConnected = useAppSelector(selectIsConnected);
  const currentUser = useAppSelector(selectUser);

  const [inputText, setInputText] = useState('');
  const [sending, setSending] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Set navigation title
  useEffect(() => {
    navigation.setOptions({
      title: partnerName || 'Chat',
      headerRight: () => (
        <View style={styles.headerRight}>
          <View style={[styles.connectionDot, { backgroundColor: isConnected ? COLORS.success : COLORS.error }]} />
        </View>
      ),
    });
  }, [navigation, partnerName, isConnected]);

  // Initialize chat
  useEffect(() => {
    dispatch(setCurrentRoom(roomId));
    dispatch(fetchMessages({ roomId }));

    // Join room
    chatService.joinRoom(roomId);

    // Mark as read
    dispatch(markRoomAsRead(roomId));

    // Cleanup
    return () => {
      chatService.leaveRoom(roomId);
      dispatch(setCurrentRoom(null));
    };
  }, [dispatch, roomId]);

  // Listen for new messages
  useEffect(() => {
    const unsubscribeMessage = chatService.onMessage((message) => {
      if (message.room_id === roomId) {
        dispatch(addMessage(message));

        // Auto-scroll to bottom
        setTimeout(() => {
          flatListRef.current?.scrollToEnd({ animated: true });
        }, 100);

        // Mark as read
        chatService.markMessageAsRead(message.id);
      }
    });

    const unsubscribeTyping = chatService.onTyping((status) => {
      if (status.user_id !== currentUser?.id) {
        dispatch(setTypingUser({ roomId, status }));
      }
    });

    return () => {
      unsubscribeMessage();
      unsubscribeTyping();
    };
  }, [dispatch, roomId, currentUser]);

  const handleSend = useCallback(async () => {
    if (!inputText.trim() || sending) return;

    const messageText = inputText.trim();
    setInputText('');
    setSending(true);

    try {
      await dispatch(sendMessage({ roomId, message: messageText })).unwrap();

      // Stop typing indicator
      chatService.sendTypingStop(roomId);

      // Scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Restore message on error
      setInputText(messageText);
    } finally {
      setSending(false);
    }
  }, [dispatch, inputText, roomId, sending]);

  const handleInputChange = (text: string) => {
    setInputText(text);

    // Send typing indicator
    if (text.trim()) {
      chatService.sendTypingStart(roomId);

      // Clear previous timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      // Stop typing after 2 seconds of inactivity
      typingTimeoutRef.current = setTimeout(() => {
        chatService.sendTypingStop(roomId);
      }, 2000);
    } else {
      chatService.sendTypingStop(roomId);
    }
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const isOwnMessage = item.sender.id === currentUser?.id;

    return (
      <View
        style={[
          styles.messageContainer,
          isOwnMessage ? styles.ownMessage : styles.otherMessage,
        ]}
      >
        {!isOwnMessage && (
          <Text style={styles.senderName}>{item.sender.name}</Text>
        )}
        <View
          style={[
            styles.messageBubble,
            isOwnMessage ? styles.ownBubble : styles.otherBubble,
          ]}
        >
          <Text
            style={[
              styles.messageText,
              isOwnMessage ? styles.ownText : styles.otherText,
            ]}
          >
            {item.message}
          </Text>
        </View>
        <Text style={styles.messageTime}>
          {new Date(item.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Text>
      </View>
    );
  };

  const renderTypingIndicator = () => {
    if (typingUsers.length === 0) return null;

    return (
      <View style={styles.typingContainer}>
        <Text style={styles.typingText}>
          {typingUsers[0].user_name} is typing...
        </Text>
      </View>
    );
  };

  if (loading && messages.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading messages...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        inverted={false}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: false })}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No messages yet</Text>
            <Text style={styles.emptySubtext}>Start the conversation!</Text>
          </View>
        }
      />

      {renderTypingIndicator()}

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={handleInputChange}
          placeholder="Type a message..."
          placeholderTextColor={COLORS.textLight}
          multiline
          maxLength={1000}
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!inputText.trim() || sending) && styles.sendButtonDisabled,
          ]}
          onPress={handleSend}
          disabled={!inputText.trim() || sending}
        >
          {sending ? (
            <ActivityIndicator size="small" color={COLORS.white} />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  headerRight: {
    marginRight: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  messagesList: {
    paddingHorizontal: 16,
    paddingTop: 16,
    flexGrow: 1,
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: '80%',
  },
  ownMessage: {
    alignSelf: 'flex-end',
    alignItems: 'flex-end',
  },
  otherMessage: {
    alignSelf: 'flex-start',
    alignItems: 'flex-start',
  },
  senderName: {
    fontSize: 12,
    color: COLORS.textLight,
    marginBottom: 4,
    marginLeft: 12,
  },
  messageBubble: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 18,
    maxWidth: '100%',
  },
  ownBubble: {
    backgroundColor: COLORS.primary,
    borderBottomRightRadius: 4,
  },
  otherBubble: {
    backgroundColor: COLORS.white,
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  ownText: {
    color: COLORS.white,
  },
  otherText: {
    color: COLORS.text,
  },
  messageTime: {
    fontSize: 11,
    color: COLORS.textLight,
    marginTop: 4,
    marginHorizontal: 12,
  },
  typingContainer: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  typingText: {
    fontSize: 14,
    color: COLORS.textLight,
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: COLORS.white,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    backgroundColor: COLORS.background,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 16,
    maxHeight: 100,
    marginRight: 12,
  },
  sendButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 70,
  },
  sendButtonDisabled: {
    backgroundColor: COLORS.textLight,
    opacity: 0.5,
  },
  sendButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: COLORS.textLight,
  },
});

export default ChatScreen;
