import PyPDF2
import docx
import re
import json
import os
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class QuestionGenerator:
    def __init__(self):
        """Initialize question generator with templates and patterns"""
        self.stop_words = set(stopwords.words('english'))
        
        # Question templates by category
        self.question_templates = {
            'technical': [
                "Can you explain your experience with {technology}?",
                "What challenges did you face while working with {technology}?",
                "How would you approach solving a problem with {technology}?",
                "What's your level of expertise in {technology}?",
                "Can you describe a project where you used {technology}?",
                "What are the key features of {technology}?",
                "How do you stay updated with {technology}?",
                "What's your experience with {technology} in production environments?"
            ],
            'experience': [
                "Can you walk me through your experience at {company}?",
                "What were your main responsibilities at {company}?",
                "What was the most challenging project you worked on at {company}?",
                "How did you contribute to the success of {company}?",
                "What did you learn from your time at {company}?",
                "Can you describe a typical day at {company}?",
                "What technologies did you use at {company}?",
                "How long did you work at {company} and why did you leave?"
            ],
            'education': [
                "Can you tell me about your {degree} in {field}?",
                "What was your favorite subject during your {degree}?",
                "How has your {degree} prepared you for this role?",
                "What projects did you work on during your {degree}?",
                "How do you apply what you learned in {field} to your work?",
                "What was your thesis/final project about?",
                "How do you stay current with developments in {field}?"
            ],
            'skills': [
                "How would you rate your proficiency in {skill}?",
                "Can you give me an example of how you used {skill}?",
                "What's your experience level with {skill}?",
                "How do you keep your {skill} skills up to date?",
                "Can you describe a situation where {skill} was crucial?",
                "What training have you had in {skill}?"
            ],
            'behavioral': [
                "Tell me about a time when you had to solve a difficult problem.",
                "Describe a situation where you had to work under pressure.",
                "Can you give me an example of when you had to learn something quickly?",
                "Tell me about a time when you had to work with a difficult team member.",
                "Describe a project where you had to meet a tight deadline.",
                "Can you tell me about a time when you failed and what you learned?",
                "Describe a situation where you had to take initiative.",
                "Tell me about a time when you had to adapt to change."
            ],
            'general': [
                "Why are you interested in this position?",
                "Where do you see yourself in 5 years?",
                "What are your strengths and weaknesses?",
                "Why should we hire you?",
                "What motivates you?",
                "How do you handle stress?",
                "What's your preferred work environment?",
                "How do you stay organized?"
            ]
        }
        
        # Technology keywords for technical questions
        self.technology_keywords = {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
                'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'powershell'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel',
                'asp.net', 'rails', 'fastapi', 'node.js', 'jquery', 'bootstrap', 'tailwind'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server',
                'dynamodb', 'cassandra', 'elasticsearch', 'neo4j'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode', 'vultr'
            ],
            'tools': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'jira',
                'confluence', 'slack', 'teams', 'zoom', 'figma', 'sketch'
            ]
        }
        
        # Common job titles and their related skills
        self.job_skills = {
            'software_engineer': ['programming', 'algorithms', 'data structures', 'testing', 'version control'],
            'data_scientist': ['python', 'r', 'statistics', 'machine learning', 'sql', 'data analysis'],
            'frontend_developer': ['javascript', 'html', 'css', 'react', 'angular', 'vue', 'responsive design'],
            'backend_developer': ['python', 'java', 'node.js', 'databases', 'apis', 'server management'],
            'devops_engineer': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'monitoring'],
            'ui_ux_designer': ['figma', 'sketch', 'adobe creative suite', 'user research', 'prototyping'],
            'project_manager': ['agile', 'scrum', 'jira', 'leadership', 'communication', 'planning']
        }
    
    def parse_resume(self, filepath: str) -> Dict:
        """Parse resume file and extract information"""
        try:
            file_extension = os.path.splitext(filepath)[1].lower()
            
            if file_extension == '.pdf':
                return self._parse_pdf(filepath)
            elif file_extension in ['.docx', '.doc']:
                return self._parse_docx(filepath)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return self._get_default_resume_data()
    
    def _parse_pdf(self, filepath: str) -> Dict:
        """Parse PDF resume"""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                return self._extract_information(text)
                
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return self._get_default_resume_data()
    
    def _parse_docx(self, filepath: str) -> Dict:
        """Parse DOCX resume"""
        try:
            doc = docx.Document(filepath)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._extract_information(text)
            
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return self._get_default_resume_data()
    
    def _extract_information(self, text: str) -> Dict:
        """Extract information from resume text"""
        try:
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Extract basic information
            name = self._extract_name(text)
            email = self._extract_email(text)
            phone = self._extract_phone(text)
            education = self._extract_education(text)
            experience = self._extract_experience(text)
            skills = self._extract_skills(text)
            projects = self._extract_projects(text)
            
            return {
                'name': name,
                'email': email,
                'phone': phone,
                'education': education,
                'experience': experience,
                'skills': skills,
                'projects': projects,
                'raw_text': text
            }
            
        except Exception as e:
            print(f"Error extracting information: {e}")
            return self._get_default_resume_data()
    
    def _extract_name(self, text: str) -> str:
        """Extract name from resume text"""
        # Simple pattern matching for name (first line or after "Name:")
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char in line.lower() for char in ['@', 'http', 'www']):
                return line
        return "Candidate"
    
    def _extract_email(self, text: str) -> str:
        """Extract email from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from resume text"""
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group() if match else ""
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        # Common education keywords
        edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'school']
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in edu_keywords):
                # Extract degree and field
                degree_match = re.search(r'(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)', sentence_lower)
                if degree_match:
                    education.append({
                        'degree': degree_match.group(),
                        'description': sentence.strip(),
                        'year': self._extract_year(sentence)
                    })
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience information"""
        experience = []
        
        # Look for company names and job titles
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Common job title keywords
            job_keywords = ['engineer', 'developer', 'analyst', 'manager', 'specialist', 'consultant', 'lead']
            
            if any(keyword in line_lower for keyword in job_keywords):
                # Try to find company name in nearby lines
                company = ""
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if lines[j].strip() and not any(char in lines[j].lower() for char in ['@', 'http']):
                        company = lines[j].strip()
                        break
                
                experience.append({
                    'title': line.strip(),
                    'company': company,
                    'description': self._get_context(text, line, 200)
                })
        
        return experience
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = []
        
        # Look for skills section
        skills_section = self._find_skills_section(text)
        if skills_section:
            # Extract individual skills
            skill_pattern = r'\b[A-Za-z+#][A-Za-z0-9+#\s]*\b'
            matches = re.findall(skill_pattern, skills_section)
            
            for match in matches:
                skill = match.strip()
                if len(skill) > 2 and skill.lower() not in self.stop_words:
                    skills.append(skill)
        
        # Also look for technologies mentioned throughout the text
        for category, tech_list in self.technology_keywords.items():
            for tech in tech_list:
                if tech.lower() in text.lower():
                    skills.append(tech)
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        
        # Look for project keywords
        project_keywords = ['project', 'developed', 'created', 'built', 'implemented', 'designed']
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in project_keywords):
                projects.append({
                    'description': sentence.strip(),
                    'technologies': self._extract_technologies_from_text(sentence)
                })
        
        return projects
    
    def _find_skills_section(self, text: str) -> str:
        """Find the skills section in resume text"""
        # Look for skills section headers
        skills_headers = ['skills', 'technical skills', 'technologies', 'tools', 'languages']
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(header in line_lower for header in skills_headers):
                # Return next few lines as skills section
                return '\n'.join(lines[i:i+10])
        
        return ""
    
    def _extract_technologies_from_text(self, text: str) -> List[str]:
        """Extract technology mentions from text"""
        technologies = []
        
        for category, tech_list in self.technology_keywords.items():
            for tech in tech_list:
                if tech.lower() in text.lower():
                    technologies.append(tech)
        
        return list(set(technologies))
    
    def _extract_year(self, text: str) -> str:
        """Extract year from text"""
        year_pattern = r'\b(19|20)\d{2}\b'
        match = re.search(year_pattern, text)
        return match.group() if match else ""
    
    def _get_context(self, text: str, target_line: str, context_length: int) -> str:
        """Get context around a target line"""
        try:
            index = text.find(target_line)
            if index != -1:
                start = max(0, index - context_length)
                end = min(len(text), index + len(target_line) + context_length)
                return text[start:end].strip()
        except:
            pass
        return target_line
    
    def generate_questions(self, resume_data: Dict) -> List[Dict]:
        """Generate personalized questions based on resume data"""
        questions = []
        
        # Generate technical questions based on skills
        technical_questions = self._generate_technical_questions(resume_data['skills'])
        questions.extend(technical_questions)
        
        # Generate experience questions
        experience_questions = self._generate_experience_questions(resume_data['experience'])
        questions.extend(experience_questions)
        
        # Generate education questions
        education_questions = self._generate_education_questions(resume_data['education'])
        questions.extend(education_questions)
        
        # Generate project questions
        project_questions = self._generate_project_questions(resume_data['projects'])
        questions.extend(project_questions)
        
        # Add behavioral questions
        behavioral_questions = self._generate_behavioral_questions()
        questions.extend(behavioral_questions)
        
        # Add general questions
        general_questions = self._generate_general_questions()
        questions.extend(general_questions)
        
        # Shuffle and limit questions
        import random
        random.shuffle(questions)
        
        return questions[:15]  # Return top 15 questions
    
    def _generate_technical_questions(self, skills: List[str]) -> List[Dict]:
        """Generate technical questions based on skills"""
        questions = []
        
        for skill in skills[:5]:  # Top 5 skills
            template = random.choice(self.question_templates['technical'])
            question_text = template.format(technology=skill)
            
            questions.append({
                'question': question_text,
                'category': 'technical',
                'skill': skill,
                'difficulty': 'medium'
            })
        
        return questions
    
    def _generate_experience_questions(self, experience: List[Dict]) -> List[Dict]:
        """Generate questions based on work experience"""
        questions = []
        
        for exp in experience[:3]:  # Top 3 experiences
            company = exp.get('company', 'your previous company')
            template = random.choice(self.question_templates['experience'])
            question_text = template.format(company=company)
            
            questions.append({
                'question': question_text,
                'category': 'experience',
                'company': company,
                'difficulty': 'medium'
            })
        
        return questions
    
    def _generate_education_questions(self, education: List[Dict]) -> List[Dict]:
        """Generate questions based on education"""
        questions = []
        
        for edu in education:
            degree = edu.get('degree', 'degree')
            field = self._extract_field_from_education(edu.get('description', ''))
            
            template = random.choice(self.question_templates['education'])
            question_text = template.format(degree=degree, field=field)
            
            questions.append({
                'question': question_text,
                'category': 'education',
                'degree': degree,
                'field': field,
                'difficulty': 'easy'
            })
        
        return questions
    
    def _generate_project_questions(self, projects: List[Dict]) -> List[Dict]:
        """Generate questions based on projects"""
        questions = []
        
        for project in projects[:2]:  # Top 2 projects
            technologies = project.get('technologies', [])
            
            if technologies:
                tech = technologies[0]
                question_text = f"Can you tell me about the project where you used {tech}? What were the challenges and how did you overcome them?"
                
                questions.append({
                    'question': question_text,
                    'category': 'project',
                    'technology': tech,
                    'difficulty': 'medium'
                })
        
        return questions
    
    def _generate_behavioral_questions(self) -> List[Dict]:
        """Generate behavioral questions"""
        questions = []
        
        for template in random.sample(self.question_templates['behavioral'], 3):
            questions.append({
                'question': template,
                'category': 'behavioral',
                'difficulty': 'hard'
            })
        
        return questions
    
    def _generate_general_questions(self) -> List[Dict]:
        """Generate general interview questions"""
        questions = []
        
        for template in random.sample(self.question_templates['general'], 3):
            questions.append({
                'question': template,
                'category': 'general',
                'difficulty': 'medium'
            })
        
        return questions
    
    def _extract_field_from_education(self, description: str) -> str:
        """Extract field of study from education description"""
        # Common fields
        fields = ['computer science', 'engineering', 'mathematics', 'physics', 'chemistry', 'biology']
        
        description_lower = description.lower()
        for field in fields:
            if field in description_lower:
                return field
        
        return "your field of study"
    
    def _get_default_resume_data(self) -> Dict:
        """Return default resume data when parsing fails"""
        return {
            'name': 'Candidate',
            'email': '',
            'phone': '',
            'education': [],
            'experience': [],
            'skills': [],
            'projects': [],
            'raw_text': ''
        }

# Import random for question generation
import random