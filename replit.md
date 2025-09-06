# YouTube Hub

## Overview

YouTube Hub is a Flask-based web application that allows users to create and manage a personal collection of YouTube videos. The application fetches video metadata using the YouTube Data API and provides features for organizing videos, sharing them via Discord webhooks, and viewing detailed information about each video in the collection.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Chosen as the lightweight Python web framework for rapid development and simplicity
- **Jinja2 Templates**: Used for server-side rendering with a responsive Bootstrap-based UI
- **Werkzeug ProxyFix**: Implemented for proper handling of proxy headers in deployment environments

### Database Layer
- **SQLAlchemy**: Selected as the ORM for database operations with Flask-SQLAlchemy integration
- **SQLite**: Used as the default database for development and small-scale deployments
- **Declarative Base**: Modern SQLAlchemy approach for model definitions
- **Database Configuration**: Includes connection pooling with 300-second recycle time and pre-ping health checks

### Data Models
- **Video Model**: Core entity storing YouTube video metadata including ID, title, description, thumbnails, view counts, like counts, and timestamps
- **Computed Properties**: youtube_url and formatted_message properties for convenient data access

### External API Integration
- **YouTube Data API v3**: Primary integration for fetching video metadata, statistics, and content details
- **URL Parsing**: Robust video ID extraction supporting multiple YouTube URL formats (watch, youtu.be, embed)
- **Error Handling**: Comprehensive error handling for API failures and invalid URLs

### Messaging Integration
- **Discord Webhooks**: Optional integration for sharing video notifications to Discord channels
- **Rich Embeds**: Formatted Discord messages with video thumbnails, descriptions, and statistics
- **Configurable Avatars**: Custom username and avatar support for Discord notifications

### Frontend Architecture
- **Bootstrap 5**: Responsive CSS framework with dark theme support
- **Font Awesome**: Icon library for consistent UI elements
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Interactive Features**: JavaScript for copy-to-clipboard functionality and dynamic UI interactions

### Security and Configuration
- **Environment Variables**: Secure API key management through environment variables
- **Session Management**: Flask session handling with configurable secret keys
- **Input Validation**: URL validation and sanitization for user inputs
- **Error Handling**: User-friendly error messages and graceful failure handling

### Application Structure
- **Route Separation**: Clean separation of concerns with dedicated routes module
- **Model Abstraction**: Separate models module for database entities
- **Service Layer**: Dedicated classes for YouTube API and Discord webhook interactions
- **Template Inheritance**: Base template with consistent navigation and styling

## External Dependencies

### Required APIs
- **YouTube Data API v3**: Required for fetching video metadata, statistics, and thumbnails
  - Needs API key stored in `YT_API_KEY` environment variable
  - Used for video details retrieval and URL validation

### Optional Integrations
- **Discord Webhooks**: Optional integration for sharing videos to Discord channels
  - Webhook URL stored in `DISCORD_WEBHOOK` environment variable
  - Supports rich embeds with video information

### Python Packages
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Requests**: HTTP client for external API calls
- **Werkzeug**: WSGI utilities and middleware

### Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN
- **Font Awesome 6**: Icon library loaded via CDN
- **Bootstrap JavaScript**: Interactive components loaded via CDN

### Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **SQLAlchemy**: Database abstraction and migration support
- **Environment Configuration**: Support for development and production configurations