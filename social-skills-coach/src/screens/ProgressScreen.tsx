import React from 'react';
import { View, Text, StyleSheet, Dimensions, ScrollView } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import { SafeAreaView } from 'react-native-safe-area-context';

// Get screen width to size the chart
const screenWidth = Dimensions.get('window').width;

const ProgressScreen = () => {
  // Hardcoded progress data
  const conversationData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        data: [5, 8, 12, 10],
      },
    ],
  };

  // Chart configuration
  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`, // #007bff with opacity
    strokeWidth: 2,
    barPercentage: 0.7,
    decimalPlaces: 0,
    propsForLabels: {
      fontSize: 12,
    },
  };

  // Skill metrics data
  const skillMetrics = [
    { skill: 'Conversation Flow', score: 78 },
    { skill: 'Active Listening', score: 65 },
    { skill: 'Empathy', score: 82 },
    { skill: 'Clarity', score: 70 },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container}>
        <Text style={styles.title}>Progress Overview</Text>
        
        <View style={styles.chartContainer}>
          <Text style={styles.chartTitle}>Completed Conversations</Text>
          <BarChart
            data={conversationData}
            width={screenWidth * 0.9}
            height={220}
            chartConfig={chartConfig}
            style={styles.chart}
            fromZero
            showValuesOnTopOfBars
            yAxisLabel=""
            yAxisSuffix=""
          />
        </View>
        
        <View style={styles.metricsContainer}>
          <Text style={styles.chartTitle}>Skill Metrics</Text>
          {skillMetrics.map((item, index) => (
            <View key={index} style={styles.metricItem}>
              <Text style={styles.metricName}>{item.skill}</Text>
              <View style={styles.progressBarContainer}>
                <View 
                  style={[
                    styles.progressBar,
                    { width: `${item.score}%` },
                    item.score > 75 ? styles.highScore : 
                    item.score > 60 ? styles.mediumScore : 
                    styles.lowScore
                  ]}
                />
              </View>
              <Text style={styles.metricScore}>{item.score}%</Text>
            </View>
          ))}
        </View>
        
        <View style={styles.summaryContainer}>
          <Text style={styles.chartTitle}>Monthly Summary</Text>
          <Text style={styles.summaryText}>
            You've completed 35 conversation practices this month, which is a 20% improvement from last month.
            Your strongest skill is Empathy, while Active Listening could use more practice.
          </Text>
          <Text style={styles.tipText}>
            Tip: Try asking more follow-up questions during conversations to improve your Active Listening score.
          </Text>
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
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 24,
    textAlign: 'center',
  },
  chartContainer: {
    alignItems: 'center',
    marginBottom: 24,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 8,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
    alignSelf: 'flex-start',
  },
  metricsContainer: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
  },
  metricItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  metricName: {
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
  highScore: {
    backgroundColor: '#28a745', // green
  },
  mediumScore: {
    backgroundColor: '#ffc107', // yellow
  },
  lowScore: {
    backgroundColor: '#dc3545', // red
  },
  metricScore: {
    width: '15%',
    fontSize: 14,
    textAlign: 'right',
    color: '#555',
  },
  summaryContainer: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
  },
  summaryText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
    marginBottom: 16,
  },
  tipText: {
    fontSize: 14,
    color: '#007bff',
    fontStyle: 'italic',
    backgroundColor: '#e9ecef',
    padding: 12,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#007bff',
  },
});

export default ProgressScreen; 