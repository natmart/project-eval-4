"""
Tests for the statistics tracker module.
"""

import threading
import time
from datetime import date, timedelta
from collections import Counter

import pytest

from pyshort.stats import (
    StatsTracker,
    get_global_tracker,
    track_click,
    get_click_count,
    get_daily_stats,
    get_top_urls,
)


class TestStatsTracker:
    """Test the StatsTracker class functionality."""
    
    def test_initialization(self):
        """Test that StatsTracker initializes with empty counters."""
        tracker = StatsTracker()
        assert tracker.get_total_clicks() == 0
        assert tracker.get_unique_urls() == 0
        assert tracker.get_top_urls() == []
    
    def test_track_single_click(self):
        """Test tracking a single click."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        assert tracker.get_click_count("abc123") == 1
        assert tracker.get_total_clicks() == 1
        assert tracker.get_unique_urls() == 1
    
    def test_track_multiple_clicks_same_url(self):
        """Test tracking multiple clicks for the same URL."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        assert tracker.get_click_count("abc123") == 3
        assert tracker.get_total_clicks() == 3
    
    def test_track_multiple_different_urls(self):
        """Test tracking clicks for multiple different URLs."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        tracker.track_click("abc123")
        
        assert tracker.get_click_count("abc123") == 2
        assert tracker.get_click_count("xyz789") == 1
        assert tracker.get_total_clicks() == 3
        assert tracker.get_unique_urls() == 2
    
    def test_get_click_count_nonexistent(self):
        """Test getting click count for non-existent short code."""
        tracker = StatsTracker()
        assert tracker.get_click_count("nonexistent") == 0
    
    def test_track_click_with_explicit_date(self):
        """Test tracking click with explicit date."""
        tracker = StatsTracker()
        test_date = date(2024, 1, 15)
        tracker.track_click("abc123", test_date)
        
        daily_stats = tracker.get_daily_stats(test_date, test_date)
        assert test_date in daily_stats
        assert daily_stats[test_date]["abc123"] == 1
    
    def test_get_daily_stats_all(self):
        """Test getting all daily stats without date range."""
        tracker = StatsTracker()
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        tracker.track_click("abc123", date1)
        tracker.track_click("abc123", date2)
        tracker.track_click("xyz789", date1)
        
        daily_stats = tracker.get_daily_stats()
        assert date1 in daily_stats
        assert date2 in daily_stats
        assert daily_stats[date1]["abc123"] == 1
        assert daily_stats[date1]["xyz789"] == 1
        assert daily_stats[date2]["abc123"] == 1
    
    def test_get_daily_stats_with_range(self):
        """Test getting daily stats with date range."""
        tracker = StatsTracker()
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        date3 = date(2024, 1, 17)
        
        tracker.track_click("abc123", date1)
        tracker.track_click("abc123", date2)
        tracker.track_click("abc123", date3)
        
        # Range from date1 to date2
        stats = tracker.get_daily_stats(date1, date2)
        assert date1 in stats
        assert date2 in stats
        assert date3 not in stats
        assert stats[date1]["abc123"] == 1
        assert stats[date2]["abc123"] == 1
    
    def test_get_daily_stats_start_only(self):
        """Test getting daily stats with only start date."""
        tracker = StatsTracker()
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        tracker.track_click("abc123", date1)
        tracker.track_click("abc123", date2)
        
        stats = tracker.get_daily_stats(start_date=date1)
        assert date1 in stats
        assert date2 in stats
    
    def test_get_daily_stats_end_only(self):
        """Test getting daily stats with only end date."""
        tracker = StatsTracker()
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        tracker.track_click("abc123", date1)
        tracker.track_click("abc123", date2)
        
        stats = tracker.get_daily_stats(end_date=date1)
        assert date1 in stats
        assert date2 not in stats
    
    def test_get_top_urls_basic(self):
        """Test getting top URLs basic functionality."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        tracker.track_click("def456")
        tracker.track_click("def456")
        tracker.track_click("def456")
        
        top_urls = tracker.get_top_urls()
        assert len(top_urls) == 3
        assert top_urls[0] == ("def456", 3)
        assert top_urls[1] == ("abc123", 2)
        assert top_urls[2] == ("xyz789", 1)
    
    def test_get_top_urls_with_limit(self):
        """Test getting top URLs with limit."""
        tracker = StatsTracker()
        for i in range(10):
            tracker.track_click(f"url{i}", clicks=i+1)
        
        # Manually increment to create different counts
        for i in range(10):
            for _ in range(i):
                tracker.track_click(f"url{i}")
        
        top_urls = tracker.get_top_urls(limit=3)
        assert len(top_urls) == 3
    
    def test_get_top_urls_with_min_clicks(self):
        """Test getting top URLs with minimum click threshold."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        
        top_urls = tracker.get_top_urls(min_clicks=2)
        assert len(top_urls) == 1
        assert top_urls[0] == ("abc123", 3)
    
    def test_get_top_urls_limit_zero(self):
        """Test getting top URLs with limit=0 (unlimited)."""
        tracker = StatsTracker()
        for i in range(5):
            tracker.track_click(f"url{i}")
        
        top_urls = tracker.get_top_urls(limit=0)
        assert len(top_urls) == 5
    
    def test_get_total_clicks(self):
        """Test getting total clicks across all URLs."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        
        assert tracker.get_total_clicks() == 3
    
    def test_get_unique_urls(self):
        """Test getting count of unique URLs."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        tracker.track_click("abc123")  # Duplicate
        
        assert tracker.get_unique_urls() == 2
    
    def test_get_clicks_for_date(self):
        """Test getting total clicks for a specific date."""
        tracker = StatsTracker()
        test_date = date(2024, 1, 15)
        tracker.track_click("abc123", test_date)
        tracker.track_click("xyz789", test_date)
        tracker.track_click("abc123", date(2024, 1, 16))
        
        assert tracker.get_clicks_for_date(test_date) == 2
        assert tracker.get_clicks_for_date(date(2024, 1, 16)) == 1
    
    def test_reset_stats_specific_url(self):
        """Test resetting stats for specific URL."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        
        tracker.reset_stats("abc123")
        
        assert tracker.get_click_count("abc123") == 0
        assert tracker.get_click_count("xyz789") == 1
    
    def test_reset_stats_all(self):
        """Test resetting all stats."""
        tracker = StatsTracker()
        tracker.track_click("abc123")
        tracker.track_click("xyz789")
        
        tracker.reset_stats()
        
        assert tracker.get_total_clicks() == 0
        assert tracker.get_unique_urls() == 0
    
    def test_track_click_empty_short_code_raises(self):
        """Test that tracking with empty short code raises ValueError."""
        tracker = StatsTracker()
        with pytest.raises(ValueError, match="short_code must be a non-empty string"):
            tracker.track_click("")
    
    def test_track_click_none_short_code_raises(self):
        """Test that tracking with None short code raises ValueError."""
        tracker = StatsTracker()
        with pytest.raises(ValueError):
            tracker.track_click(None)
    
    def test_daily_stats_isolation(self):
        """Test that daily stats dicts don't share references."""
        tracker = StatsTracker()
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        tracker.track_click("abc123", date1)
        stats1 = tracker.get_daily_stats()
        
        tracker.track_click("xyz789", date2)
        stats2 = tracker.get_daily_stats()
        
        # stats1 should not have the new data
        assert date2 not in stats1
        assert date2 in stats2
        
        # Modifying returned dict should not affect internal state
        stats1_copy = stats1.copy()
        stats1_copy[date1]["new_code"] = 999
        
        stats1_again = tracker.get_daily_stats()
        assert "new_code" not in stats1_again.get(date1, {})


