# 🚀 Next-Gen QA Automation Framework


## 📋 Executive Summary

This project is a high-performance, scalable, and **AI-enhanced** test automation framework designed specifically to demonstrate technical alignment with **Finom's QA Engineering standards**.

It goes beyond traditional automation by integrating **Self-Healing Infrastructure**, **AI-Powered Root Cause Analysis**, and **Cross-Architecture Support** (seamlessly running on both Apple Silicon & Intel chips).

### 🎯 Key Features (The "Wow" Factors)

* **🤖 AI-Powered Debugging:** When a test fails, the framework automatically sends the error logs to **Google Gemini** or **OpenAI**. The AI analyzes the root cause and injects a formatted solution directly into the Allure Report HTML.
* **🏗️ Smart Architecture Detection:** The `start_tests.py` script automatically detects the host CPU architecture (ARM64/M1 vs. AMD64) and dynamically builds/pulls the correct Docker images (Seleniarm vs. Selenoid), eliminating compatibility issues.
* **🛡️ Zero-Race-Condition Video Management:** A custom `VideoManager` listens to Docker Daemon events (`destroy` signal) to ensure test videos are perfectly saved or deleted based on the test result, guaranteeing 100% data integrity.
* **🌍 Localization & Globalization Testing:** Specific scenarios designed for **Finom.co** landing pages to verify country-specific compliance and language routing (DE, FR, NL, etc.).
* **📱 Unified Driver Factory:** A robust Factory Pattern implementation that manages Web (Chrome/Firefox), Remote (Selenoid), and Mobile (Android Appium) drivers from a single source of truth.
* **🗄️ Polyglot Database Testing:** Native support for verifying data integrity across both **SQL (PostgreSQL)** and **NoSQL (ArangoDB)** databases.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Typed, modular, and PEP-8 compliant. |
| **Framework** | Pytest | Fixture-based architecture for setup/teardown. |
| **Web UI** | Selenium WebDriver | Implemented with Page Object Model (POM). |
| **Mobile** | Appium 2.0 | Android automation (UiAutomator2). |
| **Infrastructure** | Docker Compose | Orchestrates Test Runner, Selenoid, and UI. |
| **Reporting** | Allure | Rich HTML reports with screenshots, videos, and AI analysis. |
| **CI/CD** | GitLab CI | Docker-in-Docker pipeline with artifact management. |

### 📂 Project Structure

```text
.
├── config/                 # Browser capabilities (ARM/Intel split)
├── locators/               # Centralized UI locators (Finom specific)
├── pages/                  # Page Object Model (POM) classes
├── tests/                  # Test scenarios (UI, API, DB, Mobile)
├── utilities/
│   ├── ai_debugger.py      # AI Error Analysis Module
│   ├── driver_factory.py   # Web & Mobile Driver Factory
│   ├── video_manager.py    # Docker Event Listener for Videos
│   └── db_client.py        # Database connectors
├── .gitlab-ci.yml          # CI/CD Pipeline definition
├── docker-compose.yml      # Infrastructure orchestration
├── start_tests.py          # Smart entry point script
└── requirements.txt        # Python dependencies



👨‍💻 Author

Süleyman Onur Şahin
Fullstack Software QA Engineer
Portfolio Focus: AI-Augmented Automation, Scalable Infrastructure
Contact: https://linkedin.com/in/suleymanonursahin/