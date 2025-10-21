"""
Doctor Matching Service
Matches patients with appropriate doctors based on multiple criteria
"""

import json
import os
from typing import Dict, Optional

from src.config import config
from src.services.advanced_matcher import AdvancedMatchingFeatures


class DoctorMatcher:
    """
    Intelligent doctor matching service.
    
    Matches patients with doctors based on:
    - Medical specialty requirements
    - Doctor availability (time slots)
    - Language preferences
    - Doctor ratings and experience
    """
    
    def __init__(self, doctor_details_path: Optional[str] = None):
        """
        Initialize doctor matcher with database path.
        
        Args:
            doctor_details_path: Path to doctor JSON files directory
                               Defaults to configured path if not provided
        """
        self.doctor_details_path = (
            doctor_details_path or config.DOCTOR_DETAILS_DIR
        )
        self.doctors_database = {}
        self.load_doctor_database()
    
    def load_doctor_database(self) -> None:
        """
        Load all doctor information from JSON files.
        
        Reads all specialty JSON files and builds an in-memory
        database for fast doctor matching.
        """
        for specialty in config.SUPPORTED_SPECIALTIES:
            file_path = os.path.join(
                self.doctor_details_path,
                f"{specialty}.json"
            )
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Extract first department's doctors
                    if 'departments' in data and len(data['departments']) > 0:
                        department = data['departments'][0]
                        specialty_key = specialty.title()
                        self.doctors_database[specialty_key] = department
                        
                except Exception as e:
                    # Skip files that can't be loaded
                    continue
    
    def find_best_doctor(
        self,
        specialty: str,
        preferred_slot: str,
        patient_language: str,
        urgency_score: int = 50,
        patient_age: int = None,
        sub_specialization_hint: str = None,
        patient_conditions: list = None
    ) -> Optional[Dict]:
        """
        Find the best matching doctor for a patient using advanced multi-factor scoring.
        
        Uses a weighted scoring algorithm that considers:
        - Exact specialty match (highest priority)
        - Sub-specialization alignment with patient condition
        - Available time slots matching patient preference
        - Language compatibility
        - Doctor rating, experience, and awards
        - Urgency-based prioritization
        - Age-appropriate care (pediatrics, geriatrics)
        
        Args:
            specialty: Required medical specialty (e.g., "Cardiology")
            preferred_slot: Patient's preferred time slot (e.g., "09:00")
            patient_language: Patient's preferred language (e.g., "English")
            urgency_score: Urgency score from 0-100 (default: 50)
            patient_age: Patient age for age-appropriate matching
            sub_specialization_hint: Specific sub-specialty needed
            patient_conditions: List of pre-existing conditions
        
        Returns:
            Dict: Best matching doctor with match_score and match_details, or None if no match
        """
        # Normalize specialty for lookup
        specialty_normalized = specialty.title()
        
        # Try exact match first
        if specialty_normalized in self.doctors_database:
            department = self.doctors_database[specialty_normalized]
        else:
            # Try fuzzy match
            department = None
            for key in self.doctors_database.keys():
                specialty_lower = specialty.lower()
                key_lower = key.lower()
                
                if specialty_lower in key_lower or key_lower in specialty_lower:
                    department = self.doctors_database[key]
                    break
            
            # No matching department found
            if department is None:
                return None
        
        # Get doctors from department
        doctors = department.get('doctors', [])
        if not doctors:
            return None
        
        # Score each doctor based on multiple weighted criteria
        best_doctor = None
        best_score = -1
        match_details = {}
        
        for doctor in doctors:
            score = 0
            details = {}
            
            # 1. Slot availability (40 points max)
            # High urgency patients need immediate availability
            doctor_slots = doctor.get('slots', [])
            if preferred_slot in doctor_slots:
                slot_score = 40
                details['slot_match'] = 'exact'
            elif doctor_slots:
                # Partial credit for having any slots
                slot_score = 20
                details['slot_match'] = 'alternative'
            else:
                slot_score = 0
                details['slot_match'] = 'none'
            
            # Urgency boost: High urgency cases prioritize availability
            if urgency_score >= 70:
                slot_score *= 1.5
            score += slot_score
            
            # 2. Language match (25 points)
            languages_spoken = doctor.get('languages_spoken', [])
            if patient_language in languages_spoken:
                score += 25
                details['language_match'] = True
            else:
                details['language_match'] = False
            
            # 3. Doctor rating (20 points max)
            patient_rating = doctor.get('patient_rating', 0)
            rating_score = patient_rating * 4
            score += rating_score
            details['rating_score'] = patient_rating
            
            # 4. Experience points (15 points max)
            experience_years = doctor.get('experience_years', 0)
            # Cap at 15 years for max points, 1 point per year
            experience_score = min(experience_years, 15)
            score += experience_score
            details['experience_years'] = experience_years
            
            # 5. Sub-specialization match (30 points - CRITICAL for accuracy)
            sub_spec = doctor.get('sub_specialization', '').lower()
            if sub_specialization_hint:
                hint_lower = sub_specialization_hint.lower()
                # Check if doctor's sub-specialization matches the hint
                if hint_lower in sub_spec or any(
                    word in sub_spec for word in hint_lower.split()
                ):
                    score += 30
                    details['sub_spec_match'] = 'strong'
                elif sub_spec:
                    score += 10
                    details['sub_spec_match'] = 'partial'
            elif patient_conditions:
                # Match sub-specialization to patient conditions
                condition_keywords = ' '.join(patient_conditions).lower()
                if any(
                    keyword in sub_spec
                    for keyword in condition_keywords.split()
                ):
                    score += 20
                    details['sub_spec_match'] = 'condition_based'
            
            # 6. Awards and recognition (10 points)
            awards = doctor.get('awards', [])
            if awards:
                score += min(len(awards) * 5, 10)
                details['has_awards'] = True
            
            # 7. Age-appropriate care bonus (10 points)
            if patient_age is not None:
                # Pediatric patients (0-18)
                if patient_age < 18 and specialty_normalized == 'Pediatrics':
                    score += 10
                    details['age_appropriate'] = 'pediatric'
                # Geriatric consideration (65+)
                elif patient_age >= 65 and experience_years >= 10:
                    score += 5
                    details['age_appropriate'] = 'geriatric_experienced'
            
            # 8. Urgency-experience alignment (10 points)
            # High urgency cases should go to more experienced doctors
            if urgency_score >= 80 and experience_years >= 15:
                score += 10
                details['urgency_experience_match'] = True
            elif urgency_score < 50 and experience_years < 10:
                # Junior doctors can handle routine cases
                score += 5
                details['urgency_experience_match'] = 'routine'
            
            # Update best doctor if this one scores higher
            if score > best_score:
                best_score = score
                best_doctor = doctor.copy()
                match_details = details.copy()
        
        # Add matching metadata to doctor object
        if best_doctor:
            best_doctor['match_score'] = round(best_score, 2)
            best_doctor['match_details'] = match_details
            best_doctor['match_quality'] = (
                'excellent' if best_score >= 100 else
                'good' if best_score >= 70 else
                'fair' if best_score >= 50 else
                'low'
            )
        
        return best_doctor
    
    def get_available_specialties(self) -> list[str]:
        """
        Get list of all loaded specialties.
        
        Returns:
            list: List of specialty names
        """
        return list(self.doctors_database.keys())
    
    def get_doctors_by_specialty(self, specialty: str) -> list[Dict]:
        """
        Get all doctors for a specific specialty.
        
        Args:
            specialty: Medical specialty name
        
        Returns:
            list: List of doctor information dictionaries
        """
        specialty_normalized = specialty.title()
        
        if specialty_normalized in self.doctors_database:
            department = self.doctors_database[specialty_normalized]
            return department.get('doctors', [])
        
        return []
