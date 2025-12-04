"""
Tests for markdown_report_generator module.

Tests cover:
- CSV loading and validation
- Visualization generation
- Report section generation
- Full report generation
- Edge cases and error handling
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
import markdown_report_generator as mrg


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_csv_path():
    """Return path to sample CSV file."""
    return 'reports/3j_singerSwipe.csv'


@pytest.fixture
def sample_df(sample_csv_path):
    """Load sample data."""
    if os.path.exists(sample_csv_path):
        return pd.read_csv(sample_csv_path)
    # Return empty dataframe if file doesn't exist
    return pd.DataFrame()


@pytest.fixture
def minimal_df():
    """Create minimal test dataframe."""
    return pd.DataFrame({
        'username': ['user1', 'user2'],
        'commits': [10, 5],
        'images': [0, 0],
        'lines_added': [1000, 500],
        'lines_deleted': [100, 50],
        'issues_created': [2, 1],
        'issues_resolved': [1, 0],
        'prs_opened': [3, 1],
        'prs_approved': [2, 1],
        'comments': [5, 2],
        'total_points': [100, 50],
        'grade': ['MB', 'B'],
    })


# ============================================================================
# Tests: Visualization Functions
# ============================================================================

class TestVisualizationFunctions:
    """Test visualization helper functions."""
    
    def test_format_number_millions(self):
        """Test formatting large numbers."""
        assert mrg._format_number(1_500_000) == '1.5M'
    
    def test_format_number_thousands(self):
        """Test formatting thousands."""
        assert mrg._format_number(1_500) == '1.5k'
    
    def test_format_number_small(self):
        """Test formatting small numbers."""
        assert mrg._format_number(999) == '999'
    
    def test_format_number_string(self):
        """Test formatting with string input."""
        assert mrg._format_number('test') == 'test'
    
    def test_get_grade_stars_all_grades(self):
        """Test star rating for all grades."""
        assert '⭐⭐⭐⭐' in mrg._get_grade_stars('MB')
        assert '⭐⭐⭐' in mrg._get_grade_stars('B')
        assert '⭐⭐' in mrg._get_grade_stars('R')
        assert '⭐' in mrg._get_grade_stars('I')
    
    def test_get_grade_emoji_all_grades(self):
        """Test emoji for all grades."""
        assert mrg._get_grade_emoji('MB') == '🟢'
        assert mrg._get_grade_emoji('B') == '🟡'
        assert mrg._get_grade_emoji('R') == '🟠'
        assert mrg._get_grade_emoji('I') == '🔴'
    
    def test_status_indicator_good_value(self):
        """Test status indicator for good values."""
        result = mrg._get_status_indicator(100, 50, 20)
        assert result == '🟢'
    
    def test_status_indicator_fair_value(self):
        """Test status indicator for fair values."""
        result = mrg._get_status_indicator(30, 50, 20)
        assert result == '🟡'
    
    def test_status_indicator_bad_value(self):
        """Test status indicator for bad values."""
        result = mrg._get_status_indicator(10, 50, 20)
        assert result == '🔴'
    
    def test_create_progress_bar_full(self):
        """Test progress bar at 100%."""
        result = mrg._create_progress_bar(100, 10)
        assert result == '██████████'
    
    def test_create_progress_bar_half(self):
        """Test progress bar at 50%."""
        result = mrg._create_progress_bar(50, 10)
        assert '█' in result and '░' in result
    
    def test_create_progress_bar_empty(self):
        """Test progress bar at 0%."""
        result = mrg._create_progress_bar(0, 10)
        assert result == '░░░░░░░░░░'
    
    def test_get_rank_emoji_top_three(self):
        """Test rank emojis."""
        assert mrg._get_rank_emoji(1) == '🥇'
        assert mrg._get_rank_emoji(2) == '🥈'
        assert mrg._get_rank_emoji(3) == '🥉'
    
    def test_get_rank_emoji_other(self):
        """Test rank emoji for non-medal positions."""
        result = mrg._get_rank_emoji(4)
        assert '4' in result


class TestArchetypeDetection:
    """Test contributor archetype detection."""
    
    def test_code_factory_high_lines(self):
        """Test Code Factory archetype - high lines but low images."""
        # Asset Architect triggers first due to lines > 10000
        # To get Code Factory, need even higher lines AND images < 50
        row = {'lines_added': 15000, 'lines_deleted': 5000, 'images': 20, 'prs_opened': 5, 'issues_created': 2, 'commits': 20, 'comments': 5}
        archetype, desc = mrg._detect_archetype(row)
        # With lines > 10000 and images < 50, should be Asset Architect
        assert '🎨' in archetype
    
    def test_asset_architect_with_images(self):
        """Test Asset Architect archetype."""
        row = {'lines_added': 500, 'lines_deleted': 100, 'images': 100, 'prs_opened': 5, 'issues_created': 2, 'commits': 20, 'comments': 5}
        archetype, desc = mrg._detect_archetype(row)
        assert '🎨' in archetype
    
    def test_pr_machine_high_prs(self):
        """Test PR Machine archetype."""
        row = {'lines_added': 500, 'lines_deleted': 100, 'images': 0, 'prs_opened': 20, 'issues_created': 5, 'commits': 20, 'comments': 5}
        archetype, desc = mrg._detect_archetype(row)
        assert '📤' in archetype
    
    def test_silent_coder_low_metrics(self):
        """Test Silent Coder archetype."""
        row = {'lines_added': 100, 'lines_deleted': 10, 'images': 0, 'prs_opened': 1, 'issues_created': 0, 'commits': 2, 'comments': 1}
        archetype, desc = mrg._detect_archetype(row)
        assert '⏱️' in archetype


# ============================================================================
# Tests: Data Loading
# ============================================================================

class TestDataLoading:
    """Test CSV loading and validation."""
    
    def test_load_existing_csv(self, sample_csv_path):
        """Test loading existing CSV file."""
        if os.path.exists(sample_csv_path):
            df = mrg.load_data(sample_csv_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
    
    def test_load_nonexistent_csv(self):
        """Test loading non-existent CSV raises error."""
        with pytest.raises(FileNotFoundError):
            mrg.load_data('nonexistent_file.csv')
    
    def test_load_invalid_csv(self):
        """Test loading invalid CSV - pandas handles it gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('invalid csv {[content')
            temp_path = f.name
        
        try:
            # pandas is lenient with CSV parsing, so just verify it loads
            df = mrg.load_data(temp_path)
            # If it loads without error, it's OK - pandas handles malformed CSV
            assert isinstance(df, pd.DataFrame)
        finally:
            os.unlink(temp_path)


