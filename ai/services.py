"""
AI services for emotion analysis and music recommendations.
"""
import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class HFClient:
    """Client for Hugging Face Inference API."""
    
    def __init__(self):
        self.api_token = settings.HUGGINGFACE_API_TOKEN
        self.emotion_model = "j-hartmann/emotion-english-distilroberta-base"
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Fallback advice templates by emotion
        self.advice_templates = {
            'joy': "You're feeling great! Consider sharing this positive energy with others or engaging in activities you love.",
            'sadness': "It's okay to feel sad sometimes. Try gentle activities like listening to music, taking a walk, or talking to someone you trust.",
            'anger': "Take a moment to breathe deeply. Consider what's causing this feeling and whether there's a constructive way to address it.",
            'fear': "Fear is natural. Break down what's worrying you into smaller, manageable steps. You're stronger than you think.",
            'surprise': "Unexpected moments can be opportunities for growth. Take time to process what happened and how you feel about it.",
            'disgust': "Strong negative feelings can be signals. Consider what boundaries you might need to set or changes you want to make.",
            'anxious': "Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8. Grounding exercises can also help.",
            'stressed': "Take a 5-minute break. Try progressive muscle relaxation or a short walk. Remember that stress is temporary.",
            'calm': "You're in a peaceful state. This is a great time for reflection, planning, or enjoying the present moment.",
            'excited': "Channel this positive energy into something meaningful. Consider activities that align with your goals and values.",
            'tired': "Rest is important for your wellbeing. Consider what your body and mind need - sleep, nutrition, or a mental break.",
            'content': "Contentment is a beautiful state. Take a moment to appreciate what's going well in your life right now.",
        }
    
    def analyze_emotion(self, text: str) -> Dict:
        """
        Analyze emotion in text using Hugging Face API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with 'label' and 'score' keys, or fallback data if API fails
        """
        if not self.api_token:
            logger.warning("Hugging Face API token not configured")
            return {
                'label': 'neutral',
                'score': 0.5,
                'ai_unavailable': True
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {'inputs': text}
            url = f"{self.base_url}/{self.emotion_model}"
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    # Format: [[{'label': 'LABEL_1', 'score': 0.9}]]
                    emotions = result[0]
                else:
                    # Format: [{'label': 'LABEL_1', 'score': 0.9}]
                    emotions = result
                
                # Get the highest confidence emotion
                top_emotion = max(emotions, key=lambda x: x['score'])
                
                return {
                    'label': top_emotion['label'].lower(),
                    'score': round(top_emotion['score'], 3)
                }
            
            # Fallback if unexpected format
            return {
                'label': 'neutral',
                'score': 0.5,
                'ai_unavailable': True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API error: {e}")
            return {
                'label': 'neutral',
                'score': 0.5,
                'ai_unavailable': True
            }
        except Exception as e:
            logger.error(f"Unexpected error in emotion analysis: {e}")
            return {
                'label': 'neutral',
                'score': 0.5,
                'ai_unavailable': True
            }
    
    def generate_advice(self, emotion_label: str, text: str = "") -> str:
        """
        Generate advice based on detected emotion.
        
        Args:
            emotion_label: Detected emotion label
            text: Original text (for context)
            
        Returns:
            Advice string
        """
        # Normalize emotion label
        emotion_key = emotion_label.lower()
        
        # Map some HF emotion labels to our advice templates
        emotion_mapping = {
            'admiration': 'joy',
            'amusement': 'joy',
            'approval': 'content',
            'caring': 'joy',
            'curiosity': 'excited',
            'desire': 'excited',
            'disappointment': 'sadness',
            'disapproval': 'anger',
            'embarrassment': 'anxious',
            'excitement': 'excited',
            'gratitude': 'content',
            'grief': 'sadness',
            'love': 'joy',
            'nervousness': 'anxious',
            'optimism': 'joy',
            'pride': 'content',
            'realization': 'surprise',
            'relief': 'calm',
            'remorse': 'sadness',
            'confusion': 'anxious',
        }
        
        # Get mapped emotion or use original
        advice_key = emotion_mapping.get(emotion_key, emotion_key)
        
        # Get advice template
        advice = self.advice_templates.get(
            advice_key,
            "Take a moment to acknowledge your feelings. Remember that all emotions are valid and temporary."
        )
        
        # Add disclaimer
        disclaimer = " Remember, this is general wellness advice and not a substitute for professional mental health support."
        
        return advice + disclaimer


class SpotifyRecommendationService:
    """Service for music recommendations based on mood."""
    
    def __init__(self):
        # Hardcoded playlist recommendations by mood
        self.mood_playlists = {
            'happy': [
                {'title': 'Feel Good Hits', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0'},
                {'title': 'Happy Pop', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC'},
            ],
            'sad': [
                {'title': 'Sad Songs', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1'},
                {'title': 'Melancholy Indie', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWX83CujKHHOn'},
            ],
            'anxious': [
                {'title': 'Calm & Peaceful', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWU0ScTcjJBdj'},
                {'title': 'Focus Flow', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ'},
            ],
            'stressed': [
                {'title': 'Stress Relief', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'},
                {'title': 'Ambient Relaxation', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX0SM0LYsmbMT'},
            ],
            'calm': [
                {'title': 'Peaceful Piano', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'},
                {'title': 'Nature Sounds', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWU0ScTcjJBdj'},
            ],
            'excited': [
                {'title': 'Energy Boost', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP'},
                {'title': 'Upbeat Pop', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC'},
            ],
            'angry': [
                {'title': 'Anger Management', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'},
                {'title': 'Calming Classical', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWU0ScTcjJBdj'},
            ],
            'energetic': [
                {'title': 'Workout Hits', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP'},
                {'title': 'High Energy', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DXdxcBWuJkbcy'},
            ],
            'tired': [
                {'title': 'Gentle Acoustic', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd'},
                {'title': 'Soft Rock', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U'},
            ],
            'content': [
                {'title': 'Chill Vibes', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd'},
                {'title': 'Sunday Morning', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWU0ScTcjJBdj'},
            ],
        }
    
    def get_recommendations(self, mood: str) -> List[Dict]:
        """
        Get music recommendations for a given mood.
        
        Args:
            mood: Mood string
            
        Returns:
            List of playlist dictionaries with 'title' and 'url'
        """
        mood_key = mood.lower()
        
        # Map some emotions to mood categories
        emotion_to_mood = {
            'joy': 'happy',
            'sadness': 'sad',
            'fear': 'anxious',
            'anger': 'angry',
            'surprise': 'excited',
            'disgust': 'angry',
        }
        
        # Get mapped mood or use original
        playlist_key = emotion_to_mood.get(mood_key, mood_key)
        
        # Return playlists or default calm playlists
        return self.mood_playlists.get(playlist_key, self.mood_playlists['calm'])