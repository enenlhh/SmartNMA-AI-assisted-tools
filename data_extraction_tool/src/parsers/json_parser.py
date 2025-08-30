"""
Parser for JSON format responses
Handles structured JSON output from OpenAI
"""
import json

class JsonParser:
    """Parser for JSON format LLM responses"""
    
    def parse_response(self, response_data, table_name):
        """Parse JSON response into structured data"""
        if not response_data:
            return []
        
        # Extract the appropriate array from the JSON structure
        if table_name == "Study_Info":
            return response_data.get("studies", [])
        elif table_name == "Groups":
            return response_data.get("groups", [])
        elif table_name == "Participant_Characteristics":
            return response_data.get("characteristics", [])
        elif table_name == "Outcomes":
            return response_data.get("outcomes", [])
        elif table_name == "Results":
            return response_data.get("results", [])
        elif table_name == "Comparisons":
            return response_data.get("comparisons", [])
        
        return []