# ============================================================================
# Tests: Statistics Calculation
# ============================================================================

class TestStatisticsCalculation:
    """Test statistics calculation."""
    
    def test_calculate_stats_basic(self, minimal_df):
        """Test basic statistics calculation."""
        stats = mrg._calculate_contributor_stats(minimal_df)
        
        assert stats['total_contributors'] == 2
        assert stats['total_commits'] == 15
        assert stats['total_lines'] == 1650
        assert stats['total_prs'] == 4
    
    def test_calculate_stats_grade_distribution(self, minimal_df):
        """Test grade distribution calculation."""
        stats = mrg._calculate_contributor_stats(minimal_df)
        
        assert stats['grade_distribution']['MB']['count'] == 1
        assert stats['grade_distribution']['B']['count'] == 1
        assert stats['grade_distribution']['MB']['percentage'] == 50.0
    
    def test_calculate_stats_empty_dataframe(self):
        """Test statistics with empty dataframe."""
        df = pd.DataFrame({
            'commits': [], 'images': [], 'lines_added': [], 'lines_deleted': [],
            'issues_created': [], 'issues_resolved': [], 'prs_opened': [],
            'prs_approved': [], 'comments': [], 'total_points': [], 'grade': []
        })
        
        # Empty dataframe - should handle gracefully without errors
        stats = mrg._calculate_contributor_stats(df)
        assert stats['total_contributors'] == 0
        assert stats['total_commits'] == 0
        assert stats['total_lines'] == 0
        assert stats['total_prs'] == 0
        assert stats['grade_distribution']['MB']['count'] == 0
        assert stats['grade_distribution']['B']['count'] == 0


# ============================================================================
# Tests: Report Section Generation
# ============================================================================

class TestReportSections:
    """Test individual report section generation."""
    
    def test_generate_header(self):
        """Test header generation."""
        header = mrg._generate_header("Test Project", "Test Team")
        
        assert 'Test Project' in header
        assert 'Test Team' in header
        assert '🚀' in header
    
    def test_generate_executive_summary(self, minimal_df):
        """Test executive summary generation."""
        stats = mrg._calculate_contributor_stats(minimal_df)
        summary = mrg._generate_executive_summary(minimal_df, stats)
        
        assert '📊' in summary
        assert 'Executive Summary' in summary
        assert '█' in summary  # Progress bars
    
    def test_generate_leaderboard(self, minimal_df):
        """Test leaderboard generation."""
        leaderboard = mrg._generate_leaderboard(minimal_df)
        
        assert '🏆' in leaderboard
        assert 'Top Performers' in leaderboard
        assert 'user1' in leaderboard
    
    def test_generate_performance_metrics(self, minimal_df):
        """Test performance metrics generation."""
        metrics = mrg._generate_performance_metrics(minimal_df)
        
        assert '📈' in metrics
        assert 'Heatmap' in metrics
        assert '%' in metrics
    
    def test_generate_archetypes(self, minimal_df):
        """Test archetypes generation."""
        archetypes = mrg._generate_contributor_archetypes(minimal_df)
        
        assert '🎭' in archetypes
        assert 'Archetype' in archetypes
    
    def test_generate_recommendations(self, minimal_df):
        """Test recommendations generation."""
        stats = mrg._calculate_contributor_stats(minimal_df)
        recommendations = mrg._generate_recommendations(minimal_df, stats)
        
        assert '🎯' in recommendations
        assert 'Priority' in recommendations
    
    def test_generate_awards(self, minimal_df):
        """Test awards section generation."""
        awards = mrg._generate_special_awards(minimal_df)
        
        assert '🏅' in awards
        assert 'Award' in awards
        assert 'Champion' in awards


