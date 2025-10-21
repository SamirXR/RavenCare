"""
Grok 4 Fast Reasoning Analyzer
Handles urgency scoring and risk assessment
"""

import json
from typing import Dict
from openai import OpenAI

from src.config import config


class GrokAnalyzer:
    """
    Grok 4 Fast Reasoning analyzer for urgency and risk assessment.
    
    This agent performs the second stage of triage by:
    - Calculating urgency scores (0-100 scale)
    - Assessing risk levels (Critical/High/Moderate/Low)
    - Identifying red flags requiring immediate attention
    - Determining triage categories and time-to-treatment
    """
    
    def __init__(self):
        """Initialize Grok client with API credentials from configuration"""
        if not config.GROK_ENDPOINT or not config.GROK_API_KEY:
            raise ValueError(
                "GROK_ENDPOINT and GROK_API_KEY must be set in .env file"
            )
        
        self.client = OpenAI(
            base_url=config.GROK_ENDPOINT,
            api_key=config.GROK_API_KEY
        )
        self.model_name = config.GROK_MODEL_NAME
    
    def calculate_urgency(
        self,
        patient_data: Dict,
        gemini_analysis: Dict
    ) -> Dict:
        """
        Calculate urgency score and perform risk assessment.
        
        Args:
            patient_data (Dict): Patient information including demographics
                and symptoms
            gemini_analysis (Dict): Results from Gemini specialty mapping
        
        Returns:
            Dict: Urgency assessment containing:
                - urgency_score: Numerical score 0-100
                - risk_level: Critical/High/Moderate/Low
                - triage_category: Emergency/Urgent/Standard/Routine
                - time_to_treatment: Recommended timeframe for care
                - red_flags: List of critical warning signs
                - risk_factors: Contributing risk factors
                - immediate_actions: Actions needed immediately
                - reasoning: Detailed explanation of urgency calculation
        """
        system_prompt = """You are an emergency medicine expert specializing \
in triage and urgency assessment. Analyze patient data and provide:

1. Urgency Score (0-100): Quantitative assessment of care urgency
2. Risk Assessment: Identify immediate risks and red flags
3. Time-to-Treatment: Recommended maximum time before medical attention
4. Triage Category: Emergency/Urgent/Standard/Routine

Consider factors:
- Severity of symptoms
- Duration of symptoms
- Pre-existing conditions
- Age and vulnerability
- Symptom progression
- Potential for deterioration

Respond in JSON format:
{
    "urgency_score": 75,
    "risk_level": "High/Moderate/Low/Critical",
    "triage_category": "Emergency/Urgent/Standard/Routine",
    "time_to_treatment": "Immediate/Within 2 hours/Within 24 hours/Within 1 week",
    "red_flags": ["red flag 1", "red flag 2"],
    "risk_factors": ["risk 1", "risk 2"],
    "immediate_actions": ["action 1", "action 2"],
    "reasoning": "detailed reasoning for urgency score"
}"""

        # Build comprehensive patient context
        pre_conditions = patient_data.get('pre_existing_conditions', ['None'])
        pre_conditions_str = ', '.join(pre_conditions)
        
        key_symptoms = gemini_analysis.get('key_symptoms_identified', [])
        key_symptoms_str = ', '.join(key_symptoms)
        
        potential_conditions = gemini_analysis.get('potential_conditions', [])
        potential_conditions_str = ', '.join(potential_conditions)
        
        urgency_indicators = gemini_analysis.get('urgency_indicators', [])
        urgency_indicators_str = ', '.join(urgency_indicators)
        
        user_input = f"""Patient Data:
Name: {patient_data.get('name')}
Age: {patient_data.get('age')}
Gender: {patient_data.get('gender')}
Symptoms: {patient_data.get('symptoms')}
Pre-existing Conditions: {pre_conditions_str}

Gemini Analysis:
Primary Specialty: {gemini_analysis.get('primary_specialty')}
Key Symptoms: {key_symptoms_str}
Potential Conditions: {potential_conditions_str}
Urgency Indicators: {urgency_indicators_str}

Please provide urgency assessment and risk scoring."""

        # Call Grok API
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        try:
            return json.loads(completion.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback urgency calculation
            fallback_risk_factors = patient_data.get(
                'pre_existing_conditions',
                []
            )
            
            return {
                "urgency_score": 50,
                "risk_level": "Moderate",
                "triage_category": "Standard",
                "time_to_treatment": "Within 24 hours",
                "red_flags": [],
                "risk_factors": fallback_risk_factors,
                "immediate_actions": ["Consult with appropriate specialist"],
                "reasoning": completion.choices[0].message.content
            }
