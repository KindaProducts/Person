import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const ProgressScreen = () => {
  // Mock data for progress graph
  const skillScores = [
    { category: 'Conversation Flow', score: 75 },
    { category: 'Active Listening', score: 60 },
    { category: 'Empathy', score: 80 },
    { category: 'Clarity', score: 65 },
    { category: 'Confidence', score: 70 },
  ];

  // Mock practice history
  const practiceHistory = [
    { id: 1, date: '2023-08-10', scenario: 'Networking', duration: '15 min', improvement: '+5%' },
    { id: 2, date: '2023-08-08', scenario: 'Job Interview', duration: '20 min', improvement: '+8%' },
    { id: 3, date: '2023-08-05', scenario: 'Casual Conversation', duration: '10 min', improvement: '+3%' },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container}>
        <Text style={styles.title}>Your Progress</Text>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Social Skills Overview</Text>
          
          <View style={styles.skillsContainer}>
            {skillScores.map((skill, index) => (
              <View key={index} style={styles.skillRow}>
                <Text style={styles.skillLabel}>{skill.category}</Text>
                <View style={styles.progressBarContainer}>
                  <View 
                    style={[
                      styles.progressBar, 
                      { width: `${skill.score}%` },
                      skill.score > 70 ? styles.progressHigh : 
                      skill.score > 50 ? styles.progressMedium : 
                      styles.progressLow
                    ]} 
                  />
                </View>
                <Text style={styles.skillScore}>{skill.score}%</Text>
              </View>
            ))}
          </View>
        </View>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recent Practice Sessions</Text>
          
          {practiceHistory.map(session => (
            <View key={session.id} style={styles.sessionItem}>
              <View style={styles.sessionHeader}>
                <Text style={styles.sessionTitle}>{session.scenario}</Text>
                <Text style={styles.sessionDate}>{session.date}</Text>
              </View>
              <View style={styles.sessionDetails}>
                <Text style={styles.sessionDetail}>Duration: {session.duration}</Text>
                <Text style={styles.sessionImprovement}>Improvement: {session.improvement}</Text>
              </View>
            </View>
          ))}
        </View>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recommendations</Text>
          <Text style={styles.recommendationText}>
            Based on your progress, we recommend focusing on improving your Active Listening skills.
            Try the following exercises:
          </Text>
          <View style={styles.bulletPoints}>
            <Text style={styles.bulletPoint}>• Practice summarizing what others say</Text>
            <Text style={styles.bulletPoint}>• Ask follow-up questions during conversations</Text>
            <Text style={styles.bulletPoint}>• Minimize distractions during discussions</Text>
          </View>
        </View>
      </ScrollView>
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
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 24,
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  skillsContainer: {
    marginTop: 8,
  },
  skillRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  skillLabel: {
    width: '30%',
    fontSize: 14,
    color: '#555',
  },
  progressBarContainer: {
    flex: 1,
    height: 10,
    backgroundColor: '#e9ecef',
    borderRadius: 5,
    marginHorizontal: 8,
  },
  progressBar: {
    height: '100%',
    borderRadius: 5,
  },
  progressHigh: {
    backgroundColor: '#28a745',
  },
  progressMedium: {
    backgroundColor: '#ffc107',
  },
  progressLow: {
    backgroundColor: '#dc3545',
  },
  skillScore: {
    width: '15%',
    fontSize: 14,
    textAlign: 'right',
    color: '#555',
  },
  sessionItem: {
    backgroundColor: '#fff',
    borderRadius: 4,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#007bff',
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  sessionTitle: {
    fontWeight: 'bold',
    color: '#333',
  },
  sessionDate: {
    color: '#777',
    fontSize: 12,
  },
  sessionDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  sessionDetail: {
    color: '#555',
    fontSize: 13,
  },
  sessionImprovement: {
    color: '#28a745',
    fontSize: 13,
    fontWeight: 'bold',
  },
  recommendationText: {
    color: '#555',
    marginBottom: 12,
    lineHeight: 20,
  },
  bulletPoints: {
    marginLeft: 8,
  },
  bulletPoint: {
    color: '#555',
    marginBottom: 6,
    lineHeight: 20,
  },
});

export default ProgressScreen; 