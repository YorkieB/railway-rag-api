/**
 * Main API Client
 * 
 * Re-exports all API functions for convenience.
 * Import from here: import { query, getBudgetStatus } from '@/lib/api'
 */

// Re-export memory functions
export {
  createMemory,
  listMemories,
  getMemory,
  updateMemory,
  deleteMemory,
  searchMemories,
} from "./api-memory";

// Re-export budget functions
export { getBudgetStatus } from "./api-budget";

// Re-export browser functions
export * from "./api-browser";

// Add your existing API functions here
// Example:
// export { query, uploadDocument } from "./api-rag";

