import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import 'package:airsense_5g/models/chat_message_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';

class ChatService {
  static final ChatService _instance = ChatService._internal();
  factory ChatService() => _instance;
  ChatService._internal();

  final _uuid = const Uuid();
  final _random = Random();

  Future<ChatMessage> sendQuery(String userId, String query, HealthProfile? profile) async {
    try {
      await Future.delayed(const Duration(milliseconds: 1200));
      
      final response = _generateResponse(query, profile);
      
      final chatMessage = ChatMessage(
        id: _uuid.v4(),
        userId: userId,
        message: query,
        response: response,
        timestamp: DateTime.now(),
        isUser: false,
      );
      
      debugPrint('✅ Chat response generated');
      return chatMessage;
    } catch (e) {
      debugPrint('❌ Send query error: $e');
      rethrow;
    }
  }

  String _generateResponse(String query, HealthProfile? profile) {
    final lowerQuery = query.toLowerCase();
    
    if (lowerQuery.contains('safe') && lowerQuery.contains('outside')) {
      if (profile != null && profile.conditions.contains('Asthma')) {
        return 'Based on your asthma condition, I recommend checking the current PM2.5 levels. If PM2.5 is above 35 µg/m³, it\'s safer to stay indoors. Would you like me to check the current air quality in your area?';
      }
      return 'Generally, it\'s safe to go outside when the AQI is below 100. However, if you have respiratory conditions, consider staying indoors when AQI exceeds 50. Check the current air quality on the dashboard for real-time data.';
    }
    
    if (lowerQuery.contains('asthma') || lowerQuery.contains('breathing')) {
      return 'For individuals with asthma, I recommend:\n\n1. Avoid outdoor activities when PM2.5 exceeds 35 µg/m³\n2. Keep rescue inhalers nearby\n3. Monitor air quality regularly\n4. Use indoor air purifiers\n5. Keep windows closed on high pollution days\n\nWould you like personalized alerts based on your location?';
    }
    
    if (lowerQuery.contains('exercise') || lowerQuery.contains('running') || lowerQuery.contains('workout')) {
      if (profile != null && profile.activityLevel == 'Athlete') {
        return 'As an athlete, you should be particularly cautious about air quality. Avoid strenuous outdoor exercise when:\n\n• PM10 > 80 µg/m³\n• AQI > 100\n• Early morning (6-9 AM) on weekdays due to traffic\n\nConsider indoor training alternatives during poor air quality days.';
      }
      return 'For outdoor exercise, optimal conditions are:\n\n• AQI below 50 (Good)\n• Early morning or late evening\n• Away from traffic areas\n\nAvoid intense workouts when AQI exceeds 100. Light activities may be okay up to AQI 150, but monitor how you feel.';
    }
    
    if (lowerQuery.contains('children') || lowerQuery.contains('kids')) {
      return 'Children are more vulnerable to air pollution because:\n\n1. Their lungs are still developing\n2. They breathe more air per body weight\n3. They\'re often more active outdoors\n\nKeep children indoors when AQI exceeds 100. For sensitive children, consider limiting outdoor play when AQI > 50.';
    }
    
    if (lowerQuery.contains('pm2.5') || lowerQuery.contains('pm 2.5')) {
      return 'PM2.5 refers to fine particulate matter less than 2.5 micrometers in diameter. These tiny particles can:\n\n• Penetrate deep into lungs\n• Enter bloodstream\n• Cause respiratory and cardiovascular issues\n\nSafe levels: Below 12 µg/m³ (AQI 0-50)\nModerate: 12-35 µg/m³ (AQI 51-100)\nUnhealthy: Above 35 µg/m³';
    }
    
    if (lowerQuery.contains('mask') || lowerQuery.contains('protection')) {
      return 'For air pollution protection:\n\n• N95 or KN95 masks filter 95% of particles\n• Surgical masks offer minimal protection\n• Cloth masks are not effective for pollution\n\nWear N95 masks when:\n• AQI exceeds 150\n• PM2.5 > 55 µg/m³\n• You must go outside during poor air quality';
    }
    
    if (lowerQuery.contains('indoor') || lowerQuery.contains('ventilation')) {
      return 'Improving indoor air quality:\n\n1. Use HEPA air purifiers\n2. Keep windows closed during high pollution\n3. Ensure proper ventilation (CO2 < 1000 ppm)\n4. Use exhaust fans when cooking\n5. Avoid indoor smoking\n6. Regularly clean and vacuum\n\nIndoor air can be 2-5 times more polluted than outdoor air without proper measures.';
    }
    
    if (lowerQuery.contains('forecast') || lowerQuery.contains('predict')) {
      return 'Our ML-powered forecasts analyze:\n\n• Historical air quality patterns\n• Weather conditions\n• Traffic patterns\n• Seasonal trends\n• Industrial activity\n\nCheck the Forecast tab for 24-hour and 7-day predictions. This helps you plan outdoor activities in advance.';
    }
    
    if (lowerQuery.contains('heart') || lowerQuery.contains('elderly') || lowerQuery.contains('senior')) {
      return 'Elderly individuals and those with heart conditions are at higher risk. Recommendations:\n\n• Stay indoors when PM2.5 > 50 µg/m³\n• Take medications as prescribed\n• Monitor symptoms closely\n• Avoid outdoor activities during peak pollution hours\n• Keep emergency contacts readily available\n\nSeek immediate medical attention if experiencing chest pain or unusual shortness of breath.';
    }
    
    if (lowerQuery.contains('copd')) {
      return 'For COPD patients:\n\n• Stay indoors when PM2.5 > 30 µg/m³\n• Use prescribed inhalers regularly\n• Keep oxygen therapy equipment accessible\n• Avoid exposure to secondhand smoke\n• Monitor oxygen saturation levels\n\nCOPD exacerbations are strongly linked to air pollution. Extra caution is essential.';
    }
    
    final responses = [
      'Based on current air quality data, I recommend checking the Dashboard for real-time AQI levels in your area. This will help you make informed decisions about outdoor activities.',
      'Air quality can vary significantly by location and time. I suggest monitoring the Map view to see which areas have better air quality near you.',
      'Your health profile indicates specific sensitivities. Would you like personalized recommendations based on current air quality conditions?',
      'For the most accurate advice, please check the Forecast section which provides predictive analytics for the next 24 hours and 7 days.',
    ];
    
    return responses[_random.nextInt(responses.length)];
  }
}
