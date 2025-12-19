# UI Preview Guide

## Quick Preview - Run Streamlit

To see the UI in action, run:

```powershell
cd knowledge-base-ui
streamlit run app.py
```

This will automatically open your browser at `http://localhost:8501`

---

## Visual Layout Preview

### Main Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 Personal Knowledge Base with RAG                       │
│  Ask questions about your documents and get AI-powered      │
│  answers with context.                                      │
│                                                             │
│  [💬 Ask Questions] [📤 Upload Documents] [📚 Manage Docs] │
└─────────────────────────────────────────────────────────────┘
```

---

### Tab 1: 💬 Ask Questions

```
┌─────────────────────────────────────────────────────────────┐
│  💬 Ask Questions                                           │
├─────────────────────────────────────┬───────────────────────┤
│                                     │                       │
│  💬 Ask a Question                  │  ℹ️ About            │
│  ┌─────────────────────────────┐    │                       │
│  │ Your Question:             │    │  This knowledge base │
│  │ e.g., What is vector...    │    │  uses:               │
│  └─────────────────────────────┘    │  • BigQuery Vector   │
│                                     │  • Gemini & OpenAI   │
│  [🔍 Search]                        │  • Google Cloud Run  │
│                                     │                       │
│  ✅ Answer found!                   │  📊 System Status    │
│  🌐 Answer generated using web...   │  🟢 RAG API: Online  │
│                                     │                       │
│  📝 Answer                          │  ─────────────────   │
│  ┌─────────────────────────────┐    │  Powered by Google   │
│  │ [Answer text appears here]  │    │  Cloud & OpenAI     │
│  └─────────────────────────────┘    │                       │
│                                     │                       │
│  📚 Sources                         │                       │
│  ▼ Source 1 - Score: 0.856          │                       │
│    Document: Research Paper          │                       │
│    Chunk 0                          │                       │
│    [Source content...]               │                       │
│                                     │                       │
└─────────────────────────────────────┴───────────────────────┘
```

**Features:**
- Question input field
- Search button
- Answer display with source type indicator
- Expandable source citations with scores
- System status indicator
- About section

---

### Tab 2: 📤 Upload Documents

```
┌─────────────────────────────────────────────────────────────┐
│  📤 Upload Documents                                        │
├─────────────────────────────────────┬───────────────────────┤
│                                     │                       │
│  📤 Upload Documents                 │  📋 Supported        │
│  Upload instruction, research, or   │  Formats             │
│  guidance files to add them to your  │                       │
│  knowledge base.                    │  • PDF (.pdf)         │
│                                     │  • Word (.docx)       │
│  ┌─────────────────────────────┐    │  • Text (.txt)        │
│  │ Choose a file to upload     │    │  • Markdown (.md)     │
│  │ [Browse Files]              │    │                       │
│  └─────────────────────────────┘    │  💡 Tips              │
│                                     │                       │
│  ┌─────────────────────────────┐    │  • Documents are      │
│  │ Document Name (optional)    │    │    automatically      │
│  │ Leave empty to use filename│    │    chunked            │
│  └─────────────────────────────┘    │  • Each chunk is     │
│                                     │    embedded           │
│  [📤 Upload Document]               │  • Large documents   │
│                                     │    may take longer    │
│  ✅ Document uploaded successfully!  │                       │
│  {                                  │                       │
│    "Document Name": "Test Doc",     │                       │
│    "Chunks Created": 5,             │                       │
│    "Total Characters": 1234         │                       │
│  }                                  │                       │
│                                     │                       │
└─────────────────────────────────────┴───────────────────────┘
```

**Features:**
- File uploader with drag-and-drop
- Optional custom document name
- Upload button
- Success message with document stats
- Supported formats info
- Tips section

---

### Tab 3: 📚 Manage Documents

```
┌─────────────────────────────────────────────────────────────┐
│  📚 Manage Documents                                        │
│  View and manage documents in your knowledge base.         │
│                                                             │
│  [🔄 Refresh Document List]                                │
│                                                             │
│  ✅ Found 3 document(s) in the knowledge base              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Research Paper.pdf                    │ [🗑️ Delete] │   │
│  │ 15 chunks                             │            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ───────────────────────────────────────────────────────── │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Instructions.docx                    │ [🗑️ Delete] │   │
│  │ 8 chunks                              │            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ───────────────────────────────────────────────────────── │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Guidance Document.txt                │ [🗑️ Delete] │   │
│  │ 12 chunks                             │            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Refresh button
- Document list with names and chunk counts
- Delete button for each document
- Empty state message when no documents exist

---

## Color Scheme & Styling

- **Primary Color**: Streamlit default blue
- **Success**: Green checkmarks and success messages
- **Info**: Blue info boxes for answers
- **Warning**: Yellow for warnings
- **Error**: Red for errors
- **Icons**: Emoji-based for visual clarity

---

## Interactive Features

1. **File Upload**: Drag-and-drop or click to browse
2. **Real-time Status**: System status updates automatically
3. **Expandable Sources**: Click to expand/collapse source citations
4. **Delete Confirmation**: Delete buttons with immediate feedback
5. **Auto-refresh**: Document list can be refreshed on demand

---

## Responsive Design

- **Wide Layout**: Optimized for desktop screens
- **Two-column Layout**: Main content + sidebar info
- **Mobile-friendly**: Streamlit automatically adapts to smaller screens

---

## To See It Live

1. **Install dependencies:**
   ```powershell
   cd knowledge-base-ui
   pip install -r requirements.txt
   ```

2. **Start the backend** (in another terminal):
   ```powershell
   cd rag-api
   python app.py
   ```

3. **Start Streamlit:**
   ```powershell
   cd knowledge-base-ui
   streamlit run app.py
   ```

4. **Browser opens automatically** at `http://localhost:8501`

---

## Screenshots Location

After running, you can take screenshots of:
- The main page with tabs
- Upload interface
- Document management
- Query results with sources

