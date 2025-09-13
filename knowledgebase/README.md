# MDX Knowledge Base

This folder contains the MDX-based knowledge base functionality for the streaming LLM application.

## Files

- `mdx/` - Directory containing all MDX knowledge base files
- `mdx_handler.py` - Python handler for MDX knowledge base operations
- `README.md` - This documentation file

## Functionality

The MDX knowledge base supports the following operations:

### 1. Read Knowledge Base
- **Function**: `read_knowledge_base()`
- **Description**: Retrieves all entries from the MDX knowledge base
- **Usage**: Ask the LLM to "read the knowledge base" or "show me all stored information"

### 2. Add to Knowledge Base
- **Function**: `add_to_knowledge_base(title, topic, content, tags)`
- **Description**: Adds new information to the MDX knowledge base
- **Parameters**:
  - `title`: The title of the entry
  - `topic`: The topic or category of the information
  - `content`: The markdown content to be stored
  - `tags`: Optional array of tags to categorize the information
- **Usage**: Ask the LLM to "add this to the knowledge base" or "store this information"

### 3. Search Knowledge Base
- **Function**: `search_knowledge_base(query)`
- **Description**: Searches for specific information in the MDX knowledge base
- **Parameters**:
  - `query`: The search query to find relevant information
- **Usage**: Ask the LLM to "search the knowledge base for..." or "find information about..."

### 4. Get Topics
- **Function**: `get_topics()`
- **Description**: Gets all unique topics in the knowledge base
- **Usage**: Ask the LLM to "show me all topics" or "what topics are available"

### 5. Get Tags
- **Function**: `get_tags()`
- **Description**: Gets all unique tags in the knowledge base
- **Usage**: Ask the LLM to "show me all tags" or "what tags are available"

## Example Usage

1. **Adding information**: "Please add to the knowledge base a new entry titled 'Python Programming' about Python being a programming language"
2. **Searching**: "Search the knowledge base for Python"
3. **Reading all**: "Show me everything in the knowledge base"
4. **Getting topics**: "What topics are available in the knowledge base?"

## MDX File Structure

Each entry in the knowledge base is stored as an MDX file with the following structure:

```mdx
---
title: "Entry Title"
topic: "Topic Category"
tags: ["tag1", "tag2", "tag3"]
created: "2025-01-09"
updated: "2025-01-09"
---

# Entry Title

Your markdown content goes here...

## Section 1

Content with **bold** and *italic* formatting.

## Section 2

- List item 1
- List item 2
- List item 3

## Code Example

```python
def example():
    print("Hello, World!")
```
```

## Features

- **Markdown Support**: Full markdown formatting with headers, lists, code blocks, etc.
- **Frontmatter Metadata**: Structured metadata for easy organization
- **Automatic Filename Generation**: Creates clean filenames from titles
- **Rich Content**: Support for complex content with formatting
- **Search Capabilities**: Searches across titles, topics, content, and tags
- **Topic and Tag Organization**: Easy categorization and filtering

## Notes

- The knowledge base uses MDX files for rich, formatted content
- All entries are automatically timestamped when created/updated
- The search function performs case-insensitive matching across all fields
- MDX files are created automatically with proper frontmatter
- Content supports full markdown formatting including code blocks, links, and images
