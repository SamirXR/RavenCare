"""
Gemini 2.5 Pro Analyzer
Handles initial symptom analysis and medical specialty mapping
"""

import json
from typing import Dict
from google import genai
from google.genai import types

from src.config import config


class GeminiAnalyzer:
    """
    Gemini 2.5 Pro analyzer for symptom assessment and specialty mapping.
    
    This agent performs the first stage of triage by:
    - Analyzing patient symptoms comprehensively
    - Identifying potential medical conditions
    - Mapping symptoms to appropriate medical specialties
    - Considering pre-existing conditions in assessment
    """
    
    def __init__(self):
        """Initialize Gemini client with API key from configuration"""
        if not config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = config.GEMINI_MODEL
    
    def analyze_symptoms(self, patient_data: Dict) -> Dict:
        """
        Analyze patient symptoms and map to medical specialty.
        
        Args:
            patient_data (Dict): Patient information including:
                - name: Patient name
                - age: Patient age
                - gender: Patient gender
                - symptoms: Detailed symptom description
                - pre_existing_conditions: List of pre-existing conditions
                - preferred_language: Preferred language for communication
        
        Returns:
            Dict: Analysis results containing:
                - primary_specialty: Main medical specialty needed
                - secondary_specialties: Alternative specialties to consider
                - key_symptoms_identified: List of key symptoms found
                - potential_conditions: Possible medical conditions
                - urgency_indicators: Factors indicating urgency
                - reasoning: Detailed explanation of specialty mapping
        """
        system_prompt = """You are an expert medical triage specialist with \
deep knowledge in emergency medicine, symptom analysis, and medical specialty \
mapping. Your role is to:

1. Analyze patient symptoms comprehensively
2. Identify potential medical conditions
3. Map symptoms to the appropriate medical specialty
4. Consider pre-existing conditions in your assessment
5. Provide detailed reasoning for your specialty mapping

Available Specialties:
- Cardiology (heart and cardiovascular issues)
- Gastroenterology (digestive system issues)
- Hepatology (liver diseases)
- Neurology (nervous system and brain issues)
- Orthopedics (bones, joints, muscles)
- Pediatrics (children's health)
- Dermatology (skin conditions)
- Ophthalmology (eye conditions)
- ENT (Ear, Nose, Throat)
- Psychiatry (mental health)
- Pulmonology (respiratory/lung issues)
- Emergency Medicine (critical/life-threatening)

Respond in JSON format with:
{
    "primary_specialty": "specialty name",
    "secondary_specialties": ["specialty1", "specialty2"],
    "key_symptoms_identified": ["symptom1", "symptom2"],
    "potential_conditions": ["condition1", "condition2"],
    "urgency_indicators": ["indicator1", "indicator2"],
    "reasoning": "detailed explanation of specialty mapping"
}"""

        # Build user input with patient information
        pre_conditions = patient_data.get('pre_existing_conditions', ['None'])
        pre_conditions_str = ', '.join(pre_conditions)
        
        user_input = f"""Patient Information:
Name: {patient_data.get('name', 'Unknown')}
Age: {patient_data.get('age', 'Unknown')}
Gender: {patient_data.get('gender', 'Unknown')}
Symptoms: {patient_data.get('symptoms', 'No symptoms provided')}
Pre-existing Conditions: {pre_conditions_str}
Preferred Language: {patient_data.get('preferred_language', 'English')}

Please analyze these symptoms and provide specialty mapping."""

        # Create content for Gemini API
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)]
            )
        ]
        
        # Configure generation with thinking budget and JSON output
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            system_instruction=[types.Part.from_text(text=system_prompt)],
            response_mime_type="application/json"
        )
        
        # Stream response from Gemini
        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config
        ):
            if chunk.text:
                response_text += chunk.text
        
        # Parse JSON response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            mapped_specialty = patient_data.get(
                'mapped_specialty',
                'General Medicine'
            )
            symptoms_preview = patient_data.get('symptoms', '')[:50]
            
            return {
                "primary_specialty": mapped_specialty,
                "secondary_specialties": [],
                "key_symptoms_identified": [symptoms_preview],
                "potential_conditions": ["Requires further evaluation"],
                "urgency_indicators": [],
                "reasoning": response_text
            }
