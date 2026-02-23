from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg
from feedback.models import Feedback, WeeklyFeedbackSummary
from employees.models import Employees
import re
from collections import Counter, defaultdict
from typing import List, Dict, Any
import json
import os
import requests
import time


class GroqAIAnalyzer:
    """
    Direct Groq API integration for intelligent feedback analysis
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 2.0
        
    def _call_groq_api(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Make API call to Groq with proper error handling"""
        if not self.api_key:
            return {"error": "GROQ_API_KEY not found in environment variables"}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR analyst specializing in employee feedback analysis. Always return valid JSON without any additional text or formatting."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    self.base_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        return {"error": "Rate limit exceeded after retries"}
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": "Request timeout"}
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": "Connection error"}
            except Exception as e:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": f"API call failed: {str(e)}"}
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extract and parse JSON from API response"""
        if not content:
            return {}
            
        try:
            # Clean the content
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
            return {}


# IntelligentFeedbackAnalyzer class :

class IntelligentFeedbackAnalyzer:
    def __init__(self):
        self.groq_analyzer = GroqAIAnalyzer()

    def generate_feedback_report(self, employee_name: str, individual_feedbacks: List[str]) -> Dict[str, Any]:
        """
        Generate intelligent feedback report using 100% Groq AI analysis
        """
        if not individual_feedbacks:
            return self._get_empty_report(employee_name)
        
        # Use AI analysis exclusively
        ai_report = self._generate_ai_weekly_summary(employee_name, individual_feedbacks)
        if ai_report and not ai_report.get("error"):
            return ai_report
        return self._get_empty_report(employee_name)


    def analyze_feedback_sentiment_spans(self, feedback_text: str) -> Dict[str, Any]:
        """
        Analyze individual feedback using 100% GROQ AI for sentiment highlighting
        """
        if not feedback_text or not feedback_text.strip():
            return {"sentiment_spans": [], "overall_sentiment": "neutral"}
        
        try:
            prompt = f"""
            Analyze this feedback text and identify specific phrases with their sentiment for text highlighting.

            FEEDBACK TEXT: "{feedback_text}"

            Return JSON in this exact format:
            {{
                "sentiment_spans": [
                    {{
                        "text": "exact phrase from original text",
                        "sentiment": "positive|negative|improvement",
                        "start_index": 0,
                        "end_index": 15,
                        "reason": "brief reason for classification"
                    }}
                ],
                "overall_sentiment": "positive|neutral|negative"
            }}

            CRITICAL RULES:
            - "positive": praise, strengths, achievements, positive adjectives
            - "negative": criticism, problems, weaknesses, negative issues  
            - "improvement": suggestions, areas to work on, constructive feedback
            - Return EXACT text from the original (case-sensitive)
            - Calculate accurate character indices (start_index, end_index)
            - Each span should be 2-8 words typically
            - Be precise and avoid overlapping spans
            - Cover all significant sentiment-bearing phrases
            - "reason" should be very brief (3-5 words)

            Use intelligent NLP understanding, not just keyword matching.

            Return ONLY the JSON object.
            """
            
            response = self.groq_analyzer._call_groq_api(prompt, max_tokens=800)
            
            if "error" in response:
                return {"sentiment_spans": [], "overall_sentiment": "neutral", "error": response["error"]}
            
            choices = response.get("choices", [])
            content = choices[0].get("message", {}).get("content") if choices else None
            
            if content:
                parsed_sentiment = self.groq_analyzer._extract_json_from_response(content)
                if parsed_sentiment and "sentiment_spans" in parsed_sentiment:
                    # Validate and clean the spans
                    validated_spans = self._validate_sentiment_spans(parsed_sentiment["sentiment_spans"], feedback_text)
                    return {
                        "sentiment_spans": validated_spans,
                        "overall_sentiment": parsed_sentiment.get("overall_sentiment", "neutral")
                    }
            
            return {"sentiment_spans": [], "overall_sentiment": "neutral", "error": "Failed to parse AI response"}
            
        except Exception as e:
            return {"sentiment_spans": [], "overall_sentiment": "neutral", "error": str(e)}

    def analyze_multiple_feedbacks_sentiment(self, feedbacks: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple feedbacks using 100% GROQ AI
        """
        results = []
        
        for i, feedback in enumerate(feedbacks):
            if feedback and feedback.strip():
                sentiment_data = self.analyze_feedback_sentiment_spans(feedback)
                results.append({
                    "feedback_text": feedback,
                    "sentiment_analysis": sentiment_data
                })
            else:
                results.append({
                    "feedback_text": feedback,
                    "sentiment_analysis": {"sentiment_spans": [], "overall_sentiment": "neutral"}
                })
        
        return results


    def _generate_ai_weekly_summary(self, employee_name: str, feedbacks: List[str]) -> Dict[str, Any]:
        """Generate weekly summary using 100% Groq AI"""
        try:
            # Prepare feedback context for AI
            feedback_context = self._prepare_feedback_context(feedbacks)
            
            prompt = f"""
            Analyze the following weekly feedbacks for {employee_name} and generate a comprehensive summary report using intelligent NLP understanding.

            FEEDBACKS TO ANALYZE:
            {feedback_context}

            Generate a structured JSON report with this exact format:

            {{
                "employee_name": "{employee_name}",
                "sections": {{
                    "header": "Weekly Performance Summary - {employee_name}",
                    "areas_of_improvement": {{
                        "title": "Areas of Improvement:",
                        "items": [
                            "3-4 specific, actionable improvement areas based on intelligent analysis of feedback patterns",
                            "Focus on recurring themes and concrete suggestions",
                            "Provide clear, implementable recommendations"
                        ]
                    }},
                    "positives": {{
                        "title": "Positives:",
                        "items": [
                            "3-4 key strengths and positive patterns observed across feedbacks",
                            "Highlight consistent positive feedback areas",
                            "Mention specific achievements or behaviors praised"
                        ]
                    }},
                    "negatives": {{
                        "title": "Negatives:",
                        "items": [
                            "2-3 specific concerns or negative patterns identified",
                            "Focus on actionable negative feedback",
                            "Be constructive and specific"
                        ]
                    }},
                    "conclusion": {{
                        "title": "",
                        "content": "Comprehensive summary paragraph (4-5 sentences) that synthesizes all feedback using intelligent analysis, highlights main achievements, identifies key growth areas, and provides constructive forward-looking guidance."
                    }}
                }}
            }}

            Use intelligent NLP analysis to:
            - Understand context and nuance in feedback
            - Identify patterns and themes across multiple feedbacks  
            - Extract meaningful insights beyond simple keyword matching
            - Provide nuanced, contextual understanding of feedback

            Return ONLY the JSON object.
            """
            
            response = self.groq_analyzer._call_groq_api(prompt, max_tokens=1200)
            
            if "error" in response:
                return {"error": response["error"]}
            
            choices = response.get("choices", [])
            content = choices[0].get("message", {}).get("content") if choices else None
            
            if content:
                parsed_report = self.groq_analyzer._extract_json_from_response(content)
                if parsed_report and "sections" in parsed_report:
                    return parsed_report
            
            return {"error": "Failed to parse AI response"}
            
        except Exception as e:
            return {"error": str(e)}

    # KEEP ONLY AI-RELATED HELPER METHODS
    def _prepare_feedback_context(self, feedbacks: List[str]) -> str:
        """Prepare feedback context for AI analysis"""
        context_parts = []
        
        for i, feedback in enumerate(feedbacks[:15], 1):  # Limit to avoid token limits
            if feedback and feedback.strip():
                truncated_feedback = feedback[:300] + "..." if len(feedback) > 300 else feedback
                context_parts.append(f"Feedback {i}: {truncated_feedback}")
        
        return "\n\n".join(context_parts) if context_parts else "No specific feedback content available."

    def _validate_sentiment_spans(self, spans: List[Dict], original_text: str) -> List[Dict]:
        """Validate sentiment spans against original text"""
        validated_spans = []
        
        for span in spans:
            try:
                span_text = span.get("text", "")
                start_index = span.get("start_index", 0)
                end_index = span.get("end_index", 0)
                sentiment = span.get("sentiment", "neutral")
                
                if (span_text and 
                    sentiment in ["positive", "negative", "improvement"] and
                    start_index >= 0 and 
                    end_index > start_index and
                    end_index <= len(original_text)):
                    
                    actual_text = original_text[start_index:end_index]
                    if span_text.strip() == actual_text.strip():
                        validated_spans.append(span)
                    else:
                        found_index = original_text.find(span_text)
                        if found_index != -1:
                            validated_spans.append({
                                "text": span_text,
                                "sentiment": sentiment,
                                "start_index": found_index,
                                "end_index": found_index + len(span_text),
                                "reason": span.get("reason", "")
                            })
                
            except Exception as e:
                continue
                
        return validated_spans

    def _get_empty_report(self, employee_name: str) -> Dict[str, Any]:
        """Return empty report structure when no feedback available"""
        return {
            "employee_name": employee_name,
            "sections": {
                "header": f"{employee_name}, Weekly Feedback Report",
                "areas_of_improvement": {"title": "Areas of Improvement:", "items": ["No specific improvement areas identified from available feedback"]},
                "positives": {"title": "Positives:", "items": ["No positive feedback patterns detected"]},
                "negatives": {"title": "Negatives:", "items": ["No negative concerns raised in feedback"]},
                "conclusion": {"title": "", "content": "Insufficient feedback data for comprehensive analysis."}
            }
        }

