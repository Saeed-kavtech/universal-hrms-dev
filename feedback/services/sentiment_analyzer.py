import os
import json
from unicodedata import category
import requests
import time
from typing import Optional, Dict, Any

DEFAULT_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class SentimentAnalyzer:
    """
    Enhanced sentiment analyzer using Groq/OpenAI-compatible LLM API.
    With proper error handling and rate limiting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2,
        retry_delay: float = 2.0,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")
        self.base_url = base_url or os.getenv("GROQ_API_URL") or DEFAULT_GROQ_URL
        self.model = model or os.getenv("GROQ_MODEL") or DEFAULT_MODEL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._warn_missing_key = not bool(self.api_key)
        self._last_api_call = 0

    def _call_api(self, prompt: str, max_tokens: int = 400) -> Dict[str, Any]:
        if self._warn_missing_key:
            return {"error": "missing_api_key"}

        current_time = time.time()
        time_since_last_call = current_time - self._last_api_call
        if time_since_last_call < 1.0: 
            time.sleep(1.0 - time_since_last_call)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional HR feedback and tone analyzer. Always return JSON results with no extra text.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1,  
        }

        for attempt in range(self.max_retries + 1):
            try:
                self._last_api_call = time.time()
                resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
                
                if resp.status_code == 429:
                    if attempt < self.max_retries:
                        
                        wait_time = self.retry_delay * (2 ** attempt)
                        print(f"Rate limit hit, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {"error": f"429 Rate limit exceeded after {self.max_retries} retries"}
                
                resp.raise_for_status()
                return resp.json()
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": f"Request timeout after {self.timeout} seconds"}
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": "Connection error"}
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 429 and attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                return {"error": f"HTTP error {resp.status_code}: {str(e)}"}
            except Exception as e:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": f"API call failed: {str(e)}"}

    @staticmethod
    def _extract_json_from_model(content: str) -> Optional[Dict[str, Any]]:
        if not content:
            return None
        content = content.strip()
        if content.startswith("```"):
            start, end = content.find("{"), content.rfind("}")
            if start != -1 and end != -1:
                content = content[start:end + 1]
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return None

    @staticmethod
    def _normalize_score(raw_score: Optional[float]) -> Optional[float]:
        try:
            return max(0.0, min(1.0, float(raw_score)))
        except Exception:
            return 0.5

    def analyze_text(self, text: str, _tone: Optional[str] = None, _category: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the given text and return sentiment, tone, strengths, improvements, and actions.
        Uses the provided category if available.
        """
        text = (text or "").strip()
        if not text:
            return {
                "label": "neutral",
                "score": 0.5,
                "category": _category or "Neutral Feedback",  
                "tone": "Neutral",
                "strengths": "",
                "improvement_areas": "",
                "suggested_action": "",
                "impact_level": "Low",
                "raw": {"note": "empty_text"},
            }

        tone_context = f"(Tone: {_tone}) " if _tone else ""
        category_context = f"(Category: {_category}) " if _category else ""

        prompt = (
    f"Analyze this feedback text and return ONLY valid JSON. {tone_context}{category_context}\n\n"
    f"TEXT: {text}\n\n"
    "Return JSON with these fields:\n"
    "{\n"
    '  "label": "positive|neutral|negative",\n'
    '  "score": 0.0-1.0,\n'
    f'  "category": "{_category}" if category provided, otherwise "Positive Feedback|Corrective Feedback|Time Management|Warning Feedback",\n'
    '  "tone": f"{tone_context}",\n'
    '  "strengths": "comma,separated,key,strengths",\n'
    '  "improvement_areas": "comma,separated,improvement,points",\n'
    '  "suggested_action": "Brief actionable recommendation",\n'
    '  "impact_level": "Low|Medium|High"\n'
    "}\n\n"
    "RULES:\n"
    "- Elaborate strengths and improvement areas based on tone while focusing on text content\n"
    "- Use professional, strong vocabulary to describe key points\n"
    "- Avoid repeating exact words from original text\n"
    "- Extract strengths ONLY from explicit praise\n"
    "- Extract improvements ONLY from explicit criticism\n"
    "- Describe each point in 5-7 word professional phrases\n"
    "- Leave empty if not mentioned\n"
    "- No invented content\n"
    "- For time management feedbacks add something about time improvement in improvement area and do not include strengths by yourself if no mentioned in text\n"
    "- Make  sure while defining strengths or improvement areas use professional terms not just the repetitive words from actual feedback text message\n"
)
        try:
            provider_response = self._call_api(prompt)
            
            if "error" in provider_response:
                return {
                    "label": "error", 
                    "score": 0.5,
                    "category": _category or "API Error",  # Use provided category
                    "tone": "Neutral",
                    "strengths": "",
                    "improvement_areas": "",
                    "suggested_action": "",
                    "impact_level": "Low",
                    "raw": {"error": provider_response["error"]}
                }
            
            choices = provider_response.get("choices", [])
            content = choices[0].get("message", {}).get("content") if choices else None
            
            if not content:
                return {
                    "label": "error", 
                    "score": 0.5,
                    "category": _category or "Error",  
                    "raw": {"error": "Empty response from API"}
                }

        except Exception as e:
            return {
                "label": "error", 
                "score": 0.5,
                "category": _category or "Error",  
                "raw": {"error": f"Analysis failed: {str(e)}"}
            }

        parsed = self._extract_json_from_model(content or "")
        if not parsed:
            return {
                "label": "error", 
                "score": 0.5,
                "category": _category or "Error",  
                "raw": {"response": content, "error": "Failed to parse JSON"}
            }

        return {
            "label": parsed.get("label", "neutral"),
            "score": self._normalize_score(parsed.get("score")),
            "category": _category or parsed.get("category", "Neutral Feedback"),  
            "tone": parsed.get("tone", _tone or "Neutral"),
            "strengths": parsed.get("strengths", "").strip(),
            "improvement_areas": parsed.get("improvement_areas", "").strip(),
            "suggested_action": parsed.get("suggested_action", ""),
            "impact_level": parsed.get("impact_level", "Medium"),
            "raw": parsed,
        }
    def rewrite_text_in_tone(self, text: str, tone: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Rewrite text in a specific tone, then analyze the rewritten feedback.
        Uses the provided category if available.
        """
        text = (text or "").strip()
        tone = (tone or "").strip().lower()
        if not text or not tone:
            return {"error": "Both text and tone are required."}
        if self._warn_missing_key:
            return {"error": "missing_api_key"}

        time.sleep(1.0)

    # Base rewrite prompt with intelligent handling
        rewrite_prompt = f"""Please rewrite the provided text in a {tone} tone to enhance its professionalism and ethical tone. **Preserve all original points including both positive feedback and constructive suggestions.** Maintain the balanced structure of the original feedback. The core meaning and all specific points from the original must be preserved without omission."""

    # Add intelligent category-specific guidance
        if category:
            category_instructions = {
                "job_related_skills": "When reviewing the original text, focus on job-related skills and technical competencies. Only suggest improvements in this area if the original text indicates room for growth in technical abilities.",
                "productivity": "When reviewing the original text, emphasize productivity aspects, output, and efficiency. Only suggest productivity improvements if the original text mentions efficiency-related issues.",
                "quality_of_work": "When reviewing the original text, concentrate on quality, accuracy, and thoroughness aspects. Only suggest quality improvements if the original text indicates quality concerns.",
                "behaviour_with_superiors": "When reviewing the original text, address professional behavior and communication with superiors. Only suggest behavioral improvements if the original text mentions supervisory interactions.",
                "interaction_with_colleagues": "When reviewing the original text, focus on teamwork, collaboration, and colleague interactions. Only suggest interpersonal improvements if the original text discusses team dynamics.",
                "work_initiative_responsibility": "When reviewing the original text, highlight initiative, ownership, and responsibility aspects. Only suggest improvements in initiative if the original text indicates this area.",
                "capacity_to_learn_and_grow": "When reviewing the original text, emphasize learning ability, adaptability, and growth potential. Only suggest learning improvements if the original text discusses development needs.",
                "stress_and_time_management": "When reviewing the original text, focus on handling pressure, deadlines, and time management aspects. Only suggest stress/time management improvements if the original text mentions these challenges.",
                "attendance_and_punctuality": "When reviewing the original text, address reliability, attendance, and punctuality. Only suggest attendance improvements if the original text indicates attendance issues.",
                "compliance_with_company_policies": "When reviewing the original text, concentrate on adherence to policies and procedures. Only suggest compliance improvements if the original text mentions policy-related concerns."
            }
        
            instruction = category_instructions.get(
                category, 
                f"When reviewing the original text, focus on {category.replace('_', ' ').title()} aspects. Only suggest improvements in this area if the original text indicates relevant concerns."
            )
        
            rewrite_prompt += f"\n\n**Category Context: {instruction}**"
        
            rewrite_prompt += f"\n\n**Intelligent Analysis Required:**"
            rewrite_prompt += f"\n1. Analyze the original text's tone and content first"
            rewrite_prompt += f"\n2. If the original text is purely positive with no improvement suggestions, maintain that positivity in the rewrite"
            rewrite_prompt += f"\n3. Only introduce category-specific improvement suggestions if the original text actually mentions relevant issues"
            rewrite_prompt += f"\n4. Keep the category as background context, not forced improvement areas"
            rewrite_prompt += f"\n5. Match the tone ({tone}) while using the category for nuanced understanding"

        rewrite_prompt += f"\n\nThe final output should be a concise version of 3 to 5 lines. Output **only** the final rewritten text with no additional formatting, labels, or explanations.\n\nOriginal Text: {text}"

        try:
            rewrite_response = self._call_api(rewrite_prompt)
    
            if "error" in rewrite_response:
                return {"error": f"Rewrite failed: {rewrite_response['error']}"}
        
            choices = rewrite_response.get("choices", [])
            content = (
                choices[0].get("message", {}).get("content", "").strip()
            if choices else ""
                        )
    
            if not content:
                return {"error": "Empty rewrite response"}

        # Initialize rewritten_text with the full content first
            rewritten_text = content.strip()
        
        # Only try to parse JSON if it looks like JSON
            if content.startswith('{') and '}' in content:
                try:
                # First try to parse as actual JSON
                    import json
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        # Look for common keys that might contain the text
                        for key in ['rewritten_text', 'feedback', 'text', 'content', 'message', 'response']:
                            if key in parsed and isinstance(parsed[key], str):
                                rewritten_text = parsed[key].strip()
                                break
                    else:
                        # If it's a string inside JSON, try to extract it
                        first_quote = content.find('"', 1)
                        if first_quote != -1:
                            second_quote = content.find('"', first_quote + 1)
                            if second_quote != -1:
                                colon = content.find(':', second_quote)
                                if colon != -1:
                                    value_start = content.find('"', colon)
                                    if value_start != -1:
                                        value_end = content.find('"', value_start + 1)
                                        if value_end != -1:
                                            extracted = content[value_start + 1:value_end]
                                            if extracted:  # Only use if not empty
                                                rewritten_text = extracted.strip()
                except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, fall back to the original content
                    pass
        
        # Ensure we have some text
            if not rewritten_text:
                rewritten_text = content.strip()

        except Exception as e:
            return {"error": f"Rewrite failed: {str(e)}"}

        time.sleep(1.0)
        analysis = self.analyze_text(rewritten_text, _tone=tone, _category=category)
        return {
            "original_text": text,
            "tone": tone,
            "category": category,  # Return the category used for rewriting
            "rewritten_text": rewritten_text,
            "label": analysis.get("label"),
            "score": analysis.get("score"),
            "analysis_category": analysis.get("category"),  # Renamed to avoid conflict
            "tone_detected": analysis.get("tone"),
            "impact_level": analysis.get("impact_level"),
            "strengths": analysis.get("strengths"),
            "improvement_areas": analysis.get("improvement_areas"),
            "suggested_action": analysis.get("suggested_action"),
        }


    def analyze_sentiment(text: str, category: Optional[str] = None):
        analyzer = SentimentAnalyzer()
        return analyzer.analyze_text(text, _category=category)


    def rewrite_feedback(text: str, tone: str, category: Optional[str] = None):
        analyzer = SentimentAnalyzer()
        return analyzer.rewrite_text_in_tone(text, tone, category)

#     def rewrite_text_in_tone(self, text: str, tone: str, category: Optional[str] = None) -> Dict[str, Any]:
#         """
#         Rewrite text in a specific tone, then analyze the rewritten feedback.
#         Uses the provided category if available.
#         """
#         text = (text or "").strip()
#         tone = (tone or "").strip().lower()
#         if not text or not tone:
#             return {"error": "Both text and tone are required."}
#         if self._warn_missing_key:
#             return {"error": "missing_api_key"}

#         time.sleep(1.0)

#         rewrite_prompt = (
#     f"Please rewrite the provided text in a {tone} tone to enhance its professionalism and ethical tone. **Preserve all original points including both positive feedback and constructive suggestions.** Maintain the balanced structure of the original feedback. The core meaning and all specific points from the original must be preserved without omission. The final output should be a concise version of 3 to 5 lines. Output **only** the final rewritten text with no additional formatting, labels, or explanations.\n\nOriginal Text: {text}"
# )

#         try:
#             rewrite_response = self._call_api(rewrite_prompt)
    
#             if "error" in rewrite_response:
#                 return {"error": f"Rewrite failed: {rewrite_response['error']}"}
        
#             choices = rewrite_response.get("choices", [])
#             content = (
#                 choices[0].get("message", {}).get("content", "").strip()
#             if choices else ""
#                         )
    
#             if not content:
#                 return {"error": "Empty rewrite response"}

#             rewritten_text = content
            
#             if content.startswith('{') and '}' in content:
#                 first_quote = content.find('"', 1)
#                 if first_quote != -1:
#                     second_quote = content.find('"', first_quote + 1)
#                     if second_quote != -1:
#                         colon = content.find(':', second_quote)
#                         if colon != -1:
#                             value_start = content.find('"', colon)
#                             if value_start != -1:
#                                 value_end = content.find('"', value_start + 1)
#                                 if value_end != -1:
#                                     rewritten_text = content[value_start + 1:value_end]
            
#             rewritten_text = rewritten_text.strip()

#         except Exception as e:
#             return {"error": f"Rewrite failed: {e}"}

#         time.sleep(1.0)
#         analysis = self.analyze_text(rewritten_text, _tone=tone, _category=category)
#         return {
#             "original_text": text,
#             "tone": tone,
#             "rewritten_text": rewritten_text,
#             "label": analysis.get("label"),
#             "score": analysis.get("score"),
#             "category": analysis.get("category"),
#             "tone_detected": analysis.get("tone"),
#             "impact_level": analysis.get("impact_level"),
#             "strengths": analysis.get("strengths"),
#             "improvement_areas": analysis.get("improvement_areas"),
#             "suggested_action": analysis.get("suggested_action"),
#         }


# def analyze_sentiment(text: str, category: Optional[str] = None):
#     analyzer = SentimentAnalyzer()
#     return analyzer.analyze_text(text, _category=category)


# def rewrite_feedback(text: str, tone: str, category: Optional[str] = None):
#     analyzer = SentimentAnalyzer()
#     return analyzer.rewrite_text_in_tone(text, tone, category)