video_extraction_prompt = """
Analyze the following video and provide a detailed scene-by-scene breakdown. For each scene:

1. Identify the start and end times in seconds
2. Provide a detailed description of what's happening
3. List key visual elements (people, objects, settings, etc.)
4. List key audio elements (music, speech, sound effects, etc.)
5. Describe the mood/atmosphere
6. List main actions or events

Guidelines:
- Break down the video into logical scenes based on content changes
- Be specific and detailed in descriptions
- Focus on the most important elements in each scene
- Maintain chronological order
- Include timestamps for each scene
- Consider both visual and audio elements
- Note any significant transitions or changes

Please analyze the video and provide a structured response following the VideoAnalysis model format.
"""