class Command(BaseCommand):
    help = 'Generates weekly feedback summaries for the previous week'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-id',
            type=int,
            help='Generate summary for specific employee only',
        )
    
    def handle(self, *args, **options):
        # Calculate last week's dates (Monday to Sunday)
        today = timezone.now().date()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        
        self.stdout.write(
            f"Generating weekly summaries for {start_of_last_week} to {end_of_last_week}"
        )
        
        employee_id = options.get('employee_id')
        
        if employee_id:
            self.generate_employee_summary(start_of_last_week, end_of_last_week, employee_id)
        else:
            self.generate_organization_summary(start_of_last_week, end_of_last_week)
            self.generate_all_employee_summaries(start_of_last_week, end_of_last_week)
    
    def get_feedback_text(self, feedback):
        """
        Safely get feedback text from Feedback object
        """
        if hasattr(feedback, 'message') and feedback.message:
            return feedback.message
        elif hasattr(feedback, 'feedback_text') and feedback.feedback_text:
            return feedback.feedback_text
        elif hasattr(feedback, 'comments') and feedback.comments:
            return feedback.comments
        elif hasattr(feedback, 'content') and feedback.content:
            return feedback.content
        else:
            return ""
    
    def analyze_feedback_content(self, feedbacks):
        """
        Basic analysis for strengths and improvement areas (for separate fields)
        """
        strengths = []
        improvements = []
        all_messages = [self.get_feedback_text(f) for f in feedbacks if self.get_feedback_text(f)]
        
        work_themes = {
            'communication': ['communicat', 'explain', 'discuss', 'clear', 'update'],
            'teamwork': ['team', 'collaborat', 'support', 'help', 'cooperat'],
            'initiative': ['initiative', 'proactive', 'ownership', 'lead'],
            'quality': ['quality', 'thorough', 'detail', 'accurate', 'precise'],
        }
        for theme, keywords in work_themes.items():
            theme_count = sum(1 for message in all_messages 
                            if any(keyword in message.lower() for keyword in keywords))
            if theme_count >= 2:
                strengths.append(f"Strong {theme} skills")
                improvements.append(f"Continue developing {theme} capabilities")
        
        return {
            'strengths': strengths[:5],
            'improvement_areas': improvements[:5]
        }
    
    def generate_feedback_report(self, employee_name, analysis_results, average_rating, individual_feedbacks):
        """
        Generate feedback report using the intelligent analyzer
        """
        try:
            analyzer = IntelligentFeedbackAnalyzer()
            feedback_texts = []
            for feedback in individual_feedbacks:
                text = self.get_feedback_text(feedback)
                if text:
                    feedback_texts.append(text)
                    
            return analyzer.generate_feedback_report(employee_name, feedback_texts)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error in intelligent analysis: {str(e)}"))
            strengths = analysis_results.get('strengths', [])
            improvements = analysis_results.get('improvement_areas', [])
            
            return {
                "employee_name": employee_name,
                "sections": {
                    "header": f"{employee_name}, ",
                    "areas_of_improvement": {
                        "title": "Areas of Improvement:",
                        "items": improvements[:2] if improvements else ["Focus on continuous improvement"]
                    },
                    "positives": {
                        "title": "Positives:",
                        "items": strengths[:3] if strengths else ["Demonstrating commitment and dedication"]
                    },
                    "negatives": {
                        "title": "Negatives:",
                        "items": ["No significant negative feedback received"]
                    },
                    "conclusion": {
                        "title": "",
                        "content": f"Based on {len(individual_feedbacks)} feedback(s), continue leveraging your strengths while focusing on growth opportunities."
                    }
                }
            }