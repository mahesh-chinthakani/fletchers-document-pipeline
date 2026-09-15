# Document Ingestion Pipeline

A small full-stack document processing application that accepts PDF and DOCX files, extracts their text content using the appropriate strategy, persists the results, and exposes processing status and extracted content through a REST API.

The project was designed as a simple take-home implementation with an emphasis on clear code, separation of responsibilities, testability, and extensibility.

## Features

- Upload PDF and DOCX documents
- Generate a unique tracking ID for each upload
- Process documents asynchronously from the client's perspective
- Extract digital PDF text using `pypdf`
- Detect PDFs where direct text extraction is insufficient
- Route those PDFs through a mocked OCR service
- Extract DOCX paragraph content using `python-docx`
- Persist document metadata and extracted chunks using SQLite
- Poll document processing status
- Retrieve extracted document content through a REST API
- React + TypeScript frontend
- Automated tests using pytest

## Architecture

```text
                    React + TypeScript
                           |
                           | REST API
                           v
                       FastAPI
                           |
                           v
                   DocumentProcessor
                           |
                           v
                   ExtractorRegistry
                     /           \
                    /             \
                   v               v
            PdfExtractor       DocxExtractor
                 |                  |
               pypdf            python-docx
                 |
                 v
        Meaningful text found?
             /          \
           yes           no
            |             |
            v             v
      Digital PDF     OCR Service
                          |
                          v
                    MockOCRService

                           |
                           v
                         SQLite
                    /              \
             Document metadata   Extracted chunks
```

## Document Processing Flow

When a document is uploaded, the API creates a document record with a generated UUID and an initial `processing` status.

The extractor registry selects the appropriate extractor based on the file extension.

For DOCX files, `python-docx` extracts non-empty paragraphs and preserves their original sequence.

For PDFs, `pypdf` first attempts direct text extraction. If enough meaningful text is found, the PDF is treated as a digital PDF. If direct extraction produces insufficient text, the document is routed to the OCR abstraction.

The OCR implementation is intentionally mocked for this assessment. This demonstrates the integration boundary without requiring a paid external OCR provider.

Extracted content is stored as ordered chunks alongside document metadata. The processing status is then updated to either `completed` or `failed`.

## Technology Choices

### FastAPI

FastAPI provides a lightweight Python REST API with straightforward file upload support and automatically generated OpenAPI documentation.

### React + TypeScript

React provides a simple frontend for file upload, status polling, and displaying extracted content. TypeScript adds type safety around API responses and UI state.

### SQLite

SQLite provides persistence without introducing unnecessary infrastructure for a small take-home application.

For a production system with higher concurrency and data volumes, I would consider PostgreSQL.

### pypdf

`pypdf` is used for machine-readable PDF text extraction. It allows digital PDFs to be processed locally without sending every document to an external OCR provider.

### python-docx

`python-docx` is used to extract standard paragraph text from DOCX files.

### OCR abstraction

The OCR service is defined behind an interface and injected into the PDF extractor.

The assessment uses `MockOCRService`, but a production implementation could use a provider such as Azure Document Intelligence, AWS Textract, or another OCR service without changing the PDF routing logic.

## API

### Upload a document

```http
POST /documents
```

Accepts a PDF or DOCX file.

Returns HTTP `202 Accepted` with a tracking ID.

Example:

```json
{
  "id": "f633b171-e9d9-4572-8057-4c980b6fbba0",
  "filename": "example.pdf",
  "status": "processing"
}
```

### Check processing status

```http
GET /documents/{document_id}
```

Example response:

```json
{
  "id": "f633b171-e9d9-4572-8057-4c980b6fbba0",
  "filename": "example.pdf",
  "file_type": "pdf",
  "status": "completed",
  "extraction_method": "digital_pdf",
  "created_at": "2026-09-14 23:25:12",
  "error_message": null
}
```

### Retrieve extracted content

```http
GET /documents/{document_id}/content
```

Example:

```json
{
  "document_id": "f633b171-e9d9-4572-8057-4c980b6fbba0",
  "chunks": [
    {
      "sequence_number": 1,
      "page_number": 1,
      "content": "Extracted page text..."
    }
  ]
}
```

### Health check

```http
GET /health
```

## Running the Project

### Backend

Create and activate a Python virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

Start the API:

