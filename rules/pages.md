---
trigger: model_decision
description: 生成页面README或者理解页面结构
globs: lib/pages/*
---

# Page Documentation Standard

## Directory Structure
- The `lib/pages` directory contains all page implementations of the application
- Each page has its own subdirectory at `lib/pages/{page_name}`
- Each page directory contains a [README.md] file that provides complete documentation for that page

## README.md Content Guidelines
Each page's README.md file should include the following core sections:

### 1. Directory Structure
Clearly list all files and subdirectories within the page directory, with brief descriptions of each file's purpose.

### 2. Page Entry Points
Provide detailed information on how users can access this page, including:
- Navigation paths (which pages can lead to this page)
- Trigger methods (which buttons, menu items to click, etc.)
- Invocation methods (routing methods used, such as `context.pushAppRoute()`)

### 3. Page Components
Describe the main functional areas and components of the page:
- Purpose and content of each area
- Main components and widgets used
- Relationships and interactions between different parts

### 4. Special Considerations
Explain items that require special attention during development and maintenance:
- Design style and standards
- Special requirements for functionality implementation
- Known limitations or areas for improvement
- Dependencies and data sources

## Usage Guidelines
1. **Pre-modification Reading**: Developers must read the README.md file before making any changes to a page
2. **Timely Updates**: After any modification to a page, the README.md file must be updated accordingly
3. **Maintain Consistency**: Ensure documentation descriptions remain consistent with actual code implementation
4. **Use Chinese**: README.md content should be written in Chinese to ensure smooth team communication

By strictly following these standards, we can ensure synchronization between code and documentation, improving team collaboration efficiency and code maintainability.