import 'package:flutter/material.dart';
import 'package:airsense_5g/models/chat_message_model.dart';
import 'package:airsense_5g/services/auth_service.dart';
import 'package:airsense_5g/services/bytez_service.dart';

import 'package:intl/intl.dart';
import 'dart:io';

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
  String? _userImage;

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
    String? image;
    if (user != null) {
      image = await AuthService().getProfileImage(user.id);
    }
    if (user != null && mounted) {
      setState(() {
        _userId = user.id;
        _userImage = image;
      });
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

    try {
      final history = _messages
          .where((m) => m.message.isNotEmpty || m.response.isNotEmpty)
          .map((m) {
        if (m.isUser) {
          return {'role': 'user', 'content': m.message};
        } else {
          return {'role': 'assistant', 'content': m.response};
        }
      }).toList();

      final botResponse = await BytezService().sendMessage(history);

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
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            id: 'error_${DateTime.now().millisecondsSinceEpoch}',
            userId: 'system',
            message: '',
            response: 'Sorry, verification failed or service is unavailable.',
            timestamp: DateTime.now(),
            isUser: false,
          ));
          _isSending = false;
        });
      }
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
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        forceMaterialTransparency: true,
        backgroundColor: Colors
            .transparent, // Glassmorphism effect handled by body bg usually or transparent
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.purple.shade400, Colors.blue.shade400],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.purple.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  )
                ],
              ),
              child:
                  const Icon(Icons.auto_awesome, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('AirSense AI',
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold)),
                Row(
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                          color: Colors.greenAccent, shape: BoxShape.circle),
                    ),
                    const SizedBox(width: 4),
                    Text('Online',
                        style: Theme.of(context)
                            .textTheme
                            .bodySmall
                            ?.copyWith(color: Colors.grey)),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          // Subtle background gradient for premium feel
          gradient: LinearGradient(
            colors: [
              Theme.of(context).colorScheme.surface,
              Theme.of(context).colorScheme.surfaceContainer.withOpacity(0.5),
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Column(
          children: [
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.fromLTRB(
                    16, 100, 16, 16), // Top padding for AppBar
                itemCount: _messages.length + (_isSending ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index == _messages.length) {
                    return _buildTypingIndicator();
                  }
                  return ChatBubble(
                    message: _messages[index],
                    userImage: _userImage,
                  );
                },
              ),
            ),

            // Input Area
            SafeArea(
              top: false,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Column(
                  children: [
                    // Suggestions
                    SizedBox(
                      height: 40,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        itemCount: _suggestedQuestions.length,
                        separatorBuilder: (context, index) =>
                            const SizedBox(width: 8),
                        itemBuilder: (context, index) {
                          return ActionChip(
                            elevation: 0,
                            backgroundColor: Theme.of(context)
                                .colorScheme
                                .surfaceContainerHighest,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20)),
                            label: Text(_suggestedQuestions[index],
                                style: TextStyle(
                                    fontSize: 12,
                                    color: Theme.of(context)
                                        .colorScheme
                                        .onSurface)),
                            onPressed: () =>
                                _sendMessage(_suggestedQuestions[index]),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Input Field
                    Container(
                      decoration: BoxDecoration(
                        color: Theme.of(context)
                            .colorScheme
                            .surfaceContainerHighest
                            .withOpacity(0.6),
                        borderRadius: BorderRadius.circular(30),
                        border: Border.all(color: Colors.white10),
                      ),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 4, vertical: 2),
                      child: Row(
                        children: [
                          const SizedBox(width: 16),
                          Expanded(
                            child: TextField(
                              controller: _messageController,
                              style: TextStyle(
                                  color:
                                      Theme.of(context).colorScheme.onSurface),
                              decoration: const InputDecoration(
                                hintText: 'Ask anything...',
                                border: InputBorder.none,
                                isDense: true,
                              ),
                              textInputAction: TextInputAction.send,
                              onSubmitted: (_) => _sendMessage(),
                            ),
                          ),
                          Container(
                            margin: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: _isSending
                                    ? [Colors.grey, Colors.grey]
                                    : [
                                        Colors.purple.shade400,
                                        Colors.blue.shade400
                                      ],
                              ),
                              shape: BoxShape.circle,
                            ),
                            child: IconButton(
                              icon: const Icon(Icons.arrow_upward,
                                  color: Colors.white, size: 20),
                              onPressed:
                                  _isSending ? null : () => _sendMessage(),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildBotAvatar(),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(4),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: SizedBox(
              width: 40,
              height: 20,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildDot(0),
                  _buildDot(1),
                  _buildDot(2),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDot(int index) {
    return const CircleAvatar(radius: 3, backgroundColor: Colors.grey);
  }

  Widget _buildBotAvatar() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: Colors.black, // Dark background for bot
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white10),
      ),
      child:
          const Icon(Icons.auto_awesome, color: Colors.purpleAccent, size: 16),
    );
  }
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final String? userImage;

  const ChatBubble({super.key, required this.message, this.userImage});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    // final colorScheme = Theme.of(context).colorScheme; // Removed unused variable

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            _buildBotAvatar(),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                gradient: isUser
                    ? LinearGradient(
                        colors: [Colors.purple.shade600, Colors.blue.shade600],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      )
                    : null,
                color: isUser
                    ? null
                    : const Color(0xFF1E1E2C), // Dark grey for bot
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(isUser ? 20 : 4),
                  topRight: Radius.circular(isUser ? 4 : 20),
                  bottomLeft: const Radius.circular(20),
                  bottomRight: const Radius.circular(20),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 5,
                    offset: const Offset(0, 2),
                  )
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isUser ? message.message : message.response,
                    style: TextStyle(
                      color:
                          isUser ? Colors.white : Colors.white.withOpacity(0.9),
                      fontSize: 15,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    DateFormat('HH:mm').format(message.timestamp),
                    style: TextStyle(
                      color: isUser ? Colors.white54 : Colors.grey,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            _buildUserAvatar(context),
          ],
        ],
      ),
    );
  }

  Widget _buildBotAvatar() {
    return Container(
      width: 32,
      height: 32,
      margin: const EdgeInsets.only(top: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2C),
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white10),
      ),
      child:
          const Icon(Icons.auto_awesome, color: Colors.purpleAccent, size: 16),
    );
  }

  Widget _buildUserAvatar(BuildContext context) {
    if (userImage != null) {
      return CircleAvatar(
        radius: 16,
        backgroundImage: FileImage(File(userImage!)),
        backgroundColor: Colors.transparent,
      );
    }
    return CircleAvatar(
      radius: 16,
      backgroundColor: Colors.purple.withOpacity(0.2),
      child: const Icon(Icons.person, size: 16, color: Colors.purple),
    );
  }
}