```powershell
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

## Tests

Run the backend test suite from the repository root:

```powershell
pytest -v
```

Current test coverage includes:

```text
Registry selects PDF extractor
Registry selects DOCX extractor
Unsupported file types are rejected
DOCX extraction preserves non-empty paragraphs
Digital PDFs use direct extraction
No-text PDFs route to OCR
Unsupported API uploads return HTTP 400
Health endpoint responds successfully
```

Current result:

```text
8 passed
```

The frontend production build can be verified with:

```powershell
cd frontend
npm run build
```

## Design Decisions

### Why use a registry?

The extractor registry keeps document-specific routing outside the API and processing service.

Adding another file format only requires implementing another extractor and registering its extension.

### Why store content as chunks?

Document metadata and extracted text have different responsibilities.

Storing content as ordered chunks makes it easier to preserve page or paragraph ordering and provides a cleaner foundation for future retrieval or AI-agent use.

PDF chunks retain page numbers. DOCX chunks retain sequence numbers because DOCX documents do not provide stable PDF-style page boundaries.

### Why polling?

Polling keeps the frontend implementation simple while still separating upload from processing.

The upload endpoint returns a tracking ID, and the frontend periodically checks the document status.

For this take-home, this provides an appropriate balance between clarity and functionality.

### Why is OCR mocked?

Real OCR typically requires an external service, credentials, infrastructure, or additional native dependencies.

The mock demonstrates the important architectural behaviour: detecting when normal PDF extraction is insufficient and routing the document through an OCR boundary.

## Adding TXT Support

I would create a `TextExtractor` implementing the same `BaseExtractor` contract.

The registry could then be extended with:

```python
".txt": TextExtractor()
```

The API, processing service, persistence layer, and frontend would not require major changes.

## Scaling to 100x the Volume

The current implementation is intentionally optimized for simplicity rather than high throughput.

At significantly larger scale, I would move document processing out of the FastAPI process and use a durable queue with separate worker processes.

I would also consider PostgreSQL instead of SQLite for concurrent writes, object storage for original documents, a production OCR provider, configurable retry policies, structured logging and monitoring, and horizontally scalable API and worker services.

The existing extractor abstraction and processing boundary are intended to make those changes possible without redesigning the entire application.

## Current Limitations

The PDF routing decision currently uses a simple document-level text-length heuristic. A production implementation could evaluate text quality and coverage on a page-by-page basis.

DOCX extraction currently focuses on standard paragraph text. Tables, headers, footers, and text embedded in images could be added later.

OCR is mocked and does not perform real image recognition.

FastAPI background tasks run inside the application process and are not a durable job queue.

SQLite is appropriate for this small local implementation but would not be my first choice for a high-concurrency production workload.

Authentication, authorization, malware scanning, file-size limits, rate limiting, and cloud deployment are outside the scope of this implementation.

## Production Improvements

For production I would consider:

```text
PostgreSQL
Object/blob storage
Durable job queue and worker service
Real OCR integration
File-size/type validation
Malware scanning
Authentication and authorization
Retry and dead-letter handling
Structured logging and observability
Containerisation
CI/CD
Cloud deployment
```

The goal of the take-home implementation was to keep the core processing flow clear rather than introduce infrastructure that was not required to demonstrate the solution.


## Further Questions

### 1. What scalable production architecture would support this pipeline?

For production, I would separate document upload from processing. The API would accept the document, store the original file in object storage, create a processing record in a production database such as PostgreSQL, and place a processing job onto a durable message queue.

Independent workers could then process documents, perform extraction or OCR where required, store the extracted content, and update the document status. This would allow the API and document-processing workers to scale independently.

I would also introduce retries, structured logging, monitoring, authentication, stronger file validation, and a production OCR provider.

### 2. How would the design change to support plain-text files?

I would add a `TextExtractor` implementing the existing `BaseExtractor` interface and register the `.txt` extension in the `ExtractorRegistry`.

Because plain-text files do not require document parsing or OCR, the extractor could decode the uploaded bytes and return the content as one or more ordered chunks.

The API, `DocumentProcessor`, persistence layer, and frontend would require little or no structural change.

### 3. How would the design change if document uploads increased by 100x?

I would move document processing out of FastAPI `BackgroundTasks` and use a durable queue with independently scalable worker processes.

I would replace SQLite with PostgreSQL or another production database suitable for concurrent workloads, store original documents in object storage, and add retries, monitoring, rate controls, and stronger failure handling.

The API and workers could then be scaled horizontally depending on upload and processing demand.
