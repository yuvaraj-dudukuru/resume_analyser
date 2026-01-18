import re
import json
import os

class BasicScorer:
    def __init__(self, config):
        self.config = config
        self.scoring_config = config.get("scoring", {})
        self.red_threshold = self.scoring_config.get("red_threshold", 40)
        self.green_threshold = self.scoring_config.get("green_threshold", 70)
        self.bonus_weights = self.scoring_config.get("bonus_weights", {})

    def score(self, resume_text, job_description):
        # Naive keyword extraction from JD:
        jd_words = set(re.findall(r'\b\w{4,}\b', job_description.lower()))
        
        if not jd_words:
            return 0, "No valid keywords in JD", "Red"

        resume_lower = resume_text.lower()
        
        matched_keywords = []
        
        # Base score: percentage of matched keywords
        matches = 0
        for word in jd_words:
            if word in resume_lower:
                matches += 1
                matched_keywords.append(word)
                
        if len(jd_words) == 0:
            match_percentage = 0
        else:
            match_percentage = (matches / len(jd_words)) * 100
        
        # Apply weights
        weighted_score = match_percentage
        for skill, weight in self.bonus_weights.items():
            if skill.lower() in matched_keywords:
                weighted_score += 10 * (weight - 1.0) 

        final_score = min(100, max(0, weighted_score))
        
        # Status
        if final_score < self.red_threshold:
            status = "Red"
        elif final_score < self.green_threshold:
            status = "Yellow"
        else:
            status = "Green"
            
        return final_score, f"Matched {len(matched_keywords)} keywords: {', '.join(matched_keywords[:10])}...", status


class LLMScorer:
    def __init__(self, config, api_key, provider="openai"):
        self.config = config
        self.api_key = api_key
        self.provider = provider
        self.llm_config = config.get("llm", {})
        if self.provider == "gemini":
            self.model = "gemini-pro"
        else:
            self.model = self.llm_config.get("model", "gpt-3.5-turbo")
        
    def score(self, resume_text, job_description):
        prompt = f"""
        You are an expert technical recruiter. 
        Evaluate the following resume against the job description.
        
        Job Description:
        {job_description[:2000]}
        
        Resume Content:
        {resume_text[:4000]}
        
        Output valid JSON with these fields:
        - score (integer 0-100)
        - status (Red, Yellow, Green)
        - reasoning (concise summary of why)
        - matched_keywords (list of key skills found)
        """
        
        try:
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "gemini":
                response = self._call_gemini(prompt)
            else:
                return 0, "Invalid LLM Provider", "Red"
                
            # Parse JSON
            # Clean possible markdown fencing
            cleaned = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            
            return data.get("score", 0), data.get("reasoning", "No reasoning"), data.get("status", "Red")
            
        except Exception as e:
            return 0, f"LLM Error: {str(e)}", "Red"

    def _call_openai(self, prompt):
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content

    def _call_gemini(self, prompt):
        import google.generativeai as genai
        import time
        genai.configure(api_key=self.api_key)
        
        # 1. Get all valid models
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Available Gemini Models: {valid_models}")
        
        # 2. Sort them by preference
        # We want 'flash' first (free/fast), then 'pro', then anything else
        # Also avoid experimental/latest if possible to avoid instability? Or try them last.
        
        def model_priority(name):
            n = name.lower()
            if 'flash' in n and '1.5' in n: return 0 # Highest priority: gemini-1.5-flash
            if 'flash' in n: return 1
            if 'pro' in n and '1.5' in n: return 2
            if 'pro' in n: return 3
            return 4 # Lowest priority
            
        sorted_models = sorted(valid_models, key=model_priority)
        
        last_error = None
        
        # 3. Try them in order until one works
        for model_name in sorted_models:
            try:
                print(f"Trying model: {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                # If we get here, it worked! Save this model for next time to save time
                self._gemini_model_name = model_name
                return response.text
                
            except Exception as e:
                print(f"Failed with {model_name}: {e}")
                last_error = e
                # If it's a 429 (Quota), we should definitely try another model
                # If it's a 404 (Not Found), same.
                # Only stop if it's Authentication Error maybe? But we can just try all.
                continue
                
        raise last_error if last_error else ValueError("No working Gemini models found.")

class ResumeScorer:
    def __init__(self, config, api_key=None):
        self.config = config
        self.api_key = api_key
        
        llm_config = config.get("llm", {})
        provider = llm_config.get("provider", "openai")
        
        # Auto-detect Provider based on Key Prefix
        if self.api_key:
            if self.api_key.startswith("AIza"):
                provider = "gemini"
            elif self.api_key.startswith("sk-"):
                provider = "openai"
                
        if self.api_key:
            self.delegate = LLMScorer(config, api_key, provider)
        else:
            self.delegate = BasicScorer(config)

    def score(self, resume_text, job_description):
        return self.delegate.score(resume_text, job_description)