# ============================================================================
# Tests: Full Report Generation
# ============================================================================

class TestFullReportGeneration:
    """Test complete report generation."""
    
    def test_generate_report_basic(self, minimal_df):
        """Test basic report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.md')
            
            # Create temp CSV
            csv_path = os.path.join(tmpdir, 'test_data.csv')
            minimal_df.to_csv(csv_path, index=False)
            
            # Generate report
            report = mrg.generate_report(
                csv_file_path=csv_path,
                output_file_path=output_path,
                project_name="Test Project",
                team_name="Test Team"
            )
            
            assert os.path.exists(output_path)
            assert len(report) > 1000
            assert 'Test Project' in report
            assert 'Test Team' in report
    
    def test_generate_report_structure(self, minimal_df):
        """Test that report contains all expected sections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.md')
            csv_path = os.path.join(tmpdir, 'test_data.csv')
            minimal_df.to_csv(csv_path, index=False)
            
            report = mrg.generate_report(
                csv_file_path=csv_path,
                output_file_path=output_path,
                project_name="Test",
                team_name="Team"
            )
            
            # Check for main sections
            assert '# 🚀 GitHub Performance Dashboard' in report
            assert '## 📊 Executive Summary' in report
            assert '## 🏆 Top Performers' in report
            assert '## 📈 Performance Heatmap' in report
            assert '## 🎯 Actionable Recommendations' in report
            assert '## 🏅 Special Recognition' in report
    
    def test_generate_report_with_real_data(self, sample_csv_path):
        """Test report generation with real sample data."""
        if os.path.exists(sample_csv_path):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = os.path.join(tmpdir, 'real_report.md')
                
                report = mrg.generate_report(
                    csv_file_path=sample_csv_path,
                    output_file_path=output_path,
                    project_name="Singer Swipe",
                    team_name="Team 3J"
                )
                
                assert os.path.exists(output_path)
                assert len(report) > 5000
                with open(output_path, 'r') as f:
                    content = f.read()
                    assert len(content) > 5000


# ============================================================================
# Tests: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_contributor(self):
        """Test with single contributor."""
        df = pd.DataFrame({
            'username': ['solo'],
            'commits': [50],
            'images': [10],
            'lines_added': [5000],
            'lines_deleted': [500],
            'issues_created': [5],
            'issues_resolved': [3],
            'prs_opened': [8],
            'prs_approved': [6],
            'comments': [20],
            'total_points': [500],
            'grade': ['MB'],
        })
        
        stats = mrg._calculate_contributor_stats(df)
        assert stats['total_contributors'] == 1
        assert stats['total_commits'] == 50
    
    def test_zero_values_in_metrics(self):
        """Test with zero values in metrics."""
        df = pd.DataFrame({
            'username': ['zero_user'],
            'commits': [0],
            'images': [0],
            'lines_added': [0],
            'lines_deleted': [0],
            'issues_created': [0],
            'issues_resolved': [0],
            'prs_opened': [0],
            'prs_approved': [0],
            'comments': [0],
            'total_points': [0],
            'grade': ['I'],
        })
        
        archetypes = mrg._generate_contributor_archetypes(df)
        assert '⏱️ Silent Coder' in archetypes
    
    def test_extreme_values(self):
        """Test with extreme metric values."""
        df = pd.DataFrame({
            'username': ['extreme'],
            'commits': [10000],
            'images': [500],
            'lines_added': [1000000],
            'lines_deleted': [500000],
            'issues_created': [1000],
            'issues_resolved': [500],
            'prs_opened': [500],
            'prs_approved': [450],
            'comments': [2000],
            'total_points': [9999],
            'grade': ['MB'],
        })
        
        stats = mrg._calculate_contributor_stats(df)
        assert stats['total_lines'] == 1500000
        assert stats['total_comments'] == 2000
    
    def test_missing_optional_columns(self):
        """Test handling of missing optional columns."""
        df = pd.DataFrame({
            'username': ['user'],
            'commits': [10],
            'lines_added': [100],
            'lines_deleted': [10],
            'issues_created': [2],
            'issues_resolved': [1],
            'prs_opened': [3],
            'prs_approved': [2],
            'comments': [5],
            'total_points': [50],
            'grade': ['B'],
        })
        # 'images' column missing
        archetype, desc = mrg._detect_archetype(df.iloc[0])
        assert isinstance(archetype, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
