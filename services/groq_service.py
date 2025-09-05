"""
Modul ini menyediakan service untuk berinteraksi dengan Groq API.

Fungsinya mencakup pengujian koneksi dan analisis interaksi obat
menggunakan model Llama yang dijalankan di Groq.
"""
import os
import json
from typing import List, Dict

from dotenv import load_dotenv
from groq import Groq, APIError

load_dotenv()


class GroqService:
    """Service class untuk menangani interaksi dengan Groq LLM API."""

    def __init__(self):
        """Inisialisasi Groq client dan model yang akan digunakan."""
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.model = "llama-3.3-70b-versatile"

    async def test_connection(self):
        """Menguji koneksi ke Groq API."""
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, respond with just 'OK' if you can hear me."
                    }
                ],
                model=self.model,
                max_tokens=10
            )
            return response.choices[0].message.content
        except APIError as e:  # Menangkap error spesifik dari Groq
            return f"Error: {str(e)}"

    async def analyze_drug_interactions(
        self,
        patient_data: Dict,
        new_medications: List[str],
        drug_interactions_db: List[Dict],
        notes: str = ""
    ):
        """Fungsi utama untuk menganalisis interaksi obat menggunakan Llama."""
        # Mempersiapkan konteks untuk LLM
        context = self._prepare_interaction_context(
            patient_data, new_medications, drug_interactions_db, notes
        )

        prompt = f"""You are a clinical pharmacist AI assistant. Analyze the following medication scenario and provide warnings.

PATIENT CONTEXT:
{context}

TASK: Analyze potential drug interactions and contraindications. Return response in JSON format ONLY.

RESPONSE FORMAT:
{{
    "warnings": [
        {{
            "type": "drug-drug" or "drug-disease",
            "severity": "Major" or "Moderate" or "Minor",
            "description": "Clinical explanation",
            "medications_involved": ["drug1", "drug2"]
        }}
    ],
    "safe_to_prescribe": true/false,
    "reasoning": "Brief clinical reasoning"
}}

IMPORTANT:
- Only return valid JSON
- Use clinical terminology
- Focus on actionable warnings
- Consider patient's age, gender, and existing conditions"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=1000,
                temperature=0.1  # Suhu rendah untuk konsistensi saran medis
            )

            # Membersihkan dan parse respons JSON
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())

        except json.JSONDecodeError as e:
            return {
                "warnings": [],
                "safe_to_prescribe": False,
                "reasoning": f"Error parsing AI response: {str(e)}"
            }
        except APIError as e:  # Menangkap error spesifik dari Groq
            return {
                "warnings": [],
                "safe_to_prescribe": False,
                "reasoning": f"API Error: {str(e)}"
            }

    def _prepare_interaction_context(
        self,
        patient_data: Dict,
        new_medications: List[str],
        drug_interactions_db: List[Dict],
        notes: str
    ) -> str:
        """Mempersiapkan konteks terstruktur untuk analisis LLM."""
        # Ekstrak interaksi relevan dari database
        current_meds = patient_data.get("current_medications", [])
        all_medications = current_meds + new_medications
        relevant_interactions = []

        for interaction in drug_interactions_db:
            drug_a = interaction["drug_a"].lower()
            drug_b = interaction["drug_b"].lower()

            # Cek jika kedua obat dalam interaksi ada di daftar
            for med1 in all_medications:
                for med2 in all_medications:
                    if (drug_a in med1.lower() and drug_b in med2.lower()) or \
                       (drug_b in med1.lower() and drug_a in med2.lower()):
                        relevant_interactions.append(interaction)

        context = f"""
Patient: {patient_data.get('name', 'Unknown')} ({patient_data.get('age')} years old, {patient_data.get('gender')})

Current Diagnoses: {', '.join(patient_data.get('diagnoses_text', []))}
Current Medications: {', '.join(patient_data.get('current_medications', []))}
Allergies: {', '.join(patient_data.get('allergies', ['None']))}

NEW MEDICATIONS TO PRESCRIBE: {', '.join(new_medications)}

CLINICAL NOTES: {notes}

KNOWN DRUG INTERACTIONS DATABASE:
{json.dumps(relevant_interactions, indent=2)}
"""
        return context

# Global instance
groq_service = GroqService()