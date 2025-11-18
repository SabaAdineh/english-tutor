from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import re
from typing import Dict
import random

class GrammarCorrector:
    def __init__(self):
        print("🚀 Loading grammar model locally...")
        self.model_name = "vennify/t5-base-grammar-correction"
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        self.corrector = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,
        )
        print("✅ Model loaded locally!")
    
    def correct_grammar(self, text: str, difficulty: str = "intermediate") -> Dict:
        if len(text.strip()) < 2:
            return self._create_response(text, text, "Please enter a longer sentence.", 0.1, "unsure", difficulty)
        
        try:
            result = self.corrector(
                f"grammar: {text}",
                max_length=128,
                num_beams=2,
                early_stopping=True
            )
            corrected = result[0]['generated_text'].strip()

            # Check if the sentence is actually correct
            if self._is_grammar_correct(text, corrected):
                explanation = self._get_correct_explanation(difficulty)
                return self._create_response(text, text, explanation, 0.95, "correct", difficulty)
            
            # Otherwise, get accurate explanation for the changes
            explanation = self._get_accurate_explanation(text, corrected, difficulty)
            
            if difficulty == "easy":
                return self._easy_mode(text, corrected, explanation)
            elif difficulty == "advanced":
                return self._advanced_mode(text, corrected, explanation)
            else:
                return self._intermediate_mode(text, corrected, explanation)
                    
        except Exception as e:
            return self._rule_based_correction(text, difficulty)
    
    def _is_grammar_correct(self, original: str, corrected: str) -> bool:
        """Smart check if grammar is actually correct (ignoring minor formatting)"""
        
        # If identical, definitely correct
        if original.lower() == corrected.lower():
            return True
        
        # Check if only minor punctuation/capitalization changes
        original_clean = re.sub(r'[^\w\s]', '', original.lower())
        corrected_clean = re.sub(r'[^\w\s]', '', corrected.lower())
        
        if original_clean == corrected_clean:
            return True
        
        # Check similarity of meaningful words
        similarity = self._similarity(original, corrected)
        if similarity > 0.90:  # Lower threshold for correct detection
            return True
        
        # Check for common minor rephrasing that doesn't change meaning
        minor_changes = [
            (r'i am', r"i'm"),
            (r'it is', r"it's"),
            (r'that is', r"that's"),
            (r'what is', r"what's"),
            (r'do not', r"don't"),
            (r'does not', r"doesn't"),
        ]
        
        for formal, contraction in minor_changes:
            if (re.search(formal, original.lower()) and re.search(contraction, corrected.lower())) or \
               (re.search(contraction, original.lower()) and re.search(formal, corrected.lower())):
                return True
        
        return False
    
    def _get_correct_explanation(self, difficulty: str) -> str:
        """Generate explanation for correct sentences"""
        explanations = {
            "easy": [
                "Great! Your sentence is clear and easy to understand! 👍",
                "Perfect for everyday conversation! 🎉",
                "Your meaning is clear - well done! ✅",
                "Good enough for basic communication! 💬"
            ],
            "intermediate": [
                "Perfect grammar! ✅",
                "Excellent writing - no errors found! 📚",
                "Well-constructed sentence! 🎯",
                "Grammatically correct and natural! 🌟"
            ],
            "advanced": [
                "Flawless professional English! 💎",
                "Perfect grammar and sophisticated expression! 🏆",
                "Native-level proficiency demonstrated! 🌟",
                "Impeccable grammar and structure! ✅"
            ]
        }
        return random.choice(explanations.get(difficulty, ["Great! No errors found!"]))
    
    def _get_accurate_explanation(self, original: str, corrected: str, difficulty: str) -> str:
        """Generate accurate explanation based on what actually changed"""
        
        # Check for specific common errors
        original_lower = original.lower()
        corrected_lower = corrected.lower()
        
        # Specific feedback for "don't" → "doesn't"
        if re.search(r'\b(she|he|it) don\'t\b', original_lower) and re.search(r'\b(she|he|it) doesn\'t\b', corrected_lower):
            if difficulty == "easy":
                return "Fixed the verb for clearer communication!"
            elif difficulty == "advanced":
                return "Corrected third-person singular verb form."
            else:
                return "Use 'doesn't' with he/she/it, not 'don't'."
        
        # Specific feedback for "do" → "does"  
        if re.search(r'\b(she|he|it) do\b', original_lower) and re.search(r'\b(she|he|it) does\b', corrected_lower):
            if difficulty == "easy":
                return "Made the verb match the subject!"
            elif difficulty == "advanced":
                return "Corrected subject-verb agreement."
            else:
                return "Use 'does' with he/she/it, not 'do'."
        
        # Specific feedback for "go" → "goes"
        if re.search(r'\b(she|he|it) go\b', original_lower) and re.search(r'\b(she|he|it) goes\b', corrected_lower):
            if difficulty == "easy":
                return "Fixed the verb ending!"
            elif difficulty == "advanced":
                return "Corrected third-person singular present tense."
            else:
                return "Use 'goes' with he/she/it, not 'go'."
        
        # Specific feedback for "is" → "am/are"
        if re.search(r'\bi is\b', original_lower) and 'am' in corrected_lower:
            if difficulty == "easy":
                return "Fixed the verb for 'I'!"
            elif difficulty == "advanced":
                return "Corrected first-person verb conjugation."
            else:
                return "Use 'am' with 'I', not 'is'."
        
        if difficulty == "easy":
            return "Improved the sentence for better understanding!"
        elif difficulty == "advanced":
            return "Enhanced grammar and sentence structure."
        else:
            return "Corrected grammatical errors."
    
    def _easy_mode(self, original: str, corrected: str, explanation: str) -> Dict:
        # Easy mode: Sometimes keep original if very similar
        similarity = self._similarity(original, corrected)
        if similarity > 0.85:
            return self._create_response(original, original, "Looks good for conversation!", 0.8, "correct", "easy")
        else:
            return self._create_response(original, corrected, explanation, 0.7, "corrected", "easy")
    
    def _intermediate_mode(self, original: str, corrected: str, explanation: str) -> Dict:
        # Intermediate: Usually apply corrections
        return self._create_response(original, corrected, explanation, 0.8, "corrected", "intermediate")
    
    def _advanced_mode(self, original: str, corrected: str, explanation: str) -> Dict:
        # Advanced mode: Always apply corrections
        return self._create_response(original, corrected, explanation, 0.85, "corrected", "advanced")
    
    def _similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2: return 0.0
        common = len(words1.intersection(words2))
        return common / len(words1.union(words2))
    
    def _rule_based_correction(self, text: str, difficulty: str) -> Dict:
        # Check if text is already correct using basic rules
        basic_errors = [
            r'\b(she|he|it) don\'t\b',
            r'\b(she|he|it) do\b',
            r'\b(she|he|it) go\b',
            r'\bi is\b'
        ]
        
        has_errors = any(re.search(pattern, text.lower()) for pattern in basic_errors)
        
        if not has_errors:
            explanation = self._get_correct_explanation(difficulty)
            return self._create_response(text, text, explanation, 0.9, "correct", difficulty)
        else:
            # Apply basic corrections
            corrections = {
                r'\bhe go\b': 'he goes',
                r'\bshe go\b': 'she goes',
                r'\bi is\b': 'I am',
                r'\bshe don\'t\b': "she doesn't",
                r'\bhe don\'t\b': "he doesn't",
            }
            
            corrected = text
            for wrong, right in corrections.items():
                corrected = re.sub(wrong, right, corrected, flags=re.IGNORECASE)
            
            explanation = "Applied basic grammar rules."
            return self._create_response(text, corrected, explanation, 0.7, "corrected", difficulty)
    
    def _create_response(self, original: str, corrected: str, explanation: str, 
                        confidence: float, status: str, difficulty: str) -> Dict:
        return {
            "original_text": original,
            "corrected_text": corrected,
            "explanation": explanation,
            "confidence": confidence,
            "status": status,
            "is_correct": status == "correct",
            "suggestions": [],
            "difficulty_used": difficulty
        }