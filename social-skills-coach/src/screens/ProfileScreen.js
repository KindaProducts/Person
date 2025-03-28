import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Switch, ScrollView, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const ProfileScreen = () => {
  const [notifications, setNotifications] = useState(true);
  const [dailyReminders, setDailyReminders] = useState(true);
  const [feedbackDetail, setFeedbackDetail] = useState('medium');

  // Mock user data
  const userData = {
    name: 'Alex Johnson',
    email: 'alex.johnson@example.com',
    memberSince: 'August 2023',
    sessionsCompleted: 12,
    totalPracticeTime: '4.5 hours',
    topSkill: 'Empathy',
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container}>
        <View style={styles.profileHeader}>
          <View style={styles.avatarContainer}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{userData.name.charAt(0)}</Text>
            </View>
          </View>
          <Text style={styles.userName}>{userData.name}</Text>
          <Text style={styles.userEmail}>{userData.email}</Text>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{userData.sessionsCompleted}</Text>
              <Text style={styles.statLabel}>Sessions</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{userData.totalPracticeTime}</Text>
              <Text style={styles.statLabel}>Practice Time</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{userData.topSkill}</Text>
              <Text style={styles.statLabel}>Top Skill</Text>
            </View>
          </View>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Settings</Text>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Notifications</Text>
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{ false: '#e9ecef', true: '#b3d7ff' }}
              thumbColor={notifications ? '#007bff' : '#f4f3f4'}
            />
          </View>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Daily Practice Reminders</Text>
            <Switch
              value={dailyReminders}
              onValueChange={setDailyReminders}
              trackColor={{ false: '#e9ecef', true: '#b3d7ff' }}
              thumbColor={dailyReminders ? '#007bff' : '#f4f3f4'}
            />
          </View>
          
          <Text style={styles.settingGroupLabel}>Feedback Detail Level</Text>
          <View style={styles.radioGroup}>
            <TouchableOpacity 
              style={styles.radioOption} 
              onPress={() => setFeedbackDetail('basic')}
            >
              <View style={[
                styles.radioButton, 
                feedbackDetail === 'basic' && styles.radioButtonSelected
              ]}>
                {feedbackDetail === 'basic' && <View style={styles.radioButtonInner} />}
              </View>
              <Text style={styles.radioLabel}>Basic</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.radioOption} 
              onPress={() => setFeedbackDetail('medium')}
            >
              <View style={[
                styles.radioButton, 
                feedbackDetail === 'medium' && styles.radioButtonSelected
              ]}>
                {feedbackDetail === 'medium' && <View style={styles.radioButtonInner} />}
              </View>
              <Text style={styles.radioLabel}>Medium</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.radioOption} 
              onPress={() => setFeedbackDetail('detailed')}
            >
              <View style={[
                styles.radioButton, 
                feedbackDetail === 'detailed' && styles.radioButtonSelected
              ]}>
                {feedbackDetail === 'detailed' && <View style={styles.radioButtonInner} />}
              </View>
              <Text style={styles.radioLabel}>Detailed</Text>
            </TouchableOpacity>
          </View>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Edit Profile</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.button, styles.buttonOutline]}>
            <Text style={styles.buttonTextOutline}>Change Password</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.button, styles.buttonDanger]}>
            <Text style={styles.buttonText}>Log Out</Text>
          </TouchableOpacity>
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
  },
  profileHeader: {
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
    padding: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  avatarContainer: {
    marginBottom: 16,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#007bff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  userEmail: {
    color: '#777',
    marginBottom: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007bff',
  },
  statLabel: {
    fontSize: 12,
    color: '#777',
  },
  statDivider: {
    width: 1,
    height: '100%',
    backgroundColor: '#e9ecef',
  },
  section: {
    padding: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
  },
  settingGroupLabel: {
    marginTop: 16,
    marginBottom: 8,
    fontSize: 16,
    color: '#333',
  },
  radioGroup: {
    marginBottom: 16,
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  radioButton: {
    height: 20,
    width: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#007bff',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  radioButtonSelected: {
    borderColor: '#007bff',
  },
  radioButtonInner: {
    height: 10,
    width: 10,
    borderRadius: 5,
    backgroundColor: '#007bff',
  },
  radioLabel: {
    fontSize: 16,
    color: '#333',
  },
  button: {
    backgroundColor: '#007bff',
    borderRadius: 4,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#007bff',
  },
  buttonDanger: {
    backgroundColor: '#dc3545',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  buttonTextOutline: {
    color: '#007bff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default ProfileScreen; 