class TestThreadSafety:
    """Test thread-safety of StatsTracker operations."""
    
    def test_concurrent_click_tracking_same_url(self):
        """Test that concurrent tracking of same URL is thread-safe."""
        tracker = StatsTracker()
        num_threads = 10
        clicks_per_thread = 100
        
        def track_clicks():
            for _ in range(clicks_per_thread):
                tracker.track_click("abc123")
        
        threads = [threading.Thread(target=track_clicks) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        expected = num_threads * clicks_per_thread
        assert tracker.get_click_count("abc123") == expected
    
    def test_concurrent_click_tracking_different_urls(self):
        """Test concurrent tracking of different URLs."""
        tracker = StatsTracker()
        num_threads = 10
        clicks_per_thread = 50
        
        def track_clicks(thread_id):
            for _ in range(clicks_per_thread):
                tracker.track_click(f"url{thread_id}")
        
        threads = [threading.Thread(target=track_clicks, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert tracker.get_total_clicks() == num_threads * clicks_per_thread
        assert tracker.get_unique_urls() == num_threads
        
        for i in range(num_threads):
            assert tracker.get_click_count(f"url{i}") == clicks_per_thread
    
    def test_concurrent_mixed_operations(self):
        """Test concurrent mixed read/write operations."""
        tracker = StatsTracker()
        num_writer_threads = 5
        num_reader_threads = 5
        clicks_per_writer = 100
        read_counts = []
        lock = threading.Lock()
        
        def writer(thread_id):
            for _ in range(clicks_per_writer):
                tracker.track_click(f"url{thread_id}")
        
        def reader():
            for _ in range(clicks_per_writer):
                total = tracker.get_total_clicks()
                with lock:
                    read_counts.append(total)
                time.sleep(0.001)  # Small delay to interleave operations
        
        threads = []
        threads.extend(threading.Thread(target=writer, args=(i,)) for i in range(num_writer_threads))
        threads.extend(threading.Thread(target=reader) for _ in range(num_reader_threads))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify final state is consistent
        expected_total = num_writer_threads * clicks_per_writer
        assert tracker.get_total_clicks() == expected_total
        
        # Verify all reads were non-negative and reasonable
        assert all(0 <= count <= expected_total for count in read_counts)
    
    def test_concurrent_daily_tracking_same_date(self):
        """Test concurrent daily tracking for same date."""
        tracker = StatsTracker()
        num_threads = 20
        clicks_per_thread = 10
        test_date = date(2024, 1, 15)
        
        def track_clicks():
            for _ in range(clicks_per_thread):
                tracker.track_click("abc123", test_date)
        
        threads = [threading.Thread(target=track_clicks) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        expected = num_threads * clicks_per_thread
        assert tracker.get_click_count("abc123") == expected
        assert tracker.get_clicks_for_date(test_date) == expected
    
    def test_concurrent_top_urls_retrieval(self):
        """Test concurrent top URLs retrieval while tracking."""
        tracker = StatsTracker()
        num_threads = 10
        
        results = []
        lock = threading.Lock()
        
        def worker(thread_id):
            for i in range(50):
                tracker.track_click(f"url{thread_id}")
                if i % 10 == 0:  # Periodically read
                    top = tracker.get_top_urls(limit=5)
                    with lock:
                        results.append(len(top))
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify final state
        assert tracker.get_total_clicks() == num_threads * 50
        
        # Verify all reads returned valid results
        assert all(0 <= count <= 5 for count in results)
    
    def test_race_condition_prevention(self):
        """Test that race conditions are prevented with atomic operations."""
        tracker = StatsTracker()
        counter = [0]  # Use list for mutable reference in nested function
        
        def incrementer():
            for _ in range(100):
                tracker.track_click("counter")
                counter[0] += 1
        
        threads = [threading.Thread(target=incrementer) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Both counters should match exactly
        assert tracker.get_click_count("counter") == counter[0]
        assert tracker.get_click_count("counter") == 500


class TestGlobalTracker:
    """Test global tracker singleton and convenience functions."""
    
    def test_global_tracker_singleton(self):
        """Test that get_global_tracker returns same instance."""
        tracker1 = get_global_tracker()
        tracker2 = get_global_tracker()
        assert tracker1 is tracker2
    
    def test_convenience_functions(self):
        """Test convenience functions that use global tracker."""
        # Reset global tracker state
        get_global_tracker().reset_stats()
        
        track_click("test123")
        track_click("test123")
        track_click("xyz789")
        
        assert get_click_count("test123") == 2
        assert get_click_count("xyz789") == 1
        
        top = get_top_urls(limit=2)
        assert len(top) == 2
        assert top[0] == ("test123", 2)
        
        daily = get_daily_stats()
        assert len(daily) >= 1
    
    def test_global_tracker_isolation(self):
        """Test that global tracker maintains state across calls."""
        # Reset
        get_global_tracker().reset_stats()
        
        track_click("persistent")
        count1 = get_click_count("persistent")
        
        track_click("persistent")
        count2 = get_click_count("persistent")
        
        assert count2 == count1 + 1


def test_import():
    """Test that stats module can be imported."""
    import pyshort.stats
    assert hasattr(pyshort.stats, 'StatsTracker')
    assert hasattr(pyshort.stats, 'get_global_tracker')