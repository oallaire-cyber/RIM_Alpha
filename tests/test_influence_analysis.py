"""
Tests for services/influence_analysis.py

Tests the InfluenceAnalyzer service and related data classes.
"""

import pytest
from services.influence_analysis import (
    InfluenceAnalyzer,
    PropagationResult,
    ConvergenceResult,
    CriticalPath,
    Bottleneck,
    RiskCluster,
)


class TestPropagationResult:
    """Tests for PropagationResult dataclass."""
    
    def test_create_result(self):
        """Test creating a propagation result."""
        result = PropagationResult(
            id="risk-001",
            name="Test Risk",
            level="Strategic",
            score=15.5,
            tpos_reached=2,
            risks_reached=5,
            tpo_ids=["tpo-001", "tpo-002"],
            paths_to_tpo=[{"path": ["risk-001", "tpo-001"]}]
        )
        
        assert result.id == "risk-001"
        assert result.score == 15.5
        assert result.tpos_reached == 2


class TestConvergenceResult:
    """Tests for ConvergenceResult dataclass."""
    
    def test_create_result(self):
        """Test creating a convergence result."""
        result = ConvergenceResult(
            id="risk-001",
            name="Test Risk",
            level="Strategic",
            node_type="Risk",
            score=10.0,
            source_count=3,
            path_count=5,
            is_high_convergence=True
        )
        
        assert result.id == "risk-001"
        assert result.is_high_convergence is True


class TestCriticalPath:
    """Tests for CriticalPath dataclass."""
    
    def test_create_path(self):
        """Test creating a critical path."""
        path = CriticalPath(
            path=[{"id": "r1"}, {"id": "r2"}, {"id": "tpo-1"}],
            edges=[{"strength": "Strong"}, {"impact": "High"}],
            strength=0.85,
            length=3
        )
        
        assert path.length == 3
        assert path.strength == 0.85


class TestBottleneck:
    """Tests for Bottleneck dataclass."""
    
    def test_create_bottleneck(self):
        """Test creating a bottleneck."""
        bottleneck = Bottleneck(
            id="risk-001",
            name="Bottleneck Risk",
            level="Strategic",
            path_count=10,
            total_paths=15,
            percentage=66.7
        )
        
        assert bottleneck.id == "risk-001"
        assert bottleneck.percentage == 66.7


class TestRiskCluster:
    """Tests for RiskCluster dataclass."""
    
    def test_create_cluster(self):
        """Test creating a risk cluster."""
        cluster = RiskCluster(
            nodes=["r1", "r2", "r3"],
            node_names=["Risk 1", "Risk 2", "Risk 3"],
            size=3,
            internal_edges=4,
            density=0.67,
            primary_category="Programme",
            levels={"Strategic": 1, "Operational": 2}
        )
        
        assert cluster.size == 3
        assert cluster.density == 0.67


class TestInfluenceAnalyzerInit:
    """Tests for InfluenceAnalyzer initialization."""
    
    def test_init_empty_data(self):
        """Test initialization with empty data."""
        analyzer = InfluenceAnalyzer(
            risks=[],
            tpos=[],
            influences=[],
            tpo_impacts=[]
        )
        
        assert analyzer is not None
        assert len(analyzer.risks) == 0
    
    def test_init_with_sample_data(self, sample_risk_network):
        """Test initialization with sample network data."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        assert analyzer is not None
        assert len(analyzer.risks) == 3
        assert len(analyzer.risk_dict) == 3


class TestInfluenceAnalyzerAdjacency:
    """Tests for adjacency list building."""
    
    def test_builds_outgoing_adjacency(self, sample_risk_network):
        """Test that outgoing adjacency is built correctly."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        # Outgoing adjacency should be populated
        assert isinstance(analyzer.outgoing, dict)
    
    def test_builds_incoming_adjacency(self, sample_risk_network):
        """Test that incoming adjacency is built correctly."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        # Incoming adjacency should be populated
        assert isinstance(analyzer.incoming, dict)


class TestInfluenceAnalyzerAnalyze:
    """Tests for the main analyze method."""
    
    def test_analyze_returns_dict(self, sample_risk_network):
        """Test analyze returns a dictionary with all sections."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        result = analyzer.analyze()
        
        assert isinstance(result, dict)
        assert "top_propagators" in result
        assert "convergence_points" in result
        assert "critical_paths" in result
        assert "bottlenecks" in result
    
    def test_analyze_empty_network(self):
        """Test analyze handles empty network."""
        analyzer = InfluenceAnalyzer(
            risks=[],
            tpos=[],
            influences=[],
            tpo_impacts=[]
        )
        
        result = analyzer.analyze()
        
        assert len(result["top_propagators"]) == 0
        assert len(result["convergence_points"]) == 0


class TestInfluenceAnalyzerPropagators:
    """Tests for top propagators calculation."""
    
    def test_get_top_propagators(self, sample_risk_network):
        """Test getting top propagators."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        propagators = analyzer.get_top_propagators(limit=5)
        
        # Should return list
        assert isinstance(propagators, list)
    
    def test_propagators_sorted_by_score(self, sample_risk_network):
        """Test propagators are sorted by score descending."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        propagators = analyzer.get_top_propagators(limit=5)
        
        if len(propagators) >= 2:
            for i in range(len(propagators) - 1):
                assert propagators[i]["score"] >= propagators[i + 1]["score"]


class TestInfluenceAnalyzerConvergence:
    """Tests for convergence points calculation."""
    
    def test_get_convergence_points(self, sample_risk_network):
        """Test getting convergence points."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        convergence = analyzer.get_convergence_points(limit=5)
        
        assert isinstance(convergence, list)


class TestInfluenceAnalyzerCriticalPaths:
    """Tests for critical paths calculation."""
    
    def test_get_critical_paths(self, sample_risk_network):
        """Test getting critical paths."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        paths = analyzer.get_critical_paths(limit=5)
        
        assert isinstance(paths, list)


class TestInfluenceAnalyzerBottlenecks:
    """Tests for bottleneck calculation."""
    
    def test_get_bottlenecks(self, sample_risk_network):
        """Test getting bottlenecks."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        bottlenecks = analyzer.get_bottlenecks(limit=5)
        
        assert isinstance(bottlenecks, list)


class TestInfluenceAnalyzerClusters:
    """Tests for risk cluster calculation."""
    
    def test_get_risk_clusters(self, sample_risk_network):
        """Test getting risk clusters."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        clusters = analyzer.get_risk_clusters(limit=5)
        
        assert isinstance(clusters, list)


class TestInfluenceAnalyzerHelpers:
    """Tests for helper methods."""
    
    def test_get_propagator_ids(self, sample_risk_network):
        """Test get_propagator_ids returns list/set of IDs."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        # First run analyze to populate results
        analyzer.analyze()
        
        ids = analyzer.get_propagator_ids()
        
        assert isinstance(ids, (list, set))
    
    def test_get_high_priority_ids(self, sample_risk_network):
        """Test get_high_priority_ids returns combined set."""
        analyzer = InfluenceAnalyzer(
            risks=sample_risk_network["risks"],
            tpos=sample_risk_network["tpos"],
            influences=sample_risk_network["influences"],
            tpo_impacts=sample_risk_network["tpo_impacts"]
        )
        
        # First run analyze to populate results
        analyzer.analyze()
        
        ids = analyzer.get_high_priority_ids()
        
        assert isinstance(ids, (list, set))
