import 'package:flutter/material.dart';
import 'package:airsense_5g/models/chat_message_model.dart';
import 'package:airsense_5g/services/auth_service.dart';

import 'package:airsense_5g/theme.dart';
import 'package:intl/intl.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isSending = false;
  String? _userId;

  final List<String> _suggestedQuestions = [
    "What is the weather today?",
    "Is the air quality safe?",
    "Health recommendations?",
    "Show pollutant levels",
  ];

  @override
  void initState() {
    super.initState();
    _loadUser();
    _addWelcomeMessage();
  }

  Future<void> _loadUser() async {
    final user = await AuthService().getCurrentUser();
    if (user != null && mounted) {
      setState(() => _userId = user.id);
    }
  }

  void _addWelcomeMessage() {
    _messages.add(ChatMessage(
      id: 'welcome',
      userId: 'system',
      message: '',
      response:
          'Hello! I\'m your AirSense AI assistant. How can I assist you today?',
      timestamp: DateTime.now(),
      isUser: false,
    ));
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage([String? text]) async {
    final messageText = text ?? _messageController.text.trim();
    if (messageText.isEmpty) return;

    if (text == null) _messageController.clear();

    setState(() {
      _messages.add(ChatMessage(
        id: 'user_${DateTime.now().millisecondsSinceEpoch}',
        userId: _userId ?? 'guest',
        message: messageText,
        response: '',
        timestamp: DateTime.now(),
        isUser: true,
      ));
      _isSending = true;
    });

    _scrollToBottom();

    // Simulate AI thinking delay
    await Future.delayed(const Duration(milliseconds: 1000));

    final botResponse = _getBotResponse(messageText);

    if (mounted) {
      setState(() {
        _messages.add(ChatMessage(
          id: 'bot_${DateTime.now().millisecondsSinceEpoch}',
          userId: 'system',
          message: '',
          response: botResponse,
          timestamp: DateTime.now(),
          isUser: false,
        ));
        _isSending = false;
      });
      _scrollToBottom();
    }
  }

  String _getBotResponse(String query) {
    final q = query.toLowerCase();
    if (q.contains("weather")) {
      return "The weather is currently sunny with a temperature of 25°C. Humidity is at 60%.";
    } else if (q.contains("safe") || q.contains("quality")) {
      return "The current Air Quality Index (AQI) is around 156, which is Unhealthy. It is advisable to wear a mask outdoors.";
    } else if (q.contains("health") || q.contains("recommendation")) {
      return "1. Avoid outdoor activities.\n2. Wear an N95 mask.\n3. Keep windows closed.\n4. Use an air purifier if available.";
    } else if (q.contains("pollutant")) {
      return "Main pollutants today:\n• PM2.5: High\n• PM10: Moderate\n• NO2: Good";
    } else {
      return "I'm focusing on air quality data right now. Try determining the weather or checking health tips!";
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                  color: colorScheme.primaryContainer, shape: BoxShape.circle),
              child:
                  Icon(Icons.smart_toy, color: colorScheme.primary, size: 20),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('AI Assistant',
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold)),
                Text('Online',
                    style: Theme.of(context)
                        .textTheme
                        .bodySmall
                        ?.copyWith(color: Colors.greenAccent)),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: AppSpacing.paddingMd,
              itemCount: _messages.length,
              itemBuilder: (context, index) =>
                  ChatBubble(message: _messages[index]),
            ),
          ),
          if (_isSending)
            Padding(
              padding: AppSpacing.paddingMd,
              child: Row(
                children: [
                  SizedBox(
                      height: 16,
                      width: 16,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: colorScheme.primary)),
                  const SizedBox(width: 8),
                  Text('Typing...',
                      style: TextStyle(
                          color: colorScheme.onSurfaceVariant, fontSize: 12)),
                ],
              ),
            ),
          // Suggested Questions Chips
          Container(
            height: 50,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _suggestedQuestions.length,
              separatorBuilder: (context, index) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                return ActionChip(
                  backgroundColor: colorScheme.surfaceContainerHighest,
                  labelStyle: TextStyle(color: colorScheme.primary),
                  side: BorderSide(color: colorScheme.primary.withOpacity(0.3)),
                  label: Text(_suggestedQuestions[index]),
                  onPressed: () => _sendMessage(_suggestedQuestions[index]),
                );
              },
            ),
          ),
          Container(
            padding: AppSpacing.paddingMd,
            decoration: BoxDecoration(
                color: colorScheme.surface,
                border: Border(
                    top: BorderSide(
                        color: colorScheme.outline.withOpacity(0.2)))),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      style: TextStyle(color: colorScheme.onSurface),
                      decoration: InputDecoration(
                        hintText: 'Ask specific questions...',
                        hintStyle: TextStyle(
                            color:
                                colorScheme.onSurfaceVariant.withOpacity(0.7)),
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(AppRadius.lg),
                            borderSide: BorderSide.none),
                        filled: true,
                        fillColor: colorScheme.surfaceContainerHighest,
                        contentPadding: AppSpacing.paddingMd,
                      ),
                      maxLines: 1,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    decoration: BoxDecoration(
                        color: colorScheme.primary, shape: BoxShape.circle),
                    child: IconButton(
                      icon: Icon(Icons.send, color: colorScheme.onPrimary),
                      onPressed: _isSending ? null : () => _sendMessage(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final displayText = isUser ? message.message : message.response;
    final colorScheme = Theme.of(context).colorScheme;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: AppSpacing.paddingMd,
        constraints:
            BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isUser
              ? colorScheme.primary
              : colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              displayText,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color:
                        isUser ? colorScheme.onPrimary : colorScheme.onSurface,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              DateFormat('HH:mm').format(message.timestamp),
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: isUser
                        ? colorScheme.onPrimary.withOpacity(0.7)
                        : colorScheme.onSurfaceVariant,
                    fontSize: 10,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
