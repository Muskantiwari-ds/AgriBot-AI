import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Button,
  Grid,
  Card,
  CardContent,
  Rating,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Send,
  Mic,
  MicOff,
  Agriculture,
  SmartToy,
  ThumbUp,
  ThumbDown,
  ContentCopy,
  Share,
  Refresh,
  LocationOn,
  Language as LanguageIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-toastify';
import { useLocation } from 'react-router-dom';

import { useChatContext } from '../contexts/ChatContext';
import { useLanguage } from '../contexts/LanguageContext';
import { chatService } from '../services/chatService';
import MessageBubble from '../components/Chat/MessageBubble';
import TypingIndicator from '../components/Chat/TypingIndicator';
import SuggestionChips from '../components/Chat/SuggestionChips';
import VoiceInput from '../components/Chat/VoiceInput';

const Chat = () => {
  const location = useLocation();
  const { messages, addMessage, clearMessages, isTyping, setIsTyping } = useChatContext();
  const { currentLanguage, t } = useLanguage();
  
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [userLocation, setUserLocation] = useState('');
  const [feedbackDialog, setFeedbackDialog] = useState({ open: false, messageId: null });
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initial query from navigation state
  useEffect(() => {
    if (location.state?.initialQuery) {
      setInputValue(location.state.initialQuery);
      handleSendMessage(location.state.initialQuery);
    }
  }, [location.state]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // In a real app, you'd reverse geocode these coordinates
          setUserLocation(`${position.coords.latitude.toFixed(2)}, ${position.coords.longitude.toFixed(2)}`);
        },
        (error) => {
          console.log('Location access denied');
        }
      );
    }
  }, []);

  const handleSendMessage = async (messageText = inputValue.trim()) => {
    if (!messageText) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date(),
      language: currentLanguage
    };
    addMessage(userMessage);

    // Clear input and show typing indicator
    setInputValue('');
    setIsTyping(true);

    try {
      // Call chat service
      const response = await chatService.sendMessage({
        query: messageText,
        location: userLocation,
        language: currentLanguage
      });

      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        text: response.answer,
        sender: 'ai',
        timestamp: new Date(),
        agentType: response.agent_type,
        sources: response.sources || [],
        suggestions: response.suggestions || [],
        confidence: response.confidence_score,
        processingTime: response.processing_time,
        language: response.language
      };
      addMessage(aiMessage);

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        text: 'I apologize, but I\'m having trouble processing your request right now. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
        isError: true
      };
      addMessage(errorMessage);
      
      toast.error('Failed to get response. Please try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceInput = (transcript) => {
    setInputValue(transcript);
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleFeedback = async (messageId, isPositive) => {
    if (!isPositive) {
      setFeedbackDialog({ open: true, messageId });
    } else {
      try {
        await chatService.submitFeedback({
          messageId,
          rating: 5,
          isHelpful: true
        });
        toast.success('Thank you for your feedback!');
      } catch (error) {
        toast.error('Failed to submit feedback');
      }
    }
  };

  const handleFeedbackSubmit = async () => {
    try {
      await chatService.submitFeedback({
        messageId: feedbackDialog.messageId,
        rating,
        feedbackText,
        isHelpful: rating >= 3
      });
      
      setFeedbackDialog({ open: false, messageId: null });
      setRating(0);
      setFeedbackText('');
      toast.success('Thank you for your feedback!');
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const quickActions = [
    { text: 'Weather forecast for my area', icon: '🌤️' },
    { text: 'Best crops for this season', icon: '🌾' },
    { text: 'Government schemes for farmers', icon: '🏛️' },
    { text: 'Market prices for wheat', icon: '💰' },
    { text: 'Irrigation schedule advice', icon: '💧' },
    { text: 'Pest control for cotton', icon: '🐛' }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 3, height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      <Grid container spacing={3} sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {/* Main Chat Area */}
        <Grid item xs={12} md={8}>
          <Paper
            elevation={2}
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 2
            }}
          >
            {/* Chat Header */}
            <Box
              sx={{
                p: 2,
                borderBottom: 1,
                borderColor: 'divider',
                background: 'linear-gradient(45deg, #2E7D32, #4CAF50)',
                color: 'white',
                borderRadius: '8px 8px 0 0'
              }}
            >
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center" gap={1}>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <SmartToy />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      AgriBot AI Assistant
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Your agricultural advisor • Online
                    </Typography>
                  </Box>
                </Box>
                
                <Box display="flex" gap={1}>
                  {userLocation && (
                    <Tooltip title={`Location: ${userLocation}`}>
                      <Chip
                        icon={<LocationOn />}
                        label="Located"
                        size="small"
                        sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                      />
                    </Tooltip>
                  )}
                  <Chip
                    icon={<LanguageIcon />}
                    label={currentLanguage.toUpperCase()}
                    size="small"
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                  <Button
                    size="small"
                    onClick={clearMessages}
                    sx={{ color: 'white', minWidth: 'auto' }}
                  >
                    <Refresh />
                  </Button>
                </Box>
              </Box>
            </Box>

            {/* Messages Area */}
            <Box
              sx={{
                flexGrow: 1,
                overflow: 'auto',
                p: 2,
                bgcolor: '#fafafa'
              }}
            >
              {messages.length === 0 ? (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '100%',
                    textAlign: 'center'
                  }}
                >
                  <Agriculture sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                    Welcome to AgriBot AI!
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
                    I'm here to help you with all your agricultural questions. Ask me about crops, weather, finances, or government policies.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Try asking: "What should I plant this season?" or "What's the weather like?"
                  </Typography>
                </Box>
              ) : (
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <MessageBubble
                        message={message}
                        onFeedback={handleFeedback}
                        onCopy={copyToClipboard}
                        onSuggestionClick={handleSuggestionClick}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
              
              {isTyping && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </Box>

            {/* Input Area */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box display="flex" alignItems="end" gap={1}>
                <TextField
                  ref={inputRef}
                  fullWidth
                  multiline
                  maxRows={4}
                  placeholder="Ask me anything about farming, weather, crops, or policies..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isTyping}
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 3,
                      bgcolor: 'white'
                    }
                  }}
                />
                
                <VoiceInput
                  onTranscript={handleVoiceInput}
                  isListening={isListening}
                  setIsListening={setIsListening}
                />
                
                <IconButton
                  color="primary"
                  onClick={() => handleSendMessage()}
                  disabled={!inputValue.trim() || isTyping}
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': { bgcolor: 'primary.dark' },
                    '&:disabled': { bgcolor: 'grey.300' }
                  }}
                >
                  {isTyping ? <CircularProgress size={24} color="inherit" /> : <Send />}
                </IconButton>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
            {/* Quick Actions */}
            <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    startIcon={<span>{action.icon}</span>}
                    onClick={() => handleSendMessage(action.text)}
                    sx={{
                      justifyContent: 'flex-start',
                      textAlign: 'left',
                      borderRadius: 2,
                      textTransform: 'none'
                    }}
                    fullWidth
                  >
                    {action.text}
                  </Button>
                ))}
              </Box>
            </Paper>

            {/* Current Suggestions */}
            {messages.length > 0 && messages[messages.length - 1]?.suggestions?.length > 0 && (
              <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Suggestions
                </Typography>
                <SuggestionChips
                  suggestions={messages[messages.length - 1].suggestions}
                  onSuggestionClick={handleSuggestionClick}
                />
              </Paper>
            )}

            {/* Help & Tips */}
            <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Tips
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                • Be specific with your location for better recommendations
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                • Ask follow-up questions for detailed guidance
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                • Use voice input for hands-free operation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Available in 11+ Indian languages
              </Typography>
            </Paper>
          </Box>
        </Grid>
      </Grid>

      {/* Feedback Dialog */}
      <Dialog
        open={feedbackDialog.open}
        onClose={() => setFeedbackDialog({ open: false, messageId: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Help us improve</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Your feedback helps us provide better responses. Please rate your experience:
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography component="legend" sx={{ mb: 1 }}>
              Overall Rating
            </Typography>
            <Rating
              value={rating}
              onChange={(event, newValue) => setRating(newValue)}
              size="large"
            />
          </Box>
          
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Additional feedback (optional)"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="Tell us what went wrong or how we can improve..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialog({ open: false, messageId: null })}>
            Cancel
          </Button>
          <Button
            onClick={handleFeedbackSubmit}
            variant="contained"
            disabled={rating === 0}
          >
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Chat;