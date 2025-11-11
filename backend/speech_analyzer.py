import speech_recognition as sr
import librosa
import numpy as np
import base64
import io
import wave
import json
import re
from typing import Dict, List, Optional
import os

class SpeechAnalyzer:
    def __init__(self):
        """Initialize speech analyzer with recognition engine"""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Common filler words
        self.filler_words = [
            'um', 'uh', 'ah', 'er', 'like', 'you know', 'i mean', 'basically',
            'actually', 'literally', 'sort of', 'kind of', 'right', 'okay',
            'so', 'well', 'now', 'then', 'just', 'really', 'very', 'quite'
        ]
        
        # Speech clarity parameters
        self.clarity_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.chunk_duration = 0.5  # seconds
        
    def is_ready(self) -> bool:
        """Check if speech analyzer is ready"""
        return self.recognizer is not None
    
    def analyze_audio(self, audio_data: str) -> Dict:
        """Analyze audio data for speech quality and content"""
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Convert to audio format
            audio = self._bytes_to_audio(audio_bytes)
            if audio is None:
                return self._get_default_results()
            
            # Perform analysis
            speech_text = self._speech_to_text(audio)
            clarity_score = self._analyze_clarity(audio)
            filler_words = self._detect_filler_words(speech_text)
            fluency_score = self._analyze_fluency(audio, speech_text)
            tone_analysis = self._analyze_tone(audio)
            
            return {
                'clarity_score': clarity_score,
                'fluency_score': fluency_score,
                'filler_words': filler_words,
                'speech_text': speech_text,
                'tone_analysis': tone_analysis,
                'word_count': len(speech_text.split()) if speech_text else 0,
                'speaking_rate': self._calculate_speaking_rate(audio, speech_text)
            }
            
        except Exception as e:
            print(f"Error analyzing audio: {e}")
            return self._get_default_results()
    
    def _bytes_to_audio(self, audio_bytes: bytes) -> Optional[sr.AudioData]:
        """Convert bytes to AudioData object"""
        try:
            # Try to read as WAV file
            with io.BytesIO(audio_bytes) as audio_io:
                with wave.open(audio_io, 'rb') as wav_file:
                    # Get audio parameters
                    frames = wav_file.readframes(wav_file.getnframes())
                    sample_rate = wav_file.getframerate()
                    sample_width = wav_file.getsampwidth()
                    channels = wav_file.getnchannels()
                    
                    # Convert to AudioData
                    audio_data = sr.AudioData(frames, sample_rate, sample_width)
                    return audio_data
                    
        except Exception as e:
            print(f"Error converting bytes to audio: {e}")
            return None
    
    def _speech_to_text(self, audio: sr.AudioData) -> str:
        """Convert speech to text using Google Speech Recognition"""
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return ""
        except Exception as e:
            print(f"Error in speech to text: {e}")
            return ""
    
    def _analyze_clarity(self, audio: sr.AudioData) -> float:
        """Analyze speech clarity based on audio characteristics"""
        try:
            # Convert AudioData to numpy array
            audio_array = np.frombuffer(audio.frame_data, dtype=np.int16)
            
            # Calculate signal-to-noise ratio (simplified)
            signal_power = np.mean(audio_array ** 2)
            noise_floor = np.percentile(audio_array ** 2, 10)
            
            if noise_floor > 0:
                snr = 10 * np.log10(signal_power / noise_floor)
                # Normalize SNR to 0-1 range (typical SNR range: 0-60 dB)
                clarity_score = min(1.0, max(0.0, snr / 60.0))
            else:
                clarity_score = 0.5
            
            # Additional clarity factors
            # 1. Volume consistency
            volume_std = np.std(audio_array)
            volume_score = 1.0 - min(1.0, volume_std / 10000)
            
            # 2. Frequency distribution (speech typically 85-255 Hz)
            if len(audio_array) > 0:
                # Simple frequency analysis
                fft = np.fft.fft(audio_array)
                freqs = np.fft.fftfreq(len(audio_array), 1/audio.sample_rate)
                
                # Focus on speech frequency range
                speech_mask = (freqs >= 85) & (freqs <= 255)
                speech_power = np.sum(np.abs(fft[speech_mask]) ** 2)
                total_power = np.sum(np.abs(fft) ** 2)
                
                if total_power > 0:
                    frequency_score = speech_power / total_power
                else:
                    frequency_score = 0.5
            else:
                frequency_score = 0.5
            
            # Combine factors
            final_clarity = (clarity_score * 0.4 + volume_score * 0.3 + frequency_score * 0.3)
            return max(0.0, min(1.0, final_clarity))
            
        except Exception as e:
            print(f"Error analyzing clarity: {e}")
            return 0.5
    
    def _detect_filler_words(self, text: str) -> List[Dict]:
        """Detect filler words in speech text"""
        try:
            if not text:
                return []
            
            detected_fillers = []
            words = text.lower().split()
            
            for i, word in enumerate(words):
                if word in self.filler_words:
                    detected_fillers.append({
                        'word': word,
                        'position': i,
                        'context': ' '.join(words[max(0, i-2):min(len(words), i+3)])
                    })
            
            return detected_fillers
            
        except Exception as e:
            print(f"Error detecting filler words: {e}")
            return []
    
    def _analyze_fluency(self, audio: sr.AudioData, text: str) -> float:
        """Analyze speech fluency"""
        try:
            if not text:
                return 0.0
            
            # Calculate speaking rate
            duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
            word_count = len(text.split())
            
            if duration > 0:
                words_per_minute = (word_count / duration) * 60
                
                # Optimal speaking rate is 120-160 WPM
                if 120 <= words_per_minute <= 160:
                    rate_score = 1.0
                elif 100 <= words_per_minute <= 180:
                    rate_score = 0.8
                elif 80 <= words_per_minute <= 200:
                    rate_score = 0.6
                else:
                    rate_score = 0.3
            else:
                rate_score = 0.5
            
            # Analyze pauses
            pause_score = self._analyze_pauses(audio)
            
            # Analyze filler word frequency
            filler_count = len(self._detect_filler_words(text))
            filler_ratio = filler_count / max(1, word_count)
            
            if filler_ratio < 0.05:  # Less than 5% filler words
                filler_score = 1.0
            elif filler_ratio < 0.1:  # Less than 10% filler words
                filler_score = 0.7
            elif filler_ratio < 0.15:  # Less than 15% filler words
                filler_score = 0.5
            else:
                filler_score = 0.2
            
            # Combine scores
            fluency_score = (rate_score * 0.4 + pause_score * 0.3 + filler_score * 0.3)
            return max(0.0, min(1.0, fluency_score))
            
        except Exception as e:
            print(f"Error analyzing fluency: {e}")
            return 0.5
    
    def _analyze_pauses(self, audio: sr.AudioData) -> float:
        """Analyze pause patterns in speech"""
        try:
            audio_array = np.frombuffer(audio.frame_data, dtype=np.int16)
            
            # Calculate energy envelope
            frame_length = int(self.chunk_duration * audio.sample_rate)
            energy = []
            
            for i in range(0, len(audio_array), frame_length):
                frame = audio_array[i:i+frame_length]
                if len(frame) > 0:
                    energy.append(np.mean(frame ** 2))
            
            if not energy:
                return 0.5
            
            energy = np.array(energy)
            
            # Detect pauses (low energy segments)
            energy_threshold = np.percentile(energy, 30)
            pause_frames = energy < energy_threshold
            
            # Calculate pause metrics
            pause_ratio = np.sum(pause_frames) / len(pause_frames)
            
            # Optimal pause ratio is 10-20%
            if 0.1 <= pause_ratio <= 0.2:
                pause_score = 1.0
            elif 0.05 <= pause_ratio <= 0.3:
                pause_score = 0.7
            elif 0.02 <= pause_ratio <= 0.4:
                pause_score = 0.5
            else:
                pause_score = 0.2
            
            return pause_score
            
        except Exception as e:
            print(f"Error analyzing pauses: {e}")
            return 0.5
    
    def _analyze_tone(self, audio: sr.AudioData) -> Dict:
        """Analyze speech tone and pitch"""
        try:
            audio_array = np.frombuffer(audio.frame_data, dtype=np.int16)
            
            # Convert to float and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Calculate pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio_float, sr=audio.sample_rate)
            
            # Get dominant pitch
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if not pitch_values:
                return {
                    'average_pitch': 0,
                    'pitch_variation': 0,
                    'tone_confidence': 0.5
                }
            
            average_pitch = np.mean(pitch_values)
            pitch_variation = np.std(pitch_values)
            
            # Analyze tone confidence based on pitch consistency
            pitch_consistency = 1.0 - min(1.0, pitch_variation / 50.0)
            
            return {
                'average_pitch': float(average_pitch),
                'pitch_variation': float(pitch_variation),
                'tone_confidence': float(pitch_consistency)
            }
            
        except Exception as e:
            print(f"Error analyzing tone: {e}")
            return {
                'average_pitch': 0,
                'pitch_variation': 0,
                'tone_confidence': 0.5
            }
    
    def _calculate_speaking_rate(self, audio: sr.AudioData, text: str) -> float:
        """Calculate speaking rate in words per minute"""
        try:
            if not text:
                return 0.0
            
            duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
            word_count = len(text.split())
            
            if duration > 0:
                words_per_minute = (word_count / duration) * 60
                return float(words_per_minute)
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating speaking rate: {e}")
            return 0.0
    
    def _get_default_results(self) -> Dict:
        """Return default results when analysis fails"""
        return {
            'clarity_score': 0.0,
            'fluency_score': 0.0,
            'filler_words': [],
            'speech_text': '',
            'tone_analysis': {
                'average_pitch': 0,
                'pitch_variation': 0,
                'tone_confidence': 0.5
            },
            'word_count': 0,
            'speaking_rate': 0.0
        }
    
    def get_speech_feedback(self, analysis_results: Dict) -> List[str]:
        """Generate feedback based on speech analysis"""
        feedback = []
        
        clarity_score = analysis_results.get('clarity_score', 0)
        fluency_score = analysis_results.get('fluency_score', 0)
        filler_words = analysis_results.get('filler_words', [])
        speaking_rate = analysis_results.get('speaking_rate', 0)
        
        # Clarity feedback
        if clarity_score < 0.5:
            feedback.append("Speak more clearly and enunciate your words")
        elif clarity_score < 0.7:
            feedback.append("Try to improve your pronunciation and articulation")
        
        # Fluency feedback
        if fluency_score < 0.5:
            feedback.append("Work on speaking more fluently and reducing pauses")
        elif fluency_score < 0.7:
            feedback.append("Practice speaking at a consistent pace")
        
        # Filler word feedback
        if len(filler_words) > 5:
            feedback.append("Reduce the use of filler words like 'um', 'uh', 'like'")
        elif len(filler_words) > 2:
            feedback.append("Try to minimize filler words in your speech")
        
        # Speaking rate feedback
        if speaking_rate < 100:
            feedback.append("Try to speak a bit faster to maintain engagement")
        elif speaking_rate > 180:
            feedback.append("Slow down your speech for better clarity")
        
        if not feedback:
            feedback.append("Excellent speech quality! Keep up the good work.")
        
        return feedback