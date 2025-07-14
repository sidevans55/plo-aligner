import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json
import re

# Try to import sentence_transformers, fallback to simple comparison if not available
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available, using fallback comparison method")

class CPFComparator:
    def __init__(self):
        # Load a pre-trained semantic similarity model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None
        
        # Define CPF PLOs grouped by theme with headings (EXACT FRAMEWORK FROM USER'S CSV)
        self.cpf_plos = {
            "Knowledge": {
                "Foundational Knowledge & Concepts": [
                    "Demonstrate an understanding of five core concepts: evolution, structure and function, information flow, exchange, and storage, pathways and transformations of energy, and systems as they pertain to biological organisms and ecosystems.",
                    "Demonstrate an understanding of key concepts, theories, and interdisciplinary connections in biology, including genetics, cell and molecular biology, physiology, ecology, and evolutionary biology.",
                    "Understand how structure and function are correlated at all levels of biological organization.",
                    "Understand how interactions between organisms and their environment drive the dynamics of individuals, populations, communities, and ecosystems.",
                    "Distinguish between elements of experimental design, including research questions/objectives, hypotheses, methodology, data and results, and conclusions.",
                    "Describe the peer review process for academic publication.",
                    "Differentiate between the formats in which scientists disseminate knowledge.",
                    "Identify the appropriate tools and methods associated with sub-disciplines in biology, ranging from microbiology to the study of the biosphere.",
                    "Demonstrate an understanding of how history has shaped biology and biological research, and communication of the sciences."
                ],
                "Knowledge Expansion": [
                    "Understand contemporary biological issues regarding environment, health, economy, and society.",
                    "Demonstrate knowledge of ethical, economic, commercial, and social implications of scientific research and technological innovation.",
                    "Describe the role and responsibilities of biologists in society.",
                    "Recognize the limitations of technology and how it can impact our ability to explore reality and modify biological theories.",
                    "Identify biological assumptions in society and the resulting challenges due to the inherent complexity of biological systems.",
                    "Understand the consequences of organism interactions in natural populations, communities, and ecosystems.",
                    "Understand how technological innovation impacts the process and communication of scientific information, and how it affects the role of scientists in the community."
                ],
                "Integration of Knowledge": [
                    "Integrate knowledge of biological systems at all levels, from genes to ecosystems, using cellular, physiological, ecological, and evolutionary principles and history.",
                    "Explain how biology builds upon other academic disciplines and facilitates understanding of other sciences and humanities.",
                    "Understand the interconnectedness and interdependencies of biological processes (systems biology) at the cellular, organism, and ecosystem levels."
                ]
            },
            "Skills": {
                "Communication": [
                    "Effectively communicate complex biological concepts to diverse audiences using oral, visual, and written formats.",
                    "Appraise audiences and tailor information dissemination accordingly.",
                    "Discuss and reflect on biological findings and their impact on society.",
                    "Critically appraise scientific literature and communicate the limitations of data when formulating conclusions.",
                    "Correctly cite and reference sources in written work.",
                    "Illustrate how biology relates to current events, global issues, and other scientific disciplines."
                ],
                "Application and Critical Thinking": [
                    "Utilize interdisciplinary approaches to identify and address biological problems within societal and environmental contexts.",
                    "Apply foundational knowledge and concepts to analyze biological solutions and develop innovative solutions at various levels of organization.",
                    "Evaluate gaps in biological knowledge and engage in critical analysis of pertinent topics within the field.",
                    "Synthesize and interpret biological information using appropriate methods such as graphs, figures, diagrams, or statistical analyses.",
                    "Recognize the limits of current biological knowledge and evaluate new and emerging concepts in the field.",
                    "Utilize innovative technology to explore and expand knowledge of biology.",
                    "Evaluate information from diverse media sources to form informed opinions on politicized biological issues.",
                    "Critically analyze the social and political factors that shape scientific research and its applications."
                ],
                "Research and Laboratory Techniques": [
                    "Demonstrate proficiency in applying the scientific method to develop and test hypotheses, as well as in collecting, analyzing, and interpreting data.",
                    "Gain hands-on experience in laboratory and/or field settings, exploring areas relevant to biological sciences.",
                    "Utilize standard laboratory and field sampling techniques, tools, calculations, and statistical methods.",
                    "Maintain proper research records and apply effective data management techniques."
                ],
                "Teamwork": [
                    "Collaborate effectively in a team setting, demonstrating both leadership and participation skills.",
                    "Apply efficient time management and collaboration strategies to produce high-quality projects.",
                    "Participate constructively in group activities and peer reviews.",
                    "Respectfully collaborate with interdisciplinary teams of colleagues and community members to share biological knowledge.",
                    "Consider diverse perspectives and respect contributions of others."
                ]
            },
            "Values": {
                "Professional and Ethical Behaviour": [
                    "Act with scientific, academic, and professional integrity and ethics.",
                    "Differentiate between ethical and unethical animal practices when designing biological experiments, and judge which procedures are appropriate according to government protocols.",
                    "Adhere to professional standards regarding data use and ownership, privacy, intellectual property, and artificial intelligence use.",
                    "Contribute to building a safe, supportive, and professional learning environment."
                ],
                "Societal Importance": [
                    "Analyze and critically evaluate the societal importance of biological sciences, including the relevance to human welfare, conservation, and sustainability.",
                    "Develop personal beliefs and values regarding biological issues in society, and initiate action in support of these values.",
                    "Recognize and understand sustainability challenges from a scientific perspective and the need for multiple perspectives, such as those found within indigenous systems, to achieve a sustainable future."
                ],
                "Commitment to Lifelong Learning": [
                    "Demonstrate self-direction and motivation towards learning.",
                    "Identify personal interests and develop a plan for a career in biology.",
                    "Develop a comprehensive understanding of oneself as a learner and apply appropriate learning strategies to various situations."
                ]
            }
        }
        
        # Flatten CPF PLOs for comparison with headings
        self.flattened_cpf = []
        for theme, headings in self.cpf_plos.items():
            for heading, plos in headings.items():
                for plo in plos:
                    self.flattened_cpf.append((theme, heading, plo))
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for similarity analysis"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words and short words
        key_terms = [word for word in words if word not in common_words and len(word) > 2]
        
        return key_terms
    
    def _find_common_terms(self, text1: str, text2: str) -> List[str]:
        """Find common terms between two texts"""
        terms1 = set(self._extract_key_terms(text1))
        terms2 = set(self._extract_key_terms(text2))
        return list(terms1.intersection(terms2))
    
    def _analyze_bloom_taxonomy(self, text: str) -> Dict[str, bool]:
        """Analyze text for Bloom's Taxonomy levels"""
        bloom_verbs = {
            'remember': ['define', 'describe', 'identify', 'list', 'name', 'recall', 'recognize', 'state'],
            'understand': ['explain', 'summarize', 'interpret', 'classify', 'compare', 'contrast', 'describe'],
            'apply': ['apply', 'demonstrate', 'execute', 'implement', 'solve', 'use', 'utilize'],
            'analyze': ['analyze', 'examine', 'investigate', 'compare', 'differentiate', 'distinguish'],
            'evaluate': ['evaluate', 'assess', 'critique', 'judge', 'appraise', 'examine'],
            'create': ['create', 'design', 'develop', 'formulate', 'generate', 'produce', 'construct']
        }
        
        text_lower = text.lower()
        levels = {}
        
        for level, verbs in bloom_verbs.items():
            levels[level] = any(verb in text_lower for verb in verbs)
        
        return levels
    
    def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using simple term overlap when sentence-transformers is not available"""
        terms1 = set(self._extract_key_terms(text1))
        terms2 = set(self._extract_key_terms(text2))
        
        if not terms1 or not terms2:
            return 0.0
        
        intersection = len(terms1.intersection(terms2))
        union = len(terms1.union(terms2))
        
        # Jaccard similarity
        jaccard = intersection / union if union > 0 else 0.0
        
        # Boost similarity if there are many common terms
        common_ratio = intersection / min(len(terms1), len(terms2)) if min(len(terms1), len(terms2)) > 0 else 0.0
        
        # Combine Jaccard and common ratio for better similarity score
        similarity = (jaccard * 0.6) + (common_ratio * 0.4)
        
        return min(similarity, 1.0)  # Cap at 1.0

    def compare_plos(self, institutional_plos: List[str]) -> Dict[str, Any]:
        """
        Compare institutional PLOs with CPF framework using the user's specific criteria:
        - Content alignment (0.5 if content matches)
        - Depth of learning alignment (1.0 if both content and depth match)
        - Threshold for "match" is 0.7
        """
        results = {
            'summary': {},
            'detailed_results': [],
            'theme_breakdown': {},
            'recommendations': [],
            'crosswalk_matrix': {}
        }
        
        # Compare each institutional PLO with all CPF PLOs
        detailed_results = []
        theme_scores = {'Knowledge': [], 'Skills': [], 'Values': []}
        
        # Create crosswalk matrix structure
        crosswalk_matrix = {
            'cpf_plos': [],
            'institutional_plos': institutional_plos,
            'matrix': {}
        }
        
        # Initialize matrix with CPF PLOs
        for theme, headings in self.cpf_plos.items():
            for heading, plos in headings.items():
                for plo in plos:
                    crosswalk_matrix['cpf_plos'].append({
                        'theme': theme,
                        'heading': heading,
                        'plo': plo
                    })
        
        for inst_plo in institutional_plos:
            plo_matches = []
            
            for theme, heading, cpf_plo in self.flattened_cpf:
                # Calculate similarity using available method
                if SENTENCE_TRANSFORMERS_AVAILABLE and self.model:
                    inst_emb = self.model.encode(inst_plo, convert_to_tensor=True)
                    cpf_emb = self.model.encode(cpf_plo, convert_to_tensor=True)
                    similarity = util.cos_sim(inst_emb, cpf_emb).item()
                else:
                    similarity = self._calculate_simple_similarity(inst_plo, cpf_plo)
                
                # Find common terms for explanation
                common_terms = self._find_common_terms(inst_plo, cpf_plo)
                
                # Analyze Bloom's Taxonomy levels
                inst_bloom = self._analyze_bloom_taxonomy(inst_plo)
                cpf_bloom = self._analyze_bloom_taxonomy(cpf_plo)
                
                # Check for Bloom's Taxonomy alignment
                bloom_alignment = any(inst_bloom[level] and cpf_bloom[level] for level in inst_bloom.keys())
                
                # Apply user's scoring criteria
                if similarity >= 0.7:
                    score = 1.0  # Full alignment (green)
                    alignment_type = "Full"
                elif similarity >= 0.5:
                    score = 0.5  # Partial alignment (yellow)
                    alignment_type = "Partial"
                else:
                    score = 0.0  # No alignment (red)
                    alignment_type = "None"
                
                plo_matches.append({
                    'cpf_theme': theme,
                    'cpf_heading': heading,
                    'cpf_plo': cpf_plo,
                    'similarity_score': round(similarity, 3),
                    'alignment_score': score,
                    'common_terms': common_terms,
                    'bloom_alignment': bloom_alignment,
                    'inst_bloom': inst_bloom,
                    'cpf_bloom': cpf_bloom,
                    'alignment_type': alignment_type
                })
                
                theme_scores[theme].append(similarity)
            
            # Sort matches by similarity score
            plo_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            detailed_results.append({
                'institutional_plo': inst_plo,
                'matches': plo_matches,
                'best_match': plo_matches[0] if plo_matches else None
            })
        
        # Build crosswalk matrix
        for i, cpf_item in enumerate(crosswalk_matrix['cpf_plos']):
            cpf_plo = cpf_item['plo']
            cpf_emb = self.model.encode(cpf_plo, convert_to_tensor=True)
            
            for j, inst_plo in enumerate(institutional_plos):
                inst_emb = self.model.encode(inst_plo, convert_to_tensor=True)
                similarity = util.cos_sim(inst_emb, cpf_emb).item()
                
                # Find common terms
                common_terms = self._find_common_terms(inst_plo, cpf_plo)
                
                # Analyze Bloom's Taxonomy
                inst_bloom = self._analyze_bloom_taxonomy(inst_plo)
                cpf_bloom = self._analyze_bloom_taxonomy(cpf_plo)
                bloom_alignment = any(inst_bloom[level] and cpf_bloom[level] for level in inst_bloom.keys())
                
                # Apply scoring criteria
                if similarity >= 0.7:
                    score = 1.0
                    color = 'green'
                    alignment_type = "Full"
                elif similarity >= 0.5:
                    score = 0.5
                    color = 'yellow'
                    alignment_type = "Partial"
                else:
                    score = 0.0
                    color = 'red'
                    alignment_type = "None"
                
                matrix_key = f"{i}_{j}"
                crosswalk_matrix['matrix'][matrix_key] = {
                    'score': round(similarity, 3),
                    'alignment_score': score,
                    'color': color,
                    'common_terms': common_terms,
                    'bloom_alignment': bloom_alignment,
                    'alignment_type': alignment_type,
                    'inst_bloom': inst_bloom,
                    'cpf_bloom': cpf_bloom
                }
        
        results['crosswalk_matrix'] = crosswalk_matrix
        
        # Calculate summary statistics
        total_plos = len(institutional_plos)
        avg_scores = {}
        for theme in theme_scores:
            if theme_scores[theme]:
                avg_scores[theme] = round(np.mean(theme_scores[theme]), 3)
            else:
                avg_scores[theme] = 0.0
        
        # Calculate overall alignment score
        all_scores = [score for scores in theme_scores.values() for score in scores]
        overall_alignment = float(round(np.mean(all_scores), 3)) if all_scores else 0.0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(avg_scores, overall_alignment)
        
        # Find strongest and weakest themes
        strongest_theme = None
        weakest_theme = None
        if avg_scores:
            strongest_theme = max(avg_scores.keys(), key=lambda k: avg_scores[k])
            weakest_theme = min(avg_scores.keys(), key=lambda k: avg_scores[k])
        
        results['summary'] = {
            'total_plos_analyzed': total_plos,
            'overall_alignment_score': overall_alignment,
            'theme_averages': avg_scores,
            'strongest_theme': strongest_theme,
            'weakest_theme': weakest_theme
        }
        
        results['detailed_results'] = detailed_results
        results['theme_breakdown'] = theme_scores
        results['recommendations'] = recommendations
        
        return results
    
    def _generate_recommendations(self, theme_scores: Dict[str, float], overall_alignment: float) -> List[str]:
        """Generate recommendations based on alignment scores"""
        recommendations = []
        
        # Overall alignment recommendations
        if overall_alignment >= 0.8:
            recommendations.append("Excellent alignment with CPF framework! Your PLOs demonstrate strong coverage of knowledge, skills, and values.")
        elif overall_alignment >= 0.6:
            recommendations.append("Good alignment with CPF framework. Consider strengthening areas with lower scores.")
        elif overall_alignment >= 0.4:
            recommendations.append("Moderate alignment with CPF framework. Focus on improving coverage of underrepresented themes.")
        else:
            recommendations.append("Limited alignment with CPF framework. Consider reviewing and revising PLOs to better align with Canadian standards.")
        
        # Theme-specific recommendations
        for theme, score in theme_scores.items():
            if score < 0.5:
                if theme == "Knowledge":
                    recommendations.append(f"Consider strengthening {theme} PLOs to better cover core biological concepts and scientific understanding.")
                elif theme == "Skills":
                    recommendations.append(f"Enhance {theme} PLOs to include more emphasis on experimental design, data analysis, and communication.")
                elif theme == "Values":
                    recommendations.append(f"Develop {theme} PLOs to address ethical responsibility, societal impact, and professional development.")
        
        return recommendations
    
    def get_cpf_framework(self) -> Dict[str, List[str]]:
        """Return the CPF framework for reference"""
        return self.cpf_plos
    
    def export_results(self, results: Dict[str, Any], format: str = 'json') -> str:
        """Export results in specified format"""
        if format == 'json':
            return json.dumps(results, indent=2)
        elif format == 'csv':
            # Create a flattened CSV format
            rows = []
            for result in results['detailed_results']:
                for match in result['matches']:
                    rows.append({
                        'Institutional PLO': result['institutional_plo'],
                        'CPF Theme': match['cpf_theme'],
                        'CPF Heading': match['cpf_heading'],
                        'CPF PLO': match['cpf_plo'],
                        'Similarity Score': match['similarity_score'],
                        'Alignment Score': match['alignment_score'],
                        'Common Terms': ', '.join(match['common_terms']),
                        'Bloom Alignment': match['bloom_alignment']
                    })
            df = pd.DataFrame(rows)
            return df.to_csv(index=False)
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'")
    
    def compare_with_other_frameworks(self, institutional_plos: List[str]) -> Dict[str, Any]:
        """Compare with other frameworks (Vision and Change, BioSkills, etc.)"""
        # This could be expanded to include other frameworks
        # For now, return CPF comparison with framework identification
        results = self.compare_plos(institutional_plos)
        results['framework'] = 'Canadian Program Framework (CPF)'
        return results 