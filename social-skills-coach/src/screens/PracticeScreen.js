import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const PracticeScreen = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hi there! I\'m your AI conversation partner. What social scenario would you like to practice today?', isUser: false },
  ]);
  const [input, setInput] = useState('');
  const [feedback, setFeedback] = useState(null);

  const handleSend = () => {
    if (input.trim() === '') return;
    
    // Add user message
    const newUserMessage = {
      id: messages.length + 1,
      text: input,
      isUser: true,
    };
    
    setMessages([...messages, newUserMessage]);
    setInput('');
    
    // Simulate AI response (this would be replaced with actual API call)
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        text: 'That\'s a great topic! Let\'s practice a networking conversation. Imagine we\'re at a professional conference. Tell me about what you do.',
        isUser: false,
      };
      
      setMessages(prevMessages => [...prevMessages, aiResponse]);
      
      // Simulate feedback
      setFeedback({
        tone: 'Friendly',
        clarity: 'Good',
        suggestions: 'Try to be more specific about your interests in the next response.'
      });
    }, 1000);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : null}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Conversation Practice</Text>
        </View>
        
        <ScrollView style={styles.messagesContainer}>
          {messages.map(message => (
            <View 
              key={message.id} 
              style={[
                styles.messageBubble, 
                message.isUser ? styles.userMessage : styles.aiMessage
              ]}
            >
              <Text style={styles.messageText}>{message.text}</Text>
            </View>
          ))}
          
          {feedback && (
            <View style={styles.feedbackContainer}>
              <Text style={styles.feedbackTitle}>Feedback:</Text>
              <Text style={styles.feedbackText}>Tone: {feedback.tone}</Text>
              <Text style={styles.feedbackText}>Clarity: {feedback.clarity}</Text>
              <Text style={styles.feedbackText}>Suggestion: {feedback.suggestions}</Text>
            </View>
          )}
        </ScrollView>
        
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={input}
            onChangeText={setInput}
            placeholder="Type your response..."
            multiline
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
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007bff',
    textAlign: 'center',
  },
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    marginBottom: 12,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#e1ffc7',
    borderBottomRightRadius: 4,
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#e6f2ff',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    color: '#333',
  },
  feedbackContainer: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginVertical: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#007bff',
  },
  feedbackTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
    color: '#007bff',
  },
  feedbackText: {
    fontSize: 14,
    color: '#555',
    marginBottom: 2,
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
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: '#007bff',
    borderRadius: 20,
    width: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default PracticeScreen; 