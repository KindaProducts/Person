import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface FeedbackDisplayProps {
  feedback: string | null;
}

const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({ feedback }) => {
  if (!feedback) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.feedbackTitle}>Feedback:</Text>
      <Text style={styles.feedbackText}>{feedback}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#e9ecef',
    padding: 10,
    borderRadius: 5,
    marginHorizontal: 12,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#007bff',
  },
  feedbackTitle: {
    fontWeight: 'bold',
    fontSize: 14,
    marginBottom: 4,
    color: '#007bff',
  },
  feedbackText: {
    fontSize: 14,
    color: '#333',
  },
});

export default FeedbackDisplay; 