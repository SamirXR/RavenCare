"""
OpenAI O4-Mini Evaluator
Handles final evaluation and clinical decision-making
"""

import json
from typing import Dict
from openai import AzureOpenAI

from src.config import config


class O4MiniEvaluator:
    """
    OpenAI O4-Mini evaluator for final clinical assessment.
    
    This agent performs the third stage of triage by:
    - Cross-validating Gemini and Grok analyses
    - Providing final specialty recommendations
    - Generating comprehensive action plans
    - Creating patient-friendly instructions
    - Identifying any discrepancies or concerns
    """
    
    def __init__(self):
        """Initialize O4-Mini client with Azure OpenAI credentials"""
        if not config.OPENAI_ENDPOINT or not config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_ENDPOINT and OPENAI_API_KEY must be set in .env file"
            )
        
        self.client = AzureOpenAI(
            api_version=config.OPENAI_API_VERSION,
            azure_endpoint=config.OPENAI_ENDPOINT,
            api_key=config.OPENAI_API_KEY
        )
        self.model_name = config.OPENAI_MODEL_NAME
    
    def final_evaluation(
        self,
        patient_data: Dict,
        gemini_analysis: Dict,
        grok_analysis: Dict
    ) -> Dict:
        """
        Provide final evaluation and comprehensive recommendation.
        
        Args:
            patient_data (Dict): Patient information
            gemini_analysis (Dict): Gemini specialty mapping results
            grok_analysis (Dict): Grok urgency assessment results
        
        Returns:
            Dict: Final evaluation containing:
                - final_specialty: Confirmed medical specialty
                - confidence_level: High/Moderate/Low confidence
                - recommended_action: Detailed action plan
                - doctor_requirements: Specific doctor qualifications
                - consultation_priority: Emergency/Urgent/Standard/Routine
                - estimated_consultation_duration: Time in minutes
                - patient_instructions: Clear patient guidance
                - follow_up_required: Boolean flag
                - additional_tests_needed: List of recommended tests
                - evaluation_notes: Comprehensive summary
                - warnings: Important warnings for patient/doctor
        """
        system_prompt = """You are the chief medical officer reviewing triage \
assessments. Your role is to:

1. Evaluate consistency between specialty mapping and urgency assessment
2. Provide a final recommendation for patient care
3. Suggest specific next steps and doctor assignment criteria
4. Identify any discrepancies or concerns in the analyses
5. Provide patient-friendly guidance

Respond in JSON format:
{
    "final_specialty": "specialty name",
    "confidence_level": "High/Moderate/Low",
    "recommended_action": "detailed action plan",
    "doctor_requirements": "specific doctor qualifications needed",
    "consultation_priority": "Emergency/Urgent/Standard/Routine",
    "estimated_consultation_duration": "15/30/45/60 minutes",
    "patient_instructions": "clear instructions for patient",
    "follow_up_required": true/false,
    "additional_tests_needed": ["test1", "test2"],
    "evaluation_notes": "comprehensive evaluation summary",
    "warnings": ["warning1", "warning2"]
}"""

        # Build comprehensive context from all previous analyses
        user_input = f"""Patient Information:
{json.dumps(patient_data, indent=2)}

Gemini Analysis (Specialty Mapping):
{json.dumps(gemini_analysis, indent=2)}

Grok Analysis (Urgency Assessment):
{json.dumps(grok_analysis, indent=2)}

Please provide your final evaluation and comprehensive recommendation."""

        # Call Azure OpenAI API
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_completion_tokens=40000,
            model=self.model_name,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback evaluation
            primary_specialty = gemini_analysis.get(
                'primary_specialty',
                'General Medicine'
            )
            triage_category = grok_analysis.get('triage_category', 'Standard')
            
            return {
                "final_specialty": primary_specialty,
                "confidence_level": "Moderate",
                "recommended_action": "Consult with specialist",
                "doctor_requirements": "Experienced specialist",
                "consultation_priority": triage_category,
                "estimated_consultation_duration": "30 minutes",
                "patient_instructions": (
                    "Please arrive 15 minutes early for your appointment"
                ),
                "follow_up_required": True,
                "additional_tests_needed": [],
                "evaluation_notes": response.choices[0].message.content,
                "warnings": []
            }
