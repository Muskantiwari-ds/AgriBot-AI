import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  CardMedia,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fade,
} from '@mui/material';
import {
  Agriculture,
  CloudQueue,
  AttachMoney,
  Policy,
  Chat,
  CheckCircle,
  Translate,
  Speed,
  Security,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';

const Home = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  const features = [
    {
      icon: <Agriculture sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Crop Management',
      description: 'Get personalized crop recommendations, planting calendars, and care instructions based on your location and soil conditions.',
      path: '/crops',
      color: '#4CAF50'
    },
    {
      icon: <CloudQueue sx={{ fontSize: 48, color: 'info.main' }} />,
      title: 'Weather Intelligence',
      description: 'Access real-time weather data, forecasts, and agricultural advisories to make informed farming decisions.',
      path: '/weather',
      color: '#2196F3'
    },
    {
      icon: <AttachMoney sx={{ fontSize: 48, color: 'warning.main' }} />,
      title: 'Financial Guidance',
      description: 'Explore loan options, insurance schemes, subsidies, and market prices for your agricultural needs.',
      path: '/finance',
      color: '#FF9800'
    },
    {
      icon: <Policy sx={{ fontSize: 48, color: 'secondary.main' }} />,
      title: 'Government Policies',
      description: 'Stay updated with latest government schemes, policies, and application processes for farmers.',
      path: '/policies',
      color: '#9C27B0'
    }
  ];

  const benefits = [
    {
      icon: <Translate />,
      title: 'Multilingual Support',
      description: 'Available in Hindi, English, and 10+ Indian regional languages'
    },
    {
      icon: <Speed />,
      title: 'Real-time Insights',
      description: 'Get instant responses powered by advanced AI and current data'
    },
    {
      icon: <Security />,
      title: 'Reliable Information',
      description: 'All recommendations backed by verified agricultural data sources'
    },
    {
      icon: <CheckCircle />,
      title: 'Expert Guidance',
      description: 'AI-powered advice equivalent to consulting agricultural experts'
    }
  ];

  const stats = [
    { number: '50K+', label: 'Farmers Helped' },
    { number: '10+', label: 'Languages Supported' },
    { number: '1000+', label: 'Queries Daily' },
    { number: '95%', label: 'Accuracy Rate' }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%)',
          color: 'white',
          py: 12,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Typography
                  variant="h1"
                  sx={{
                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                    fontWeight: 700,
                    mb: 2,
                    lineHeight: 1.2
                  }}
                >
                  AgriBot AI
                </Typography>
                <Typography
                  variant="h5"
                  sx={{
                    fontSize: { xs: '1.2rem', md: '1.5rem' },
                    mb: 4,
                    opacity: 0.9
                  }}
                >
                  Your Intelligent Agricultural Advisor
                </Typography>
                <Typography variant="body1" sx={{ fontSize: '1.1rem', mb: 4, maxWidth: '500px' }}>
                  Get instant, expert advice on crops, weather, finances, and government policies. 
                  Available in your local language, powered by advanced AI.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/chat')}
                    sx={{
                      bgcolor: 'white',
                      color: 'primary.main',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      '&:hover': {
                        bgcolor: 'grey.100'
                      }
                    }}
                    startIcon={<Chat />}
                  >
                    Start Chatting
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/about')}
                    sx={{
                      borderColor: 'white',
                      color: 'white',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      '&:hover': {
                        borderColor: 'white',
                        bgcolor: 'rgba(255,255,255,0.1)'
                      }
                    }}
                  >
                    Learn More
                  </Button>
                </Box>
              </motion.div>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <Box
                  sx={{
                    position: 'relative',
                    textAlign: 'center'
                  }}
                >
                  <img
                    src="/api/placeholder/500/400"
                    alt="Farmer using technology"
                    style={{
                      width: '100%',
                      maxWidth: '500px',
                      height: 'auto',
                      borderRadius: '12px',
                      boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
                    }}
                  />
                </Box>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Grid container spacing={3}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Paper
                  elevation={2}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    borderTop: 3,
                    borderColor: 'primary.main'
                  }}
                >
                  <Typography
                    variant="h3"
                    sx={{
                      fontSize: { xs: '1.8rem', md: '2.5rem' },
                      fontWeight: 700,
                      color: 'primary.main',
                      mb: 1
                    }}
                  >
                    {stat.number}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Paper>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={6}>
            <Typography
              variant="h2"
              sx={{
                fontSize: { xs: '2rem', md: '2.75rem' },
                fontWeight: 600,
                mb: 2,
                color: 'text.primary'
              }}
            >
              Our Services
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: '600px', mx: 'auto' }}>
              Comprehensive agricultural guidance powered by AI and real-time data
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  style={{ height: '100%' }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        boxShadow: 6,
                        transform: 'translateY(-4px)'
                      }
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                      <Box mb={2}>
                        {feature.icon}
                      </Box>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 600,
                          mb: 2,
                          color: 'text.primary'
                        }}
                      >
                        {feature.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {feature.description}
                      </Typography>
                      <Chip
                        label="AI Powered"
                        size="small"
                        sx={{
                          bgcolor: feature.color,
                          color: 'white',
                          fontWeight: 500
                        }}
                      />
                    </CardContent>
                    <CardActions sx={{ p: 2, pt: 0 }}>
                      <Button
                        size="medium"
                        onClick={() => navigate(feature.path)}
                        sx={{
                          width: '100%',
                          fontWeight: 500
                        }}
                      >
                        Explore
                      </Button>
                    </CardActions>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Benefits Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box textAlign="center" mb={6}>
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '2.75rem' },
              fontWeight: 600,
              mb: 2
            }}
          >
            Why Choose AgriBot AI?
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: '600px', mx: 'auto' }}>
            Built specifically for Indian farmers with cutting-edge technology
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {benefits.map((benefit, index) => (
            <Grid item xs={12} sm={6} key={index}>
              <motion.div
                initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 3,
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 3,
                    transition: 'box-shadow 0.2s',
                    '&:hover': {
                      boxShadow: 3
                    }
                  }}
                >
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: 'primary.light',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {benefit.icon}
                  </Box>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {benefit.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {benefit.description}
                    </Typography>
                  </Box>
                </Paper>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 8,
          textAlign: 'center'
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Typography
              variant="h3"
              sx={{
                fontSize: { xs: '1.8rem', md: '2.5rem' },
                fontWeight: 600,
                mb: 2
              }}
            >
              Ready to Transform Your Farming?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              Join thousands of farmers already using AgriBot AI for smarter agricultural decisions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/chat')}
                sx={{
                  bgcolor: 'white',
                  color: 'primary.main',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  '&:hover': {
                    bgcolor: 'grey.100'
                  }
                }}
                startIcon={<Chat />}
              >
                Start Your First Query
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/weather')}
                sx={{
                  borderColor: 'white',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  '&:hover': {
                    borderColor: 'white',
                    bgcolor: 'rgba(255,255,255,0.1)'
                  }
                }}
                startIcon={<CloudQueue />}
              >
                Check Weather
              </Button>
            </Box>
          </motion.div>
        </Container>
      </Box>

      {/* Quick Access Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography
          variant="h4"
          sx={{
            textAlign: 'center',
            fontWeight: 600,
            mb: 4,
            color: 'text.primary'
          }}
        >
          Quick Access
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Popular Queries
              </Typography>
              <List dense>
                {[
                  'When should I plant wheat this season?',
                  'What is the weather forecast for my area?',
                  'How to apply for PM-KISAN scheme?',
                  'Current market price for rice?',
                  'Best fertilizer for cotton crop?'
                ].map((query, index) => (
                  <ListItem
                    key={index}
                    button
                    onClick={() => navigate('/chat', { state: { initialQuery: query } })}
                    sx={{
                      borderRadius: 1,
                      mb: 0.5,
                      '&:hover': {
                        bgcolor: 'grey.100'
                      }
                    }}
                  >
                    <ListItemIcon>
                      <CheckCircle color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={query} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Supported Languages
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {[
                  'English', 'हिंदी', 'বাংলা', 'தமிழ்', 'తెలుగు',
                  'मराठी', 'ગુજરાતી', 'ಕನ್ನಡ', 'മലയാളം', 'ਪੰਜਾਬੀ', 'اردو'
                ].map((lang, index) => (
                  <Chip
                    key={index}
                    label={lang}
                    variant="outlined"
                    sx={{
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      '&:hover': {
                        bgcolor: 'primary.light',
                        color: 'white'
                      }
                    }}
                  />
                ))}
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Ask questions in your preferred language and get responses in the same language.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Home;