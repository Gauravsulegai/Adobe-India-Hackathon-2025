# Adobe India Hackathon 2025: Connecting the Dots
## Round 1A: PDF Document Structure Extraction

### Overview

This project is a robust, high-performance solution for **Challenge 1A** of the Adobe India Hackathon. The mission is to transform raw PDFs into structured data by intelligently extracting their hierarchical outline (Title, H1, H2, etc.).

Our solution is packaged in a lightweight, offline Docker container and is engineered to process a wide variety of document types—from structured reports and forms to highly stylized flyers—with exceptional accuracy and speed.

### Our Approach: A Context-Aware Heuristic Engine

Recognizing that a one-size-fits-all rule set is insufficient for the diversity of PDF documents, we developed a **context-aware, multi-pass heuristic engine**. Instead of relying on a single attribute like font size, our engine analyzes the document as a whole to understand its context and then applies a sophisticated scoring model.

The process works as follows:

1.  **Contextual Analysis**: The engine first performs a quick scan of the entire document to determine its properties. Is it a dense, text-heavy report, a sparse form with many small labels, or a visually-driven flyer? This initial analysis allows the engine to adjust its strategy.

2.  **Candidate Scoring**: The solution processes the document in logical text blocks (not just single lines), preserving multi-line headings. Each block is scored based on a weighted combination of universal, language-agnostic features:
    * **Font Size**: Relative size compared to the document's main body text.
    * **Font Weight**: Boldness is detected using language-agnostic font metadata flags.
    * **Structural Patterns**: A high score is given to text that follows common heading patterns, like numbered lists ("1.", "2.1") or appendices.
    * **Contextual Clues**: The score is adjusted based on the document's context. For example, short, bold text in a "form-like" document is penalized, while large, stylized text in a "sparse" document (like an invitation) is given a significant boost.

3.  **Dynamic Level Assignment**: Finally, the scores are clustered to dynamically assign heading levels (H1, H2, H3, etc.) based on the document's own unique visual hierarchy. This allows the solution to adapt to any styling convention.

This intelligent, multi-layered approach ensures high accuracy and resilience, allowing the engine to "connect the dots" in a way that a simple rules-based system cannot.

### Libraries & Models

* **Primary Library**: **PyMuPDF (`fitz`)** for its high-speed and detailed PDF parsing.
* **No ML Models**: This solution is a pure, advanced heuristic engine and does not use any pre-trained machine learning models, ensuring it is lightweight and fast. All libraries are open-source.

### Submission Requirements Checklist

-   [x] **GitHub Project**: Complete and functional solution repository.
-   [x] **Dockerfile**: Located in the `round1a/` directory and fully functional.
-   [x] **README.md**: This file.

### Build and Run Commands

**Prerequisites**: Docker Desktop must be installed and running.

1.  **Build the Docker Image**:
    ```bash
    docker build --platform linux/amd64 -t round1a-solution round1a/
    ```

2.  **Run the Container**:
    _Place your PDFs in an `input` folder in the project root before running._
    ```bash
    docker run --rm -v /$(pwd)/input:/app/input -v /$(pwd)/output:/app/output --network none round1a-solution
    ```
    The processed JSON files will appear in an `output` folder.

### Validation Checklist

-   [x] **All PDFs in input directory are processed**: Yes.
-   [x] **JSON output files are generated for each PDF**: Yes.
-   [x] **Output format matches required structure**: Yes.
-   [x] **Processing completes within 10 seconds for 50-page PDFs**: Yes.
-   [x] **Solution works without internet access**: Yes.
-   [x] **Memory usage stays within 16GB limit**: Yes.
-   [x] **Compatible with AMD64 architecture**: Yes.