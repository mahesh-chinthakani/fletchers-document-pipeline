import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

type DocumentStatus = {
  id: string;
  filename: string;
  file_type: string;
  status: "processing" | "completed" | "failed";
  extraction_method: string | null;
  error_message: string | null;
};

type Chunk = {
  sequence_number: number;
  page_number: number | null;
  content: string;
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [document, setDocument] = useState<DocumentStatus | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const pollStatus = async (documentId: string) => {
    for (let attempt = 0; attempt < 30; attempt++) {
      const response = await fetch(
        `${API_URL}/documents/${documentId}`
      );

      if (!response.ok) {
        throw new Error("Unable to check document status.");
      }

      const status: DocumentStatus = await response.json();
      setDocument(status);

      if (status.status === "completed") {
        const contentResponse = await fetch(
          `${API_URL}/documents/${documentId}/content`
        );

        if (!contentResponse.ok) {
          throw new Error("Unable to retrieve extracted content.");
        }

        const contentData = await contentResponse.json();
        setChunks(contentData.chunks);
        return;
      }

      if (status.status === "failed") {
        throw new Error(
          status.error_message || "Document processing failed."
        );
      }

      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    throw new Error("Document processing took too long.");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please choose a PDF or DOCX file.");
      return;
    }

    setUploading(true);
    setError("");
    setDocument(null);
    setChunks([]);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/documents`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setDocument({
        id: data.id,
        filename: data.filename,
        file_type: file.name.split(".").pop() || "",
        status: "processing",
        extraction_method: null,
        error_message: null,
      });

      await pollStatus(data.id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong.";

      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="page">
      <section className="container">
        <header className="header">
          <p className="eyebrow">Document Processing</p>
          <h1>Document Ingestion Pipeline</h1>
          <p className="subtitle">
            Upload a PDF or DOCX document to extract and retrieve its
            text content.
          </p>
        </header>

        <section className="card upload-card">
          <label className="file-label" htmlFor="document">
            Choose document
          </label>

          <input
            id="document"
            type="file"
            accept=".pdf,.docx"
            onChange={(event) =>
              setFile(event.target.files?.[0] || null)
            }
          />

          {file && (
            <p className="selected-file">
              Selected: <strong>{file.name}</strong>
            </p>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? "Processing..." : "Upload document"}
          </button>

          {error && <div className="error">{error}</div>}
        </section>

        {document && (
          <section className="card">
            <h2>Processing result</h2>

            <div className="details">
              <div>
                <span>File</span>
                <strong>{document.filename}</strong>
              </div>

              <div>
                <span>Status</span>
                <strong className={`status ${document.status}`}>
                  {document.status}
                </strong>
              </div>

              <div>
                <span>Extraction method</span>
                <strong>
                  {document.extraction_method || "Waiting..."}
                </strong>
              </div>
            </div>
          </section>
        )}

        {chunks.length > 0 && (
          <section className="card">
            <h2>Extracted content</h2>

            <div className="chunks">
              {chunks.map((chunk) => (
                <article
                  className="chunk"
                  key={chunk.sequence_number}
                >
                  <div className="chunk-header">
                    {chunk.page_number
                      ? `Page ${chunk.page_number}`
                      : `Chunk ${chunk.sequence_number}`}
                  </div>

                  <p>{chunk.content}</p>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;