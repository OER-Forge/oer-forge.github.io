---
title: RaiseMyHand
description: Real-time classroom question management system
draft: false
---

![RaiseMyHand Screenshot](/raisemyhand.png)

A real-time web-based classroom question management system that enables anonymous student participation and helps instructors prioritize questions during live classes.

## Overview

[RaiseMyHand](https://github.com/OER-Forge/raisemyhand/) addresses limitations of traditional hand-raising by removing participation barriers. It creates a more inclusive and responsive learning environment by letting students contribute anonymously while helping instructors focus on questions that matter most to the class.

## Key Features

- **Anonymous Submissions** – Students ask without fear of judgment
- **Real-Time Upvoting** – Questions auto-rank by student interest (Reddit-style voting)
- **QR Code Access** – Students join sessions instantly with their phones
- **Live Instructor Dashboard** – Monitor, moderate, and respond to questions in real-time
- **Content Moderation** – Automatic profanity filtering and instructor review
- **Presentation Mode** – Full-screen classroom display for projectors
- **Markdown Support** – Rich formatting for instructor responses
- **Data Export** – Download session reports as JSON or CSV
- **Security** – JWT authentication, CSRF protection, rate limiting, bcrypt hashing
- **Docker Deployment** – Production-ready containerization

## Technology Stack

- **Backend**: FastAPI with SQLAlchemy ORM, WebSocket support
- **Frontend**: Vanilla JavaScript with responsive design
- **Database**: SQLite (development) or PostgreSQL (production)
- **Deployment**: Docker/Docker Compose with Nginx support
- **Real-Time Communication**: WebSockets for instant updates

## Use Cases

Perfect for:
- Lecture halls and large classes
- Laboratory sessions and seminars
- Online and hybrid courses
- Interactive Q&A sessions
- Student feedback collection

## Resources

- **GitHub Repository**: [OER-Forge/raisemyhand](https://github.com/OER-Forge/raisemyhand)
- **Live Demo**: [raisemyhand.oerforge.org](https://raisemyhand.oerforge.org/)
- **Documentation**: Available in the GitHub repository
- **Report Issues**: [GitHub Issues](https://github.com/OER-Forge/raisemyhand/issues)
