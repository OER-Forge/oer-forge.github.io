---
title: WikiAccess
description: Convert DokuWiki to accessible documents
draft: false
---

![WikiAccess Document Outputs](/wikiaccess-samplepage.png)

Transform DokuWiki pages into accessible, WCAG 2.1 compliant documents in multiple formats.

## Overview

WikiAccess is an open-source tool that converts DokuWiki pages into professionally formatted, accessible outputs. It's designed for educational institutions and content creators needing to convert wiki-based materials into formats suitable for diverse audiences while maintaining comprehensive accessibility standards.

## Key Features

### Document Generation
- **Multiple Output Formats**: Semantic HTML5, Microsoft Word (.docx), and Markdown
- **Mathematical Equations**: LaTeX → MathJax for HTML, OMML for Word conversion
- **Responsive Design**: Works across devices with dark mode capability
- **Image Handling**: Automatically downloads images while preserving alt-text metadata
- **Video Support**: Generates YouTube thumbnails for embedded videos

![WikiAccess Screenshot](/wikiaccess-dashboard.png)

### Accessibility & Compliance
- **WCAG 2.1 Compliance**: Validates against AA and AAA standards
- **pa11y Testing**: Implements 50+ accessibility rules with interactive reporting
- **Per-Page Scoring**: Individual and aggregate compliance metrics
- **Accessibility Reports**: Comprehensive dashboards and audit trails

![WikiAccess Page](/wikiaccess-page.png)


### Link & Content Management
- **Link Detection**: Identifies broken internal wiki links
- **Conversion Tracking**: Suggests missing page conversions
- **Link Analytics**: Tracks relationships for content analysis
- **Database Tracking**: SQLite-based conversion history

### Batch Processing
- **Incremental Processing**: Skips previously-converted content for efficiency
- **Batch Management**: Handle multiple pages in a single conversion run
- **Statistics Export**: Generate batch processing reports

## Technology Stack

- **Language**: Python 3.7+
- **Document Processing**: BeautifulSoup4, python-docx, Pandoc
- **Accessibility Testing**: Node.js with pa11y
- **Image Processing**: Pillow
- **Data Storage**: SQLite3
- **HTTP Requests**: requests library

## Output Organization

Converted materials are organized into structured directories:
- HTML pages with accessibility reports
- Word documents (.docx)
- Markdown source files
- Downloaded images with metadata
- Central accessibility reporting hub

## Use Cases

- Converting course materials to accessible formats
- Creating WCAG-compliant documentation
- Archiving wiki content with compliance validation
- Generating multiple document formats from a single source
- Ensuring educational materials meet accessibility standards

## Resources

- **GitHub Repository**: [OER-Forge/wikiaccess](https://github.com/OER-Forge/wikiaccess)
- **License**: MIT - Open for reuse and modification

## Getting Started

For installation and usage instructions, please visit the [GitHub repository](https://github.com/OER-Forge/wikiaccess).
