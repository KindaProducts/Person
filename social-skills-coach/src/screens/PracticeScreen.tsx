import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  Button,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Import the FeedbackDisplay component
import FeedbackDisplay from '../components/FeedbackDisplay';

// Define message type
type MessageType = {
  id: string;
  sender: 'AI' | 'User';
  text: string;
  timestamp: number;
};

const PracticeScreen = () => {
  // State for conversation history
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: '1',
      sender: 'AI',
      text: 'Hi there! I\'m your AI conversation partner. What social scenario would you like to practice today?',
      timestamp: Date.now(),
    },
  ]);

  // State for user input
  const [inputText, setInputText] = useState('');
  
  // State for feedback
  const [feedback, setFeedback] = useState<string | null>(null);
  
  // Reference to FlatList for scrolling to bottom
  const flatListRef = useRef<FlatList>(null);

  // Handler for sending a message
  const handleSend = () => {
    if (inputText.trim() === '') return;

    // Create a user message
    const userMessage: MessageType = {
      id: Date.now().toString() + '-user',
      sender: 'User',
      text: inputText,
      timestamp: Date.now(),
    };

    // Add user message to conversation
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Clear input
    setInputText('');

    // Simulate AI response after a delay
    setTimeout(() => {
      const aiMessage: MessageType = {
        id: Date.now().toString() + '-ai',
        sender: 'AI',
        text: 'Great job, try elaborating more on your thoughts. How do you think the other person might respond?',
        timestamp: Date.now(),
      };
      
      setMessages(prevMessages => [...prevMessages, aiMessage]);
      
      // Provide feedback
      setFeedback('Try to maintain eye contact and speak clearly. Your response could include more specific details.');
      
      // Scroll to bottom after adding new message
      if (flatListRef.current) {
        flatListRef.current.scrollToEnd({ animated: true });
      }
    }, 1000);
  };

  // Render each message
  const renderMessage = ({ item }: { item: MessageType }) => {
    const isAI = item.sender === 'AI';
    
    return (
      <View style={[
        styles.messageContainer,
        isAI ? styles.aiMessageContainer : styles.userMessageContainer
      ]}>
        <View style={[
          styles.messageBubble,
          isAI ? styles.aiMessage : styles.userMessage
        ]}>
          <Text style={styles.messageText}>{item.text}</Text>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <View style={styles.header}>
          <Text style={styles.headerText}>Practice Conversation</Text>
        </View>
        
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.messageList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />
        
        <FeedbackDisplay feedback={feedback} />
        
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your message..."
            multiline
            returnKeyType="send"
            onSubmitEditing={handleSend}
          />
          <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
            <Text style={styles.sendButtonText}>Send</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
  },
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
    backgroundColor: '#fff',
  },
  headerText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007bff',
    textAlign: 'center',
  },
  messageList: {
    padding: 16,
    paddingBottom: 16,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  aiMessageContainer: {
    justifyContent: 'flex-start',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
  },
  aiMessage: {
    backgroundColor: '#e0f7fa',
    borderBottomLeftRadius: 4,
  },
  userMessage: {
    backgroundColor: '#d1e7dd',
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: 16,
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
    backgroundColor: '#fff',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 8,
    maxHeight: 100,
    backgroundColor: '#f8f9fa',
  },
  sendButton: {
    backgroundColor: '#007bff',
    borderRadius: 20,
    paddingHorizontal: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default PracticeScreen; 