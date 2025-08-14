from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod
from vector_store import VectorStore, SearchResults


class Tool(ABC):
    """Abstract base class for all tools"""
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass


class CourseSearchTool(Tool):
    """Tool for searching course content with semantic course name matching"""
    
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self.last_sources = []  # Track sources from last search
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        return {
            "name": "search_course_content",
            "description": "Search course materials with smart course name matching and lesson filtering",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "What to search for in the course content"
                    },
                    "course_name": {
                        "type": "string",
                        "description": "Course title (partial matches work, e.g. 'MCP', 'Introduction')"
                    },
                    "lesson_number": {
                        "type": "integer",
                        "description": "Specific lesson number to search within (e.g. 1, 2, 3)"
                    }
                },
                "required": ["query"]
            }
        }
    
    def execute(self, query: str, course_name: Optional[str] = None, lesson_number: Optional[int] = None) -> str:
        """
        Execute the search tool with given parameters.
        
        Args:
            query: What to search for
            course_name: Optional course filter
            lesson_number: Optional lesson filter
            
        Returns:
            Formatted search results or error message
        """
        
        # Use the vector store's unified search interface
        results = self.store.search(
            query=query,
            course_name=course_name,
            lesson_number=lesson_number
        )
        
        # Handle errors
        if results.error:
            return results.error
        
        # Handle empty results
        if results.is_empty():
            filter_info = ""
            if course_name:
                filter_info += f" in course '{course_name}'"
            if lesson_number:
                filter_info += f" in lesson {lesson_number}"
            return f"No relevant content found{filter_info}."
        
        # Format and return results
        return self._format_results(results)
    
    def _format_results(self, results: SearchResults) -> str:
        """Format search results with course and lesson context"""
        formatted = []
        sources = []  # Track sources for the UI with links
        
        for doc, meta in zip(results.documents, results.metadata):
            course_title = meta.get('course_title', 'unknown')
            lesson_num = meta.get('lesson_number')
            
            # Build context header
            header = f"[{course_title}"
            if lesson_num is not None:
                header += f" - Lesson {lesson_num}"
            header += "]"
            
            # Track source for the UI with link if available
            source_text = course_title
            if lesson_num is not None:
                source_text += f" - Lesson {lesson_num}"
            
            # Try to get lesson link if we have a lesson number
            lesson_link = None
            if lesson_num is not None and course_title != 'unknown':
                lesson_link = self.store.get_lesson_link(course_title, lesson_num)
            
            # Store structured source data
            source_data = {
                "text": source_text,
                "url": lesson_link
            }
            sources.append(source_data)
            
            formatted.append(f"{header}\n{doc}")
        
        # Store sources for retrieval
        self.last_sources = sources
        
        return "\n\n".join(formatted)


