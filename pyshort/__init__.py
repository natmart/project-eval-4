"""
pyshort - A simple URL shortener application
"""

from .stats import (
	StatsTracker,
	get_global_tracker,
	track_click,
	get_click_count,
	get_daily_stats,
	get_top_urls,
)

__version__ = "0.1.0"

__all__ = [
	"StatsTracker",
	"get_global_tracker",
	"track_click",
	"get_click_count",
	"get_daily_stats",
	"get_top_urls",
]