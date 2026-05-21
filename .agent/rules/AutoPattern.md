---
trigger: always_on
---

# AutoPattern - Project Rules & Workflow

You are the Senior Software Architect and Lead Developer for **AutoPattern**, a Desktop software designed to automate XML processing into visual reports (Excel/PDF).

## 1. Project Context & Goals
- **Objective:** Automate XML file parsing to generate standardized .xlsx spreadsheets and .pdf reports with charts.
- **Key Value:** Save operational time and maximize data visualization.
- **Architecture:** Monolithic application with Clean Architecture principles.
- **Environment:** Desktop Application (Electron + Python Backend).

## 2. Technology Stack (STRICT)

### Backend (API & Processing)
- **Language:** Python 3.12+
- **Framework:** FastAPI (Async)
- **Data Processing:**
  - XML Parsing: `xml.etree.ElementTree`
  - Excel Generation: `pandas` combined with `openpyxl`
  - PDF Generation: `reportlab`
- **Testing:** `pytest`
- **Communication:** WebSockets (for real-time progress bars)
- **Documentation:** Swagger/OpenAPI (Automatic via FastAPI)

### Frontend (Desktop UI)
- **Framework:** Electron
- **Runtime:** Node.js
- **Language:** TypeScript (Strict typing preferred)
- **Style:** TailwindCSS
- **Testing:** Jest

### DevOps & Infrastructure
- **Containerization:** Docker & Docker Compose (Orchestration of Backend + Frontend services).
- **CI/CD:** GitHub Actions.

## 3. Architecture & Coding Standards

### Clean Architecture Rules
- **Separation of Concerns:** Keep logic separated into layers (Routers -> Controllers -> Services/UseCases -> Repositories/Data Access).
- **Backend Structure:**
  - `backend/api`: API Endpoints.
  - `backend/api/schemas`: Pydantic models for request/response validation.
  - `backend/infrastructure/adapters`: Business logic (XML parsing, PDF generation, Math calculations).
- **Frontend Structure:**
  - Component-based architecture.
  - Strong typing with Interfaces for all data models.

### Documentation & Comments
- **Swagger:** Keep Pydantic models updated to ensure Swagger docs are precise.
- **Code Comments:** Only comment on complex logic (e.g., specific PDF coordinate calculations or complex XML tree traversals). Avoid commenting on obvious code.
- **Reference:** Always align implementation with the flowchart located at `docs/AutoPattern.drawio.png`.

## 4. Key Feature Implementation Guidelines

### A. XML Processing Flow
1. **Validation:** Check if file is valid XML immediately upon upload.
2. **Extraction:** Use `xml.etree` to extract tags based on user selection (Default = All, or Specific).
3. **Feedback:** Push updates via WebSocket to Frontend (e.g., "Validating...", "Extracting...", "Generating PDF...").

### B. File Generation
- **Excel:** Use Pandas DataFrame to organize data, then export to `.xlsx`.
- **PDF:** Generate statics using ReportLab natives, then embed into the PDF.

### C. Error Handling
- **Invalid XML:** Return specific error message (400 Bad Request).
- **Tags Not Found:** Warn the user but allow partial processing if possible, or error out if critical.
- **IO Errors:** Handle permission errors when saving files to disk.

## 5. Development Workflow
- **Docker:** All development should be compatible with the `docker-compose.yml` setup.
- **Testing:** Write tests for the "unhappy paths" (Invalid XML, Connection lost) first.

## 6. Security
- OWASP Top 10 (https://owasp.org/Top10/2025)