class CourseOutlineTool(Tool):
    """Tool for getting course outlines with lesson lists"""
    
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self.last_sources = []  # Track sources from last search
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        return {
            "name": "get_course_outline",
            "description": "Get the complete outline of a course including all lesson numbers and titles",
            "input_schema": {
                "type": "object",
                "properties": {
                    "course_title": {
                        "type": "string",
                        "description": "The course title to get the outline for (partial matches work)"
                    }
                },
                "required": ["course_title"]
            }
        }
    
    def execute(self, course_title: str) -> str:
        """
        Execute the outline tool to get course structure.
        
        Args:
            course_title: Course title to search for
            
        Returns:
            Formatted course outline or error message
        """
        
        try:
            # Get all courses metadata
            all_courses = self.store.get_all_courses_metadata()
            
            # Find matching course (case-insensitive partial match)
            matching_course = None
            course_title_lower = course_title.lower()
            
            for course in all_courses:
                course_name = course.get('title', '').lower()
                if course_title_lower in course_name or course_name in course_title_lower:
                    matching_course = course
                    break
            
            if not matching_course:
                return f"No course found matching '{course_title}'. Available courses: {', '.join([c.get('title', 'Unknown') for c in all_courses])}"
            
            # Format the course outline
            return self._format_course_outline(matching_course)
            
        except Exception as e:
            return f"Error retrieving course outline: {str(e)}"
    
    def _format_course_outline(self, course_metadata: Dict[str, Any]) -> str:
        """Format course outline with title, link, and lessons"""
        
        title = course_metadata.get('title', 'Unknown Course')
        course_link = course_metadata.get('course_link', '')
        instructor = course_metadata.get('instructor', '')
        lessons = course_metadata.get('lessons', [])
        
        # Build the outline
        outline = []
        outline.append(f"**Course Title:** {title}")
        
        if course_link:
            outline.append(f"**Course Link:** {course_link}")
        
        if instructor:
            outline.append(f"**Instructor:** {instructor}")
        
        outline.append(f"**Number of Lessons:** {len(lessons)}")
        outline.append("")
        outline.append("**Course Outline:**")
        
        # Check for gaps in lesson numbering
        if lessons:
            lesson_numbers = [lesson.get('lesson_number') for lesson in lessons if lesson.get('lesson_number') is not None]
            if lesson_numbers:
                min_lesson = min(lesson_numbers)
                max_lesson = max(lesson_numbers)
                expected_lessons = set(range(min_lesson, max_lesson + 1))
                actual_lessons = set(lesson_numbers)
                missing_lessons = expected_lessons - actual_lessons
                if missing_lessons:
                    outline.append(f"*Note: Missing lessons: {sorted(missing_lessons)}*")
                    outline.append("")
        
        # Add lesson list (sorted by lesson number)
        if lessons:
            # Sort lessons by lesson_number to ensure consecutive order
            sorted_lessons = sorted(lessons, key=lambda x: x.get('lesson_number', 0))
            
            for lesson in sorted_lessons:
                lesson_num = lesson.get('lesson_number', 'N/A')
                lesson_title = lesson.get('lesson_title', lesson.get('title', 'Untitled Lesson'))
                lesson_link = lesson.get('lesson_link')
                
                if lesson_link:
                    outline.append(f"- Lesson {lesson_num}: {lesson_title} - [{lesson_link}]({lesson_link})")
                else:
                    outline.append(f"- Lesson {lesson_num}: {lesson_title}")
        else:
            outline.append("- No lessons found")
        
        # Store source data for the UI
        sources = []
        
        # Add main course link
        sources.append({
            "text": f"{title} - Course Outline",
            "url": course_link if course_link else None
        })
        
        # Add individual lesson links (sorted by lesson number)
        if lessons:
            # Use the same sorted lessons for consistency
            sorted_lessons = sorted(lessons, key=lambda x: x.get('lesson_number', 0))
            
            for lesson in sorted_lessons:
                lesson_num = lesson.get('lesson_number', 'N/A')
                lesson_title = lesson.get('lesson_title', lesson.get('title', 'Untitled Lesson'))
                lesson_link = lesson.get('lesson_link')
                
                if lesson_link:
                    sources.append({
                        "text": f"Lesson {lesson_num}: {lesson_title}",
                        "url": lesson_link
                    })
        
        self.last_sources = sources
        
        return "\n".join(outline)


class ToolManager:
    """Manages available tools for the AI"""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, tool: Tool):
        """Register any tool that implements the Tool interface"""
        tool_def = tool.get_tool_definition()
        tool_name = tool_def.get("name")
        if not tool_name:
            raise ValueError("Tool must have a 'name' in its definition")
        self.tools[tool_name] = tool

    
    def get_tool_definitions(self) -> list:
        """Get all tool definitions for Anthropic tool calling"""
        return [tool.get_tool_definition() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name with given parameters"""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        
        return self.tools[tool_name].execute(**kwargs)
    
    def get_last_sources(self) -> list:
        """Get sources from the last search operation"""
        # Check all tools for last_sources attribute
        for tool in self.tools.values():
            if hasattr(tool, 'last_sources') and tool.last_sources:
                # Return structured sources for clickable links in frontend
                sources = []
                for source in tool.last_sources:
                    if isinstance(source, dict):
                        # Return structured source data with text and url
                        sources.append({
                            'text': source.get('text', ''),
                            'url': source.get('url', None)
                        })
                    else:
                        # Handle legacy string sources
                        sources.append({
                            'text': str(source),
                            'url': None
                        })
                return sources
        return []

    def reset_sources(self):
        """Reset sources from all tools that track sources"""
        for tool in self.tools.values():
            if hasattr(tool, 'last_sources'):
                tool.last_sources = []