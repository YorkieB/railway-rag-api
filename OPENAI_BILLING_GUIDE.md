# OpenAI Billing Guide for Jarvis Project

## Models Used in This Project

Your project uses **two OpenAI models**:

### 1. **GPT-4o** (Primary Model)
**Used for:**
- RAG answer generation (`/query` endpoint)
- Vision analysis (multimodal queries)
- WebSocket multimodal communication

**Pricing** (as of 2025):
- **Input tokens**: ~$2.50 per 1M tokens
- **Output tokens**: ~$10.00 per 1M tokens
- **Average cost**: ~$6.25 per 1M tokens (mixed input/output)

**Usage**: This is your **main cost driver**. Each query generates:
- Input: System prompt + RAG context + user question (~500-2000 tokens)
- Output: Generated answer (~100-500 tokens)

### 2. **text-embedding-3-small** (Embeddings Model)
**Used for:**
- Document embeddings (when uploading documents)
- Query embeddings (when searching)
- Memory embeddings (for memory system)

**Pricing** (as of 2025):
- **Cost**: ~$0.02 per 1M tokens (very cheap!)
- **Usage**: ~1536 tokens per embedding

**Usage**: This is **very low cost**. Each document upload creates multiple embeddings (one per chunk).

## Cost Breakdown Example

### Typical Query Cost:
- **RAG Query**: ~1,000 input tokens + ~200 output tokens = **~$0.0025 per query**
- **Embedding Search**: ~0.001 tokens = **~$0.00002 per search**

### Document Upload Cost:
- **10-page document** (~5,000 words):
  - Embeddings: ~10 chunks × 1,536 tokens = **~$0.0003**
  - **Total upload cost**: ~$0.0003 (negligible)

## Recommended Billing Plan

### For Development/Testing:
- **Pay-as-you-go** plan is fine
- Set a **monthly spending limit** ($10-20 recommended)
- Monitor usage in OpenAI dashboard

### For Production:
- **Pay-as-you-go** with higher limits
- Set **daily budget limits** in code (already implemented: 500K tokens/day, $10/day)
- Consider **usage-based billing** if high volume

## Cost Optimization Tips

### 1. Use GPT-4o (Current Choice) ✅
- **Best balance** of cost and performance
- Faster than GPT-4 Turbo
- Good for RAG + vision tasks

### 2. Alternative: GPT-4o-mini (If Budget Constrained)
- **Much cheaper**: ~$0.15/$0.60 per 1M tokens (input/output)
- **Trade-off**: Slightly lower quality
- **Recommendation**: Use for non-critical queries

### 3. Keep text-embedding-3-small ✅
- Already the cheapest embedding model
- No need to change

## Budget Settings in Code

Your project already has budget enforcement:
- **Daily token limit**: 500,000 tokens (default)
- **Daily dollar limit**: $10.00 (default)
- **Warning threshold**: 80% utilization

These can be adjusted in `rag-api/cost.py`.

## Estimated Monthly Costs

### Light Usage (100 queries/day):
- Queries: 100 × $0.0025 = **$0.25/day** = **~$7.50/month**
- Embeddings: Negligible (~$0.10/month)
- **Total**: ~**$8/month**

### Medium Usage (1,000 queries/day):
- Queries: 1,000 × $0.0025 = **$2.50/day** = **~$75/month**
- Embeddings: ~$1/month
- **Total**: ~**$76/month**

### Heavy Usage (10,000 queries/day):
- Queries: 10,000 × $0.0025 = **$25/day** = **~$750/month**
- Embeddings: ~$10/month
- **Total**: ~**$760/month**

## What to Set Up in OpenAI Dashboard

1. **Add Payment Method**: 
   - Go to https://platform.openai.com/account/billing
   - Add credit card or payment method

2. **Set Spending Limits**:
   - **Hard limit**: Set maximum monthly spend
   - **Soft limit**: Get alerts at 80% usage

3. **Monitor Usage**:
   - Check dashboard regularly
   - Review token usage by model
   - Track costs per endpoint

## Current Issue: Quota Exceeded

Your API key has exceeded its quota. To resolve:

1. **Check Account Status**:
   - Visit https://platform.openai.com/account/billing
   - Verify payment method is added
   - Check if account has spending limits

2. **Add Credits** (if on prepaid):
   - Add credits to your account
   - Or switch to pay-as-you-go

3. **Upgrade Plan** (if needed):
   - Free tier has very limited quota
   - Upgrade to paid plan for higher limits

## Recommendation

**For this project, use:**
- ✅ **GPT-4o** for answer generation (current choice - good balance)
- ✅ **text-embedding-3-small** for embeddings (current choice - cheapest)
- ✅ **Pay-as-you-go** billing plan
- ✅ **Set $10-20/month spending limit** for development

**No model changes needed** - your current setup is cost-effective!

