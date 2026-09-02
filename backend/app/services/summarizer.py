import asyncio
import json
import time
import logging
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.llm import get_groq_llm
from app.core.config import GROQ_MODEL, MAX_CONCURRENT_SUMMARIES, CHUNK_SIZE, CHUNK_OVERLAP
from app.services.youtube import clean_transcript_text

logger = logging.getLogger(__name__)

DEFAULT_SUMMARY_PROMPT = """
You are an expert summarizer. Summarize the following content clearly and accurately.

Guidelines:
- Use English strictly for the summary response.
- Explain key concepts, steps, logic, and core takeaways.
- Exclude code syntax, personal remarks, or unrelated info.
- Use clear section titles and bullet points.
- Keep it concise, direct, and faithful to the original text.

Content:
{text}

Final Summary:
"""

COMBINE_SUMMARY_PROMPT = """
You are an expert editor. Below are individual summary sections generated from different parts of the same transcript, in sequential order.

Synthesize these section summaries into one coherent, unified, and well-structured final summary.

Guidelines:
- Maintain chronological and logical progression.
- Eliminate redundant or repeated information across sections.
- Use clear section titles and clean bullet points.
- Preserve key insights, steps, and takeaways.
- Do not invent information or omit major concepts.

Sequential Section Summaries:
{text}

Final Unified Summary:
"""

prompt = PromptTemplate(template=DEFAULT_SUMMARY_PROMPT, input_variables=["text"])
combine_prompt = PromptTemplate(template=COMBINE_SUMMARY_PROMPT, input_variables=["text"])


async def safe_summarize(
    text: str,
    chunk_index: int = 1,
    total_chunks: int = 1,
    max_retries: int = 3
) -> str:
    """Summarizes text chunk using Groq with rate-limit retry backoff for TPM limits."""
    if not text or not text.strip():
        return "No content found."

    prompt_str = prompt.format(text=text)
    char_count = len(text)
    payload_bytes = len(prompt_str.encode("utf-8"))
    model_name = GROQ_MODEL or "openai/gpt-oss-20b"
    est_tokens = len(text) // 4  # Practical estimation (~4 chars per token)

    logger.info(
        f"📊 [Groq Request Payload] Chunk {chunk_index}/{total_chunks} | "
        f"Chars: {char_count} | Payload: {payload_bytes} bytes | "
        f"Est. Tokens: ~{est_tokens} | Model: {model_name}"
    )

    llm = get_groq_llm()
    chain = prompt | llm | StrOutputParser()

    for attempt in range(max_retries):
        try:
            return await chain.ainvoke({"text": text})
        except Exception as e:
            err_msg = str(e)
            err_lower = err_msg.lower()
            is_rate_limit = any(k in err_lower for k in ["413", "429", "rate_limit", "tokens per minute", "tpm"])

            if is_rate_limit and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5.0
                logger.warning(
                    f"⏳ [Groq Rate Limit/TPM Exceeded] Chunk {chunk_index}/{total_chunks} attempt {attempt + 1}/{max_retries}. Backing off for {wait_time:.1f}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ [Groq Error] Chunk {chunk_index}/{total_chunks} failed: {err_msg}")
                raise RuntimeError(f"Groq API Error: {err_msg}")


async def summarize_chunks(chunks: List[str]) -> List[str]:
    """
    Summarizes chunks concurrently using bounded parallelism (Semaphore = MAX_CONCURRENT_SUMMARIES).
    Preserves exact positional transcript ordering via asyncio.gather().
    """
    total = len(chunks)
    max_concurrency = MAX_CONCURRENT_SUMMARIES
    semaphore = asyncio.Semaphore(max_concurrency)

    logger.info(f"🚀 Processing {total} chunks concurrently (Bounded Concurrency Limit = {max_concurrency})")

    async def worker(index: int, chunk_text_str: str) -> str:
        async with semaphore:
            logger.info(f"🤖 Processing chunk {index + 1}/{total} ({len(chunk_text_str)} chars)...")
            res = await safe_summarize(chunk_text_str, chunk_index=index + 1, total_chunks=total)
            logger.info(f"✅ Chunk {index + 1}/{total} completed.")
            return res

    tasks = [worker(i, chunk) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks)
    return list(results)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    cleaned = clean_transcript_text(text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=CHUNK_OVERLAP)
    docs = splitter.create_documents([cleaned])
    return [doc.page_content for doc in docs]


async def summarize_long_content(content_input: Any) -> str:
    """Unified summarization pipeline for transcripts list or raw text string with timing."""
    start_time = time.perf_counter()

    if isinstance(content_input, list):
        full_text = " ".join([line.get("text", "") for line in content_input if isinstance(line, dict)])
    else:
        full_text = str(content_input)

    chunks = chunk_text(full_text)
    logger.info(f"📦 Created {len(chunks)} text chunks (Chunk Size: {CHUNK_SIZE} chars / ~{CHUNK_SIZE // 4} tokens) for Groq processing.")

    if not chunks:
        return "No content found."

    chunk_summaries = await summarize_chunks(chunks)

    # Single-chunk optimization: skip redundant final synthesis call
    if len(chunk_summaries) == 1:
        elapsed = time.perf_counter() - start_time
        logger.info(f"⚡ Single summary chunk generated. Skipping final synthesis call. (Duration: {elapsed:.2f}s)")
        return chunk_summaries[0].strip()

    # Final synthesis step for multiple chunk summaries
    logger.info(f"🔄 Performing final synthesis on {len(chunk_summaries)} chunk summaries...")
    combined_input = "\n\n--- Next Section ---\n\n".join(chunk_summaries)

    llm = get_groq_llm()
    chain = combine_prompt | llm | StrOutputParser()

    try:
        final_summary = await chain.ainvoke({"text": combined_input})
        elapsed = time.perf_counter() - start_time
        logger.info(f"⏱️ Total summarization pipeline completed in {elapsed:.2f}s across {len(chunks)} chunks.")
        return final_summary.strip()
    except Exception as e:
        logger.error(f"Error during final summary synthesis: {e}")
        elapsed = time.perf_counter() - start_time
        logger.warning(f"Falling back to concatenated summaries. Total duration: {elapsed:.2f}s")
        return "\n\n".join(chunk_summaries)
