/**
 * Word Processor Component
 * 
 * UI for creating and editing documents
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Button } from './Button';

interface Document {
  id: string;
  title: string;
  author?: string;
  created_at: string;
  modified_at: string;
  word_count: number;
}

interface Paragraph {
  text: string;
  style?: string;
  alignment: string;
  bold: boolean;
  italic: boolean;
  underline: boolean;
}

export function WordProcessor() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [docContent, setDocContent] = useState<Paragraph[]>([]);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newParagraph, setNewParagraph] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    if (selectedDoc) {
      loadDocument(selectedDoc);
    }
  }, [selectedDoc]);

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${apiBase}/word-processor/documents`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (err) {
      // Ignore errors
    }
  };

  const loadDocument = async (docId: string) => {
    try {
      const response = await fetch(`${apiBase}/word-processor/documents/${docId}`);
      if (response.ok) {
        const data = await response.json();
        setDocContent(data.paragraphs || []);
      }
    } catch (err) {
      setError('Failed to load document');
    }
  };

  const handleCreateDocument = async () => {
    if (!newDocTitle.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBase}/word-processor/documents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newDocTitle })
      });

      if (!response.ok) {
        throw new Error('Failed to create document');
      }

      const data = await response.json();
      setNewDocTitle('');
      await loadDocuments();
      setSelectedDoc(data.document_id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddParagraph = async () => {
    if (!selectedDoc || !newParagraph.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBase}/word-processor/documents/${selectedDoc}/paragraphs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newParagraph })
      });

      if (!response.ok) {
        throw new Error('Failed to add paragraph');
      }

      setNewParagraph('');
      await loadDocument(selectedDoc);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    if (!selectedDoc) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${apiBase}/word-processor/documents/${selectedDoc}/export?format=${format}`
      );
      if (response.ok) {
        const data = await response.json();
        alert(`Document exported to ${data.filename}`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Word Processor</CardTitle>
        <CardDescription>Create and edit documents</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Create New Document */}
          <div className="flex gap-2">
            <input
              type="text"
              className="flex-1 p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              placeholder="New document title..."
              value={newDocTitle}
              onChange={(e) => setNewDocTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreateDocument()}
            />
            <Button
              variant="primary"
              onClick={handleCreateDocument}
              isLoading={loading}
              disabled={!newDocTitle.trim()}
            >
              Create
            </Button>
          </div>

          {/* Document List */}
          {documents.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Document
              </label>
              <select
                className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                value={selectedDoc || ''}
                onChange={(e) => setSelectedDoc(e.target.value || null)}
              >
                <option value="">-- Select a document --</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.title} ({doc.word_count} words)
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Document Editor */}
          {selectedDoc && (
            <div className="space-y-4 border-t pt-4 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">Document Content</h3>

              {/* Add Paragraph */}
              <div className="flex gap-2">
                <textarea
                  className="flex-1 p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  placeholder="Add a new paragraph..."
                  rows={2}
                  value={newParagraph}
                  onChange={(e) => setNewParagraph(e.target.value)}
                />
                <Button
                  variant="primary"
                  onClick={handleAddParagraph}
                  isLoading={loading}
                  disabled={!newParagraph.trim()}
                >
                  Add
                </Button>
              </div>

              {/* Document Content */}
              <div className="border rounded-lg p-4 min-h-64 dark:border-gray-700 bg-white dark:bg-gray-800">
                {docContent.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 italic">
                    No content yet. Add a paragraph to get started.
                  </p>
                ) : (
                  docContent.map((para, idx) => (
                    <p
                      key={idx}
                      className={`mb-2 ${
                        para.bold ? 'font-bold' : ''
                      } ${para.italic ? 'italic' : ''} ${
                        para.underline ? 'underline' : ''
                      }`}
                      style={{ textAlign: para.alignment as any }}
                    >
                      {para.text}
                    </p>
                  ))
                )}
              </div>

              {/* Export Options */}
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleExport('docx')}
                  disabled={loading}
                >
                  Export DOCX
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleExport('pdf')}
                  disabled={loading}
                >
                  Export PDF
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleExport('html')}
                  disabled={loading}
                >
                  Export HTML
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleExport('markdown')}
                  disabled={loading}
                >
                  Export Markdown
                </Button>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">Error: {error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

