"""
Job Enrichment System.

This module provides semantic enrichment for job postings, extracting implicit
information, inferring required competencies, and enhancing matching capabilities.
"""

from .enrichment_agent import enrich_job_posting

__all__ = ["enrich_job_posting"]

