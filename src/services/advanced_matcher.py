"""
Advanced Doctor Matching with ML-like Features
Adds intelligent features for more accurate doctor-patient matching
"""

from typing import Dict, List, Optional
import re


class AdvancedMatchingFeatures:
    """
    Advanced matching features for improved doctor-patient connections.
    
    Provides:
    - Symptom-to-subspecialty keyword mapping
    - Condition severity analysis
    - Historical matching pattern optimization
    - Multi-specialty coordination detection
    """
    
    # Comprehensive symptom-to-subspecialty keyword mappings
    SUBSPECIALTY_KEYWORDS = {
        'Cardiology': {
            'interventional': [
                'angioplasty', 'stent', 'catheterization', 'coronary',
                'heart attack', 'myocardial infarction', 'acute coronary'
            ],
            'electrophysiology': [
                'arrhythmia', 'palpitations', 'irregular heartbeat', 
                'atrial fibrillation', 'afib', 'flutter', 'tachycardia',
                'bradycardia', 'heart rhythm'
            ],
            'heart_failure': [
                'shortness of breath', 'swelling', 'edema', 'fatigue',
                'weak heart', 'heart failure', 'cardiomyopathy'
            ],
            'congenital': [
                'birth defect', 'congenital', 'hole in heart', 'murmur'
            ]
        },
        'Gastroenterology': {
            'liver': [
                'jaundice', 'hepatitis', 'cirrhosis', 'liver',
                'yellow skin', 'ascites', 'liver disease'
            ],
            'inflammatory_bowel': [
                'crohn', 'colitis', 'inflammatory bowel', 'ibd',
                'bloody stool', 'chronic diarrhea'
            ],
            'pancreas': [
                'pancreatitis', 'pancreas', 'diabetes'
            ],
            'acid_reflux': [
                'gerd', 'acid reflux', 'heartburn', 'esophagus'
            ]
        },
        'Neurology': {
            'stroke': [
                'stroke', 'paralysis', 'facial drooping', 'slurred speech',
                'sudden weakness', 'tia', 'transient ischemic'
            ],
            'epilepsy': [
                'seizure', 'epilepsy', 'convulsion', 'fits'
            ],
            'migraine': [
                'migraine', 'severe headache', 'visual aura'
            ],
            'movement_disorders': [
                'parkinson', 'tremor', 'movement disorder', 'dystonia'
            ],
            'dementia': [
                'alzheimer', 'dementia', 'memory loss', 'cognitive decline'
            ]
        },
        'Orthopedics': {
            'sports': [
                'sports injury', 'ligament tear', 'acl', 'mcl',
                'meniscus', 'athletic injury'
            ],
            'spine': [
                'back pain', 'spine', 'disc', 'herniated', 'sciatica',
                'spinal', 'vertebra'
            ],
            'joint_replacement': [
                'knee replacement', 'hip replacement', 'arthritis',
                'joint pain', 'osteoarthritis'
            ],
            'trauma': [
                'fracture', 'broken bone', 'trauma', 'injury'
            ]
        },
        'Pulmonology': {
            'asthma': [
                'asthma', 'wheezing', 'breathing difficulty', 'inhaler'
            ],
            'copd': [
                'copd', 'emphysema', 'chronic bronchitis', 'smoker'
            ],
            'sleep': [
                'sleep apnea', 'snoring', 'cpap'
            ],
            'interstitial': [
                'fibrosis', 'interstitial lung', 'pulmonary fibrosis'
            ]
        },
        'Psychiatry': {
            'depression': [
                'depression', 'low mood', 'sadness', 'hopelessness',
                'loss of interest', 'suicidal'
            ],
            'anxiety': [
                'anxiety', 'panic', 'worry', 'nervousness', 'ocd'
            ],
            'bipolar': [
                'bipolar', 'manic', 'mood swings'
            ],
            'psychosis': [
                'schizophrenia', 'psychosis', 'hallucination', 'delusion'
            ]
        },
        'Dermatology': {
            'acne': [
                'acne', 'pimples', 'blackheads', 'breakout'
            ],
            'psoriasis': [
                'psoriasis', 'scaly skin', 'plaque'
            ],
            'skin_cancer': [
                'mole', 'melanoma', 'skin cancer', 'changing spot'
            ],
            'eczema': [
                'eczema', 'atopic dermatitis', 'itchy rash'
            ]
        },
        'ENT': {
            'hearing': [
                'hearing loss', 'deaf', 'tinnitus', 'ringing in ear'
            ],
            'sinus': [
                'sinusitis', 'sinus', 'nasal congestion'
            ],
            'throat': [
                'sore throat', 'tonsillitis', 'hoarseness', 'voice problem'
            ]
        }
    }
    
    # Urgency-based keywords
    EMERGENCY_KEYWORDS = [
        'chest pain', 'heart attack', 'stroke', 'seizure',
        'severe bleeding', 'difficulty breathing', 'unconscious',
        'severe pain', 'suicide', 'overdose', 'trauma'
    ]
    
    @classmethod
    def extract_subspecialty_hints(
        cls,
        symptoms: str,
        specialty: str,
        conditions: List[str]
    ) -> Optional[str]:
        """
        Extract specific sub-specialization hints from symptoms and conditions.
        
        Args:
            symptoms: Patient symptom description
            specialty: Primary specialty identified
            conditions: List of pre-existing conditions
        
        Returns:
            str: Sub-specialization hint, or None if no match
        """
        specialty_normalized = specialty.title()
        
        if specialty_normalized not in cls.SUBSPECIALTY_KEYWORDS:
            return None
        
        # Combine symptoms and conditions for analysis
        text_to_analyze = (
            f"{symptoms} {' '.join(conditions)}".lower()
        )
        
        # Check each sub-specialty's keywords
        subspecialty_matches = {}
        for subspec, keywords in cls.SUBSPECIALTY_KEYWORDS[
            specialty_normalized
        ].items():
            match_count = sum(
                1 for keyword in keywords
                if keyword.lower() in text_to_analyze
            )
            if match_count > 0:
                subspecialty_matches[subspec] = match_count
        
        # Return sub-specialty with most keyword matches
        if subspecialty_matches:
            best_match = max(
                subspecialty_matches.items(),
                key=lambda x: x[1]
            )
            return best_match[0].replace('_', ' ').title()
        
        return None
    
    @classmethod
    def calculate_condition_severity(
        cls,
        symptoms: str,
        urgency_score: int
    ) -> str:
        """
        Calculate condition severity level.
        
        Args:
            symptoms: Patient symptom description
            urgency_score: Urgency score (0-100)
        
        Returns:
            str: Severity level (critical/high/moderate/low)
        """
        symptoms_lower = symptoms.lower()
        
        # Check for emergency keywords
        has_emergency = any(
            keyword in symptoms_lower
            for keyword in cls.EMERGENCY_KEYWORDS
        )
        
        if has_emergency or urgency_score >= 90:
            return 'critical'
        elif urgency_score >= 70:
            return 'high'
        elif urgency_score >= 40:
            return 'moderate'
        else:
            return 'low'
    
    @classmethod
    def detect_multi_specialty_need(
        cls,
        analyses: Dict
    ) -> List[str]:
        """
        Detect if patient needs multiple specialty consultations.
        
        Args:
            analyses: Dictionary containing gemini, grok, and o4mini results
        
        Returns:
            List[str]: List of additional specialties that may be needed
        """
        additional_specialties = []
        
        # Extract secondary specialties from Gemini
        gemini = analyses.get('gemini', {})
        secondary = gemini.get('secondary_specialties', [])
        
        # Extract warnings from O4-Mini
        o4mini = analyses.get('o4mini', {})
        warnings = o4mini.get('warnings', [])
        
        # If there are secondary specialties with high confidence
        if len(secondary) > 0:
            additional_specialties.extend(secondary[:2])
        
        # Check for multi-system involvement in warnings
        multi_system_keywords = [
            'multiple', 'systemic', 'comprehensive', 'coordinated'
        ]
        for warning in warnings:
            if any(kw in warning.lower() for kw in multi_system_keywords):
                additional_specialties.append('Internal Medicine')
                break
        
        return list(set(additional_specialties))
    
    @classmethod
    def generate_match_explanation(
        cls,
        doctor: Dict,
        match_details: Dict,
        patient_name: str
    ) -> str:
        """
        Generate human-readable explanation of why doctor was matched.
        
        Args:
            doctor: Matched doctor information
            match_details: Match details from scoring algorithm
            patient_name: Patient name
        
        Returns:
            str: Detailed explanation of the match
        """
        explanations = []
        
        doctor_name = doctor.get('name', 'Unknown')
        
        # Slot match
        if match_details.get('slot_match') == 'exact':
            explanations.append(
                "appointment slot matches patient preference"
            )
        
        # Language match
        if match_details.get('language_match'):
            explanations.append(
                "speaks patient's preferred language"
            )
        
        # Sub-specialization
        if match_details.get('sub_spec_match') == 'strong':
            explanations.append(
                "has specific expertise in patient's condition"
            )
        
        # Experience
        exp_years = match_details.get('experience_years', 0)
        if exp_years >= 15:
            explanations.append(
                f"highly experienced ({exp_years} years)"
            )
        
        # Rating
        rating = match_details.get('rating_score', 0)
        if rating >= 4.5:
            explanations.append(
                f"excellent patient rating ({rating}/5.0)"
            )
        
        # Awards
        if match_details.get('has_awards'):
            explanations.append("recognized with professional awards")
        
        if explanations:
            explanation_text = ", ".join(explanations)
            return (
                f"{doctor_name} was matched to {patient_name} because: "
                f"{explanation_text}."
            )
        else:
            return (
                f"{doctor_name} was matched to {patient_name} "
                f"based on specialty alignment."
            )
    
    @classmethod
    def suggest_appointment_preparation(
        cls,
        specialty: str,
        urgency_score: int,
        conditions: List[str]
    ) -> List[str]:
        """
        Suggest what patient should prepare for appointment.
        
        Args:
            specialty: Medical specialty
            urgency_score: Urgency score
            conditions: Pre-existing conditions
        
        Returns:
            List[str]: List of preparation suggestions
        """
        suggestions = [
            "Bring valid ID and insurance card",
            "List all current medications with dosages"
        ]
        
        # Add specialty-specific suggestions
        specialty_prep = {
            'Cardiology': [
                "Bring previous ECG/echo reports if available",
                "Note any chest pain episodes with timing"
            ],
            'Gastroenterology': [
                "Keep a food diary for 3 days before visit",
                "Note bowel movement patterns"
            ],
            'Neurology': [
                "Document seizure episodes if applicable",
                "Bring previous brain imaging (MRI/CT) reports"
            ],
            'Orthopedics': [
                "Bring previous X-rays or MRI scans",
                "Note which movements cause pain"
            ],
            'Dermatology': [
                "Document when skin changes started",
                "Avoid makeup on affected areas"
            ],
            'Psychiatry': [
                "Keep a mood diary",
                "List previous treatments tried"
            ]
        }
        
        if specialty in specialty_prep:
            suggestions.extend(specialty_prep[specialty])
        
        # High urgency cases
        if urgency_score >= 80:
            suggestions.insert(
                0,
                "⚠️ HIGH URGENCY: Go to emergency room if symptoms worsen"
            )
        
        return suggestions
