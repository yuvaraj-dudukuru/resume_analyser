from .config import get_email_template

class EmailGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self, candidate_data):
        status = candidate_data.get("status", "Red")
        template = get_email_template(self.config, status)
        
        try:
            return template.format(**candidate_data)
        except Exception:
            # Fallback if keys are missing
            return template.replace("{candidate_name}", candidate_data.get("candidate_name", "Candidate"))
