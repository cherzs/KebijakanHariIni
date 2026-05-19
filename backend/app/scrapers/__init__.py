from .base_scraper import BaseScraper
from .rss_scraper import RSSScraper
from .jdih_scraper import JDIHSetnegScraper
from .jdih_bpk_scraper import JDIHBPKScraper
from .dpr_scraper import DPRProlegnasScraper
from .kementerian_scraper import KementerianScraper

__all__ = [
    "BaseScraper",
    "RSSScraper",
    "JDIHSetnegScraper",
    "JDIHBPKScraper",
    "DPRProlegnasScraper",
    "KementerianScraper",
]