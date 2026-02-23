# apps/feedback/services/trend_analyzer.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count
import statistics
from collections import defaultdict


class TrendAnalyzer:
    """
    Service class for analyzing feedback trends within a time period
    """
    
    @staticmethod
    def calculate_monthly_trend(feedbacks, month_start, month_end):
        """
        Calculate trend based on rating patterns within the month
        Returns: 'improving', 'declining', 'stable', 'volatile', 'consistent'
        """
        if feedbacks.count() < 2:
            return 'stable'  # Not enough data for trend analysis
        
        # Method 1: Weekly progression analysis
        weekly_trend = TrendAnalyzer._analyze_weekly_progression(feedbacks, month_start, month_end)
        if weekly_trend:
            return weekly_trend
        
        # Method 2: Sequential time-based analysis
        sequential_trend = TrendAnalyzer._analyze_sequential_pattern(feedbacks)
        if sequential_trend:
            return sequential_trend
        
        # Method 3: Statistical analysis
        statistical_trend = TrendAnalyzer._analyze_statistical_pattern(feedbacks)
        return statistical_trend
    
    @staticmethod
    def _analyze_weekly_progression(feedbacks, month_start, month_end):
        """Analyze trend by comparing weekly averages"""
        weekly_data = TrendAnalyzer._get_weekly_breakdown(feedbacks, month_start, month_end)
        
        if len(weekly_data) >= 2:
            ratings = [week['average_rating'] for week in weekly_data if week['average_rating'] is not None]
            
            if len(ratings) >= 2:
                # Split into halves for comparison
                first_half = ratings[:len(ratings)//2]
                second_half = ratings[len(ratings)//2:]
                
                if first_half and second_half:
                    avg_first = sum(first_half) / len(first_half)
                    avg_second = sum(second_half) / len(second_half)
                    
                    # Determine trend based on significant changes
                    difference = avg_second - avg_first
                    
                    if difference > 0.3:  # Significant improvement
                        return 'improving'
                    elif difference < -0.3:  # Significant decline
                        return 'declining'
                    elif max(ratings) - min(ratings) > 1.0:  # High volatility
                        return 'volatile'
        
        return None
    
    @staticmethod
    def _analyze_sequential_pattern(feedbacks):
        """Analyze trend by looking at chronological rating sequence"""
        ordered_feedbacks = feedbacks.order_by('created_at')
        
        if ordered_feedbacks.count() >= 3:
            ratings = [fb.rating for fb in ordered_feedbacks]
            
            # Calculate moving direction
            improvements = 0
            declines = 0
            stable_points = 0
            
            for i in range(1, len(ratings)):
                diff = ratings[i] - ratings[i-1]
                
                if diff > 0.2:  # Significant improvement
                    improvements += 1
                elif diff < -0.2:  # Significant decline
                    declines += 1
                else:  # Stable
                    stable_points += 1
            
            total_changes = improvements + declines
            
            if total_changes > 0:
                improvement_ratio = improvements / total_changes
                
                if improvement_ratio >= 0.7:  # Mostly improvements
                    return 'improving'
                elif improvement_ratio <= 0.3:  # Mostly declines
                    return 'declining'
                elif improvements > 0 and declines > 0:  # Mixed pattern
                    return 'volatile'
            
            # If mostly stable with minimal changes
            if stable_points >= len(ratings) * 0.7:
                return 'consistent'
        
        return None
    
    @staticmethod
    def _analyze_statistical_pattern(feedbacks):
        """Analyze trend using statistical methods"""
        ratings = [fb.rating for fb in feedbacks]
        
        if len(ratings) < 2:
            return 'stable'
        
        # Calculate standard deviation to measure volatility
        stdev = statistics.stdev(ratings) if len(ratings) > 1 else 0
        
        # High volatility indicates inconsistent performance
        if stdev > 1.0:
            return 'volatile'
        
        # Check for linear trend using simple linear regression
        try:
            x = list(range(len(ratings)))
            slope = TrendAnalyzer._calculate_slope(x, ratings)
            
            if slope > 0.1:  # Positive slope
                return 'improving'
            elif slope < -0.1:  # Negative slope
                return 'declining'
        except:
            pass
        
        # Low standard deviation indicates consistent performance
        if stdev < 0.3:
            return 'consistent'
        
        return 'stable'
    
    @staticmethod
    def _calculate_slope(x, y):
        """Calculate slope of simple linear regression"""
        n = len(x)
        if n == 0:
            return 0
            
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0
            
        return (n * sum_xy - sum_x * sum_y) / denominator
    
    @staticmethod
    def _get_weekly_breakdown(feedbacks, month_start, month_end):
        """Break down feedbacks by week for trend analysis"""
        weekly_breakdown = []
        current_week_start = month_start
        
        while current_week_start <= month_end:
            week_end = min(current_week_start + timedelta(days=6), month_end)
            
            week_feedbacks = feedbacks.filter(
                created_at__date__gte=current_week_start,
                created_at__date__lte=week_end
            )
            
            week_avg = week_feedbacks.aggregate(Avg('rating'))['rating__avg']
            
            if week_feedbacks.exists():
                weekly_breakdown.append({
                    'week_start': current_week_start,
                    'average_rating': week_avg,
                    'feedback_count': week_feedbacks.count()
                })
            
            current_week_start += timedelta(days=7)
        
        return weekly_breakdown
    
    @staticmethod
    def get_trend_insight(trend, employee_name, average_rating):
        """Generate human-readable insight based on trend"""
        insights = {
            'improving': f"{employee_name} shows positive progress this month with improving ratings",
            'declining': f"{employee_name}'s performance needs attention with declining ratings",
            'volatile': f"{employee_name} shows inconsistent performance with varying ratings",
            'consistent': f"{employee_name} maintains consistent performance throughout the month", 
            'stable': f"{employee_name} shows stable performance with an average of {average_rating}"
        }
        return insights.get(trend, f"{employee_name}'s performance trend: {trend}")
    
    @staticmethod
    def get_trend_icon(trend):
        """Get visual icon for trend"""
        icons = {
            'improving': '📈',
            'declining': '📉', 
            'volatile': '📊',
            'consistent': '✅',
            'stable': '➡️'
        }
        return icons.get(trend, '➡️')
    
    @staticmethod
    def get_trend_color(trend):
        """Get color code for trend"""
        colors = {
            'improving': '#28a745',  # Green
            'declining': '#dc3545',  # Red
            'volatile': '#ffc107',   # Yellow
            'consistent': '#17a2b8', # Teal
            'stable': '#6c757d'      # Gray
        }
        return colors.get(trend, '#6c757d')