#!/usr/bin/env python3
"""
MDX-based Knowledge Base Handler
Handles reading, writing, and searching MDX files for the knowledge base
"""

import os
import re
import json
import frontmatter
import markdown
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class MDXKnowledgeBase:
    def __init__(self, mdx_directory: str = "knowledgebase/mdx"):
        self.mdx_directory = Path(mdx_directory)
        self.mdx_directory.mkdir(parents=True, exist_ok=True)
    
    def _get_mdx_files(self) -> List[Path]:
        """Get all MDX files in the knowledge base directory"""
        return list(self.mdx_directory.glob("*.mdx"))
    
    def _parse_mdx_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse an MDX file and extract frontmatter and content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter manually since the library seems to have issues
            frontmatter_data, markdown_content = self._parse_frontmatter(content)
            
            # Extract metadata from frontmatter
            metadata = {
                'id': file_path.stem,  # Use filename as ID
                'title': frontmatter_data.get('title', file_path.stem),
                'topic': frontmatter_data.get('topic', ''),
                'tags': frontmatter_data.get('tags', []),
                'created': frontmatter_data.get('created', ''),
                'updated': frontmatter_data.get('updated', ''),
                'filename': file_path.name,
                'filepath': str(file_path)
            }
            
            # Get content (both raw and HTML)
            content_raw = markdown_content
            content_html = markdown.markdown(content_raw)
            
            return {
                **metadata,
                'content_raw': content_raw,
                'content_html': content_html
            }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse frontmatter from content manually"""
        import yaml
        
        # Check if content starts with frontmatter
        if not content.startswith('---'):
            return {}, content
        
        # Find the end of frontmatter
        lines = content.split('\n')
        if len(lines) < 2:
            return {}, content
        
        # Find the second '---'
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return {}, content
        
        # Extract frontmatter
        frontmatter_text = '\n'.join(lines[1:end_index])
        markdown_content = '\n'.join(lines[end_index + 1:])
        
        try:
            frontmatter_data = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            frontmatter_data = {}
        
        return frontmatter_data, markdown_content
    
    
    def read_knowledge_base(self) -> List[Dict[str, Any]]:
        """Read all entries from the MDX knowledge base"""
        try:
            mdx_files = self._get_mdx_files()
            entries = []
            
            for file_path in mdx_files:
                entry = self._parse_mdx_file(file_path)
                if entry:
                    entries.append(entry)
            
            return entries
        except Exception as e:
            print(f"Error reading knowledge base: {e}")
            return []
    
    def add_to_knowledge_base(self, title: str, topic: str, content: str, tags: Optional[List[str]] = None) -> str:
        """Add new information to the MDX knowledge base"""
        try:
            import yaml
            
            # Create filename from title
            filename = self._create_filename(title)
            file_path = self.mdx_directory / f"{filename}.mdx"
            
            # Prepare frontmatter
            frontmatter_data = {
                'title': title,
                'topic': topic,
                'tags': tags or [],
                'created': datetime.now().strftime('%Y-%m-%d'),
                'updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Create MDX content with manual frontmatter
            frontmatter_yaml = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
            mdx_content = f"---\n{frontmatter_yaml}---\n\n{content}"
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(mdx_content)
            
            return f"Successfully added entry: {filename}.mdx"
        except Exception as e:
            return f"Error adding to knowledge base: {e}"
    
    def _create_filename(self, title: str) -> str:
        """Create a filename from a title"""
        # Convert to lowercase and replace spaces with hyphens
        filename = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        filename = re.sub(r'\s+', '-', filename.strip())
        
        # Ensure uniqueness
        base_filename = filename
        counter = 1
        while (self.mdx_directory / f"{filename}.mdx").exists():
            filename = f"{base_filename}-{counter}"
            counter += 1
        
        return filename
    
    def search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """Search for specific information in the MDX knowledge base"""
        try:
            entries = self.read_knowledge_base()
            if not entries:
                return []
            
            query_lower = query.lower()
            matching_entries = []
            
            # Common transcription variations and synonyms
            query_variations = self._generate_search_variations(query_lower)
            
            # Define priority mappings for specific queries - FILENAME FIRST, then tags
            priority_mappings = {
                # Services & Solutions
                'services': ['key_services.mdx', 'industries_served.mdx'],
                'solutions': ['key_services.mdx', 'industries_served.mdx'],
                'what services': ['key_services.mdx'],
                'offer': ['key_services.mdx', 'industries_served.mdx'],
                'services-offered': ['key_services.mdx'],
                'data-services': ['key_services.mdx', 'industries_served.mdx'],
                
                # Company Information
                'company': ['company_overview.mdx'],
                'overview': ['company_overview.mdx'],
                'about': ['company_overview.mdx'],
                'history': ['company_overview.mdx'],
                'founder': ['company_overview.mdx', 'leadership_team.mdx'],
                
                # Leadership & Team
                'leadership': ['leadership_team.mdx', 'board_of_directors.mdx'],
                'team': ['leadership_team.mdx'],
                'ceo': ['leadership_team.mdx'],
                'coo': ['leadership_team.mdx'],
                'chief operating officer': ['leadership_team.mdx'],
                'chief executive officer': ['leadership_team.mdx'],
                'cfo': ['leadership_team.mdx'],
                'chief financial officer': ['leadership_team.mdx'],
                'cto': ['leadership_team.mdx'],
                'chief technology officer': ['leadership_team.mdx'],
                'vp': ['leadership_team.mdx'],
                'vice president': ['leadership_team.mdx'],
                'executive': ['leadership_team.mdx'],
                'executives': ['leadership_team.mdx'],
                'management': ['leadership_team.mdx'],
                'board': ['board_of_directors.mdx', 'leadership_team.mdx'],
                'directors': ['board_of_directors.mdx'],
                
                # FAQs & Questions
                'faq': ['faqs.mdx'],
                'faqs': ['faqs.mdx'],
                'question': ['faqs.mdx'],
                'questions': ['faqs.mdx'],
                
                # Workforce & Operations
                'workforce': ['workforce_capacity.mdx'],
                'employees': ['workforce_capacity.mdx'],
                'capacity': ['workforce_capacity.mdx'],
                'staff': ['workforce_capacity.mdx'],
                
                # Location & Operations
                'location': ['where_we_operate.mdx'],
                'locations': ['where_we_operate.mdx'],
                'where': ['where_we_operate.mdx'],
                'operate': ['where_we_operate.mdx'],
                'centers': ['where_we_operate.mdx'],
                'yemmiganur': ['where_we_operate.mdx'],
                
                # Clients & Partnerships
                'clients': ['client_collaborations.mdx'],
                'collaborations': ['client_collaborations.mdx'],
                'partnerships': ['client_collaborations.mdx'],
                'swiggy': ['client_collaborations.mdx'],
                'healthifyme': ['client_collaborations.mdx'],
                
                # Contact & Support
                'contact': ['contact_information.mdx'],
                'support': ['contact_information.mdx'],
                'website': ['contact_information.mdx'],
                'demo': ['contact_information.mdx'],
                
                # Social Impact
                'social': ['social_impact.mdx'],
                'impact': ['social_impact.mdx'],
                'foundation': ['social_impact.mdx'],
                'community': ['social_impact.mdx'],
                
                # Awards & Recognition
                'awards': ['recognition_awards.mdx'],
                'recognition': ['recognition_awards.mdx'],
                'iaop': ['recognition_awards.mdx'],
                'rockefeller': ['recognition_awards.mdx'],
                'credibility': ['recognition_awards.mdx', 'why_choose_indivillage.mdx', 'leadership_team.mdx'],
                'trust': ['why_choose_indivillage.mdx', 'recognition_awards.mdx'],
                'reputation': ['recognition_awards.mdx', 'why_choose_indivillage.mdx'],
                'certifications': ['leadership_team.mdx', 'why_choose_indivillage.mdx'],
                'standards': ['leadership_team.mdx', 'why_choose_indivillage.mdx'],
                'quality': ['why_choose_indivillage.mdx', 'client_collaborations.mdx'],
                'reliable': ['why_choose_indivillage.mdx', 'client_collaborations.mdx'],
                
                # Why Choose
                'why': ['why_choose_indivillage.mdx'],
                'choose': ['why_choose_indivillage.mdx'],
                'differentiation': ['why_choose_indivillage.mdx'],
                'value': ['why_choose_indivillage.mdx']
            }
            
            # STEP 1: Check for priority filename matches first (HIGHEST PRIORITY)
            priority_files = []
            for key, files in priority_mappings.items():
                if key in query_lower:
                    priority_files.extend(files)
            
            # Remove duplicates and keep order
            priority_files = list(dict.fromkeys(priority_files))
            
            # STEP 2: If we have priority files, return them first
            if priority_files:
                for entry in entries:
                    filename = entry.get('filename', '')
                    if filename in priority_files:
                        matching_entries.append(entry)
                
                # Sort by priority order
                def sort_key(entry):
                    filename = entry.get('filename', '')
                    try:
                        return priority_files.index(filename)
                    except ValueError:
                        return len(priority_files)
                
                matching_entries.sort(key=sort_key)
                return matching_entries
            
            # STEP 3: If no priority files, search in content and tags (FALLBACK)
            for entry in entries:
                # Search in title, topic, content, and tags
                searchable_text = [
                    entry.get('title', ''),
                    entry.get('topic', ''),
                    entry.get('content_raw', ''),
                    ' '.join(entry.get('tags', []))
                ]
                
                searchable_text = ' '.join(searchable_text).lower()
                
                # Check if any variation matches
                for variation in query_variations:
                    if variation in searchable_text:
                        matching_entries.append(entry)
                        break
                
                # Also check for partial word matches (for compound words like IndiVillage)
                if not matching_entries or entry not in matching_entries:
                    if self._check_partial_matches(query_lower, searchable_text):
                        matching_entries.append(entry)
            
            return matching_entries
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def _generate_search_variations(self, query: str) -> List[str]:
        """Generate search variations for common transcription issues"""
        variations = [query]
        
        # Common transcription mappings with priority
        transcription_map = {
            'indivillage': ['in the village', 'india village', 'indie village', 'in village'],
            'machine learning': ['machine learning', 'machinelearning', 'ml', 'machine learn'],
            'data science': ['data science', 'datascience', 'data scientist'],
            'python': ['python', 'python programming', 'python language'],
            'social enterprise': ['social enterprise', 'socialenterprise', 'social enterprises'],
            'leadership': ['leadership', 'management', 'executives', 'ceo', 'coo', 'founder'],
            'services': ['services', 'solutions', 'data services', 'ai services'],
            'faqs': ['faqs', 'questions', 'frequently asked', 'common questions'],
            'workforce': ['workforce', 'employees', 'staff', 'team', 'capacity'],
            'locations': ['locations', 'centers', 'where we operate', 'geographic presence']
        }
        
        # Check if query matches any transcription variations
        matched_key = None
        for key, values in transcription_map.items():
            if key in query or any(val in query for val in values):
                matched_key = key
                variations.extend(values)
                variations.append(key)  # Add the correct form
                break  # Only match one key to avoid confusion
        
        # If no specific transcription match, add word variations (split compound words)
        if not matched_key:
            words = query.split()
            if len(words) > 1:
                # Try different combinations
                for i in range(len(words)):
                    for j in range(i + 1, len(words) + 1):
                        variation = ''.join(words[i:j])
                        if variation not in variations:
                            variations.append(variation)
        
        return list(set(variations))  # Remove duplicates
    
    def _check_partial_matches(self, query: str, searchable_text: str) -> bool:
        """Check for partial matches in compound words"""
        # Special handling for IndiVillage variations
        if 'village' in query.lower():
            # Only match if it's likely referring to IndiVillage
            if 'indivillage' in searchable_text.lower():
                # Check if this is a social enterprise entry (more specific)
                if 'social enterprise' in searchable_text.lower():
                    return True
                # Or if it's the only entry with "village" in the title
                if 'indivillage' in searchable_text.lower() and 'tech solutions' in searchable_text.lower():
                    return True
        
        # Remove spaces and special characters for comparison
        query_clean = re.sub(r'[^a-zA-Z0-9]', '', query)
        text_clean = re.sub(r'[^a-zA-Z0-9]', '', searchable_text)
        
        # Check if query is contained within any word in the text
        words_in_text = text_clean.split()
        for word in words_in_text:
            if query_clean in word or word in query_clean:
                return True
        
        # Check for common word combinations
        query_words = query.split()
        if len(query_words) >= 2:
            # Try combining words
            combined = ''.join(query_words)
            if combined in text_clean:
                return True
            
            # Try different word combinations
            for i in range(len(query_words)):
                for j in range(i + 1, len(query_words) + 1):
                    combo = ''.join(query_words[i:j])
                    if combo in text_clean:
                        return True
        
        return False
    
    def get_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific entry by ID (filename without extension)"""
        try:
            file_path = self.mdx_directory / f"{entry_id}.mdx"
            if file_path.exists():
                return self._parse_mdx_file(file_path)
            return None
        except Exception as e:
            print(f"Error getting entry {entry_id}: {e}")
            return None
    
    def update_entry(self, entry_id: str, title: str = None, topic: str = None, 
                    content: str = None, tags: List[str] = None) -> str:
        """Update an existing entry"""
        try:
            import yaml
            
            file_path = self.mdx_directory / f"{entry_id}.mdx"
            if not file_path.exists():
                return f"Entry {entry_id} not found"
            
            # Parse existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            frontmatter_data, markdown_content = self._parse_frontmatter(file_content)
            
            # Update fields
            if title is not None:
                frontmatter_data['title'] = title
            if topic is not None:
                frontmatter_data['topic'] = topic
            if content is not None:
                markdown_content = content
            if tags is not None:
                frontmatter_data['tags'] = tags
            
            # Update timestamp
            frontmatter_data['updated'] = datetime.now().strftime('%Y-%m-%d')
            
            # Create new MDX content
            frontmatter_yaml = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
            mdx_content = f"---\n{frontmatter_yaml}---\n\n{markdown_content}"
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(mdx_content)
            
            return f"Successfully updated entry: {entry_id}"
        except Exception as e:
            return f"Error updating entry: {e}"
    
    def delete_entry(self, entry_id: str) -> str:
        """Delete an entry by ID"""
        try:
            file_path = self.mdx_directory / f"{entry_id}.mdx"
            if file_path.exists():
                file_path.unlink()
                return f"Successfully deleted entry: {entry_id}"
            else:
                return f"Entry {entry_id} not found"
        except Exception as e:
            return f"Error deleting entry: {e}"
    
    def get_topics(self) -> List[str]:
        """Get all unique topics in the knowledge base"""
        try:
            entries = self.read_knowledge_base()
            topics = set()
            for entry in entries:
                topic = entry.get('topic', '')
                if topic:
                    topics.add(topic)
            return sorted(list(topics))
        except Exception as e:
            print(f"Error getting topics: {e}")
            return []
    
    def get_tags(self) -> List[str]:
        """Get all unique tags in the knowledge base"""
        try:
            entries = self.read_knowledge_base()
            tags = set()
            for entry in entries:
                entry_tags = entry.get('tags', [])
                tags.update(entry_tags)
            return sorted(list(tags))
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []
