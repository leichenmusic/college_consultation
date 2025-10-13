"""
Product Manager Agent for 蕾拉酱的AI留学顾问
Provides strategic insights, feature analysis, user research, and product management capabilities
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import os
from database import DatabaseManager

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

class FeatureStatus(Enum):
    IDEA = "idea"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    LAUNCHED = "launched"
    DEPRECATED = "deprecated"

@dataclass
class Feature:
    id: str
    name: str
    description: str
    priority: Priority
    status: FeatureStatus
    estimated_effort: int  # story points
    business_value: int    # 1-10 scale
    target_users: List[str]
    success_metrics: List[str]
    dependencies: List[str]
    created_date: str
    target_launch: Optional[str] = None
    owner: str = "PM Agent"

@dataclass
class UserInsight:
    id: str
    insight: str
    source: str  # "chat_analysis", "form_data", "user_behavior"
    confidence: float  # 0-1
    impact: Priority
    actionable_items: List[str]
    created_date: str

@dataclass
class ProductMetric:
    name: str
    value: float
    unit: str
    trend: str  # "up", "down", "stable"
    target: Optional[float] = None
    date: str = None

class ProductManagerAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.features: List[Feature] = []
        self.insights: List[UserInsight] = []
        self.metrics: List[ProductMetric] = []
        self.load_product_data()
    
    def load_product_data(self):
        """Load existing product data from database or files"""
        try:
            # Try to load from database first
            # If not available, initialize with default features
            self.initialize_default_features()
        except Exception as e:
            print(f"PM Agent: Could not load data: {e}")
            self.initialize_default_features()
    
    def initialize_default_features(self):
        """Initialize with current features and planned improvements"""
        default_features = [
            Feature(
                id="chat_history_persistence",
                name="Chat History Persistence", 
                description="Store and retrieve chat conversations for logged-in users",
                priority=Priority.HIGH,
                status=FeatureStatus.LAUNCHED,
                estimated_effort=8,
                business_value=9,
                target_users=["returning_users", "registered_users"],
                success_metrics=["user_retention_rate", "session_length"],
                dependencies=[],
                created_date="2024-09-20"
            ),
            Feature(
                id="smart_form_prefill",
                name="Smart Form Pre-filling",
                description="Auto-populate forms based on user login info and chat history",
                priority=Priority.HIGH,
                status=FeatureStatus.LAUNCHED,
                estimated_effort=5,
                business_value=8,
                target_users=["logged_in_users"],
                success_metrics=["form_completion_rate", "user_satisfaction"],
                dependencies=["user_authentication"],
                created_date="2024-09-22"
            ),
            Feature(
                id="multilingual_support",
                name="Multilingual Support",
                description="Support English and Chinese languages with smart detection",
                priority=Priority.MEDIUM,
                status=FeatureStatus.IDEA,
                estimated_effort=13,
                business_value=7,
                target_users=["international_students", "english_speakers"],
                success_metrics=["user_engagement", "market_expansion"],
                dependencies=[],
                created_date="2024-09-28"
            ),
            Feature(
                id="school_recommendation_engine",
                name="AI School Recommendation Engine",
                description="Intelligent school matching based on user profile and preferences",
                priority=Priority.CRITICAL,
                status=FeatureStatus.PLANNED,
                estimated_effort=21,
                business_value=10,
                target_users=["all_users"],
                success_metrics=["recommendation_accuracy", "user_satisfaction", "conversion_rate"],
                dependencies=["user_profile_completion"],
                created_date="2024-09-28"
            ),
            Feature(
                id="video_consultation_booking",
                name="Video Consultation Booking",
                description="Allow users to book 1-on-1 video consultations with advisors",
                priority=Priority.HIGH,
                status=FeatureStatus.IDEA,
                estimated_effort=34,
                business_value=9,
                target_users=["serious_applicants"],
                success_metrics=["booking_rate", "consultation_completion", "revenue"],
                dependencies=["payment_integration", "calendar_system"],
                created_date="2024-09-28"
            ),
            Feature(
                id="application_timeline_tracker",
                name="Application Timeline Tracker",
                description="Personalized timeline with deadlines and milestones",
                priority=Priority.MEDIUM,
                status=FeatureStatus.IDEA,
                estimated_effort=13,
                business_value=7,
                target_users=["active_applicants"],
                success_metrics=["timeline_completion_rate", "deadline_adherence"],
                dependencies=["user_profile_completion"],
                created_date="2024-09-28"
            ),
            Feature(
                id="peer_community_forum",
                name="Peer Community Forum",
                description="Connect students with similar goals and backgrounds",
                priority=Priority.LOW,
                status=FeatureStatus.IDEA,
                estimated_effort=55,
                business_value=6,
                target_users=["community_seekers"],
                success_metrics=["community_engagement", "peer_connections"],
                dependencies=["user_verification", "moderation_system"],
                created_date="2024-09-28"
            ),
            Feature(
                id="ai_portfolio_evaluation",
                name="AI作品集智能评估",
                description="基于AI的音乐作品集分析和改进建议系统",
                priority=Priority.HIGH,
                status=FeatureStatus.IDEA,
                estimated_effort=28,
                business_value=9,
                target_users=["music_students", "applicants"],
                success_metrics=["evaluation_accuracy", "user_satisfaction", "improvement_tracking"],
                dependencies=["audio_processing", "ml_models"],
                created_date="2024-10-10"
            ),
            Feature(
                id="mobile_app_development",
                name="移动端原生应用",
                description="iOS和Android原生应用，提供完整的移动端体验",
                priority=Priority.HIGH,
                status=FeatureStatus.IDEA,
                estimated_effort=42,
                business_value=8,
                target_users=["mobile_users", "all_users"],
                success_metrics=["app_downloads", "mobile_engagement", "user_retention"],
                dependencies=["api_optimization", "push_notifications"],
                created_date="2024-10-10"
            ),
            Feature(
                id="data_analytics_dashboard",
                name="数据分析仪表板",
                description="深度用户行为分析和商业智能平台",
                priority=Priority.MEDIUM,
                status=FeatureStatus.IDEA,
                estimated_effort=18,
                business_value=7,
                target_users=["administrators", "business_analysts"],
                success_metrics=["data_accuracy", "insight_quality", "decision_impact"],
                dependencies=["data_pipeline", "visualization_tools"],
                created_date="2024-10-10"
            )
        ]
        self.features = default_features
    
    def analyze_user_behavior(self, session_data: Dict) -> List[UserInsight]:
        """Analyze user behavior patterns and generate insights"""
        insights = []
        
        # Analyze form completion patterns
        if session_data.get('user_profile', {}).get('form_completed'):
            profile = session_data['user_profile']
            incomplete_fields = [k for k, v in profile.items() if not v or v == []]
            
            if len(incomplete_fields) > 3:
                insights.append(UserInsight(
                    id=f"incomplete_profile_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    insight="User has many incomplete profile fields, suggesting form may be too long or complex",
                    source="form_data",
                    confidence=0.8,
                    impact=Priority.MEDIUM,
                    actionable_items=[
                        "Consider progressive profiling",
                        "Make more fields optional",
                        "Add form progress indicator"
                    ],
                    created_date=datetime.datetime.now().isoformat()
                ))
        
        # Analyze chat patterns
        chat_history = session_data.get('chat_history', [])
        if len(chat_history) > 5:
            user_messages = [msg for msg in chat_history if msg.get('sender') == 'user']
            avg_message_length = sum(len(msg.get('message', '')) for msg in user_messages) / len(user_messages)
            
            if avg_message_length < 20:
                insights.append(UserInsight(
                    id=f"short_messages_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    insight="Users tend to send very short messages, may prefer structured choices",
                    source="chat_analysis",
                    confidence=0.7,
                    impact=Priority.MEDIUM,
                    actionable_items=[
                        "Increase use of choice buttons",
                        "Provide more guided conversation flows",
                        "Add quick reply options"
                    ],
                    created_date=datetime.datetime.now().isoformat()
                ))
        
        return insights
    
    def calculate_metrics(self) -> List[ProductMetric]:
        """Calculate key product metrics"""
        metrics = []
        
        try:
            # User engagement metrics
            total_sessions = len(self.db.get_all_sessions()) if hasattr(self.db, 'get_all_sessions') else 0
            
            metrics.extend([
                ProductMetric(
                    name="Total Sessions",
                    value=total_sessions,
                    unit="count",
                    trend="up",
                    date=datetime.datetime.now().isoformat()
                ),
                ProductMetric(
                    name="Feature Completion Rate",
                    value=len([f for f in self.features if f.status == FeatureStatus.LAUNCHED]) / len(self.features) * 100,
                    unit="percentage",
                    trend="up",
                    target=80.0,
                    date=datetime.datetime.now().isoformat()
                ),
                ProductMetric(
                    name="High Priority Features",
                    value=len([f for f in self.features if f.priority in [Priority.CRITICAL, Priority.HIGH]]),
                    unit="count",
                    trend="stable",
                    date=datetime.datetime.now().isoformat()
                )
            ])
        except Exception as e:
            print(f"PM Agent: Error calculating metrics: {e}")
        
        return metrics
    
    def get_product_roadmap(self, timeframe: str = "next_quarter") -> Dict[str, List[Feature]]:
        """Generate product roadmap organized by status and priority"""
        roadmap = {
            "now": [],
            "next": [],
            "later": [],
            "launched": []
        }
        
        # Sort features by priority and status
        sorted_features = sorted(self.features, key=lambda f: (f.priority.value, f.estimated_effort))
        
        for feature in sorted_features:
            if feature.status == FeatureStatus.LAUNCHED:
                roadmap["launched"].append(feature)
            elif feature.status in [FeatureStatus.IN_PROGRESS, FeatureStatus.TESTING]:
                roadmap["now"].append(feature)
            elif feature.priority in [Priority.CRITICAL, Priority.HIGH]:
                roadmap["next"].append(feature)
            else:
                roadmap["later"].append(feature)
        
        return roadmap
    
    def generate_strategic_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive strategic analysis"""
        roadmap = self.get_product_roadmap()
        metrics = self.calculate_metrics()
        
        # Calculate feature effort distribution
        total_effort = sum(f.estimated_effort for f in self.features if f.status != FeatureStatus.LAUNCHED)
        effort_by_priority = {}
        for priority in Priority:
            effort = sum(f.estimated_effort for f in self.features 
                        if f.priority == priority and f.status != FeatureStatus.LAUNCHED)
            effort_by_priority[priority.value] = effort
        
        # Identify bottlenecks
        bottlenecks = []
        high_effort_features = [f for f in self.features if f.estimated_effort > 20]
        if high_effort_features:
            bottlenecks.append("Large features may block roadmap progress")
        
        dependency_count = {}
        for feature in self.features:
            for dep in feature.dependencies:
                dependency_count[dep] = dependency_count.get(dep, 0) + 1
        
        critical_dependencies = [dep for dep, count in dependency_count.items() if count > 2]
        if critical_dependencies:
            bottlenecks.extend([f"Critical dependency: {dep}" for dep in critical_dependencies])
        
        return {
            "roadmap_summary": {
                "in_progress": len(roadmap["now"]),
                "planned_next": len(roadmap["next"]),
                "future": len(roadmap["later"]),
                "launched": len(roadmap["launched"])
            },
            "effort_analysis": {
                "total_remaining_effort": total_effort,
                "effort_by_priority": effort_by_priority,
                "avg_effort_per_feature": total_effort / len(self.features) if self.features else 0
            },
            "risk_analysis": {
                "bottlenecks": bottlenecks,
                "high_effort_features": len(high_effort_features),
                "critical_dependencies": critical_dependencies
            },
            "metrics": [asdict(m) for m in metrics],
            "recommendations": self.generate_recommendations()
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate strategic recommendations based on current state"""
        recommendations = []
        
        # Analyze feature distribution
        critical_features = [f for f in self.features if f.priority == Priority.CRITICAL]
        launched_critical = [f for f in critical_features if f.status == FeatureStatus.LAUNCHED]
        
        if len(launched_critical) < len(critical_features):
            recommendations.append("🚨 Focus on completing critical features first for maximum impact")
        
        # Check for quick wins
        quick_wins = [f for f in self.features 
                     if f.estimated_effort <= 8 and f.business_value >= 7 and f.status == FeatureStatus.IDEA]
        if quick_wins:
            recommendations.append(f"⚡ Consider prioritizing {len(quick_wins)} quick win features for fast value delivery")
        
        # Resource allocation
        high_effort_count = len([f for f in self.features if f.estimated_effort > 20])
        if high_effort_count > 2:
            recommendations.append("📊 Consider breaking down large features into smaller, deliverable chunks")
        
        # User experience
        ux_features = [f for f in self.features if "user" in f.description.lower() or "experience" in f.description.lower()]
        if len(ux_features) < len(self.features) * 0.3:
            recommendations.append("👥 Consider adding more user experience focused features")
        
        # Technical debt
        launched_features = [f for f in self.features if f.status == FeatureStatus.LAUNCHED]
        if len(launched_features) > 5:
            recommendations.append("🔧 Plan for technical debt reduction and system optimization")
        
        return recommendations
    
    def add_feature(self, feature_data: Dict) -> Feature:
        """Add a new feature to the roadmap"""
        feature = Feature(
            id=feature_data.get('id', f"feature_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=feature_data['name'],
            description=feature_data['description'],
            priority=Priority(feature_data.get('priority', 'medium')),
            status=FeatureStatus(feature_data.get('status', 'idea')),
            estimated_effort=feature_data.get('estimated_effort', 5),
            business_value=feature_data.get('business_value', 5),
            target_users=feature_data.get('target_users', []),
            success_metrics=feature_data.get('success_metrics', []),
            dependencies=feature_data.get('dependencies', []),
            created_date=datetime.datetime.now().isoformat(),
            target_launch=feature_data.get('target_launch'),
            owner=feature_data.get('owner', 'PM Agent')
        )
        
        self.features.append(feature)
        return feature
    
    def update_feature_status(self, feature_id: str, new_status: FeatureStatus) -> bool:
        """Update the status of a feature"""
        for feature in self.features:
            if feature.id == feature_id:
                feature.status = new_status
                return True
        return False
    
    def get_feature_by_id(self, feature_id: str) -> Optional[Feature]:
        """Get a specific feature by ID"""
        for feature in self.features:
            if feature.id == feature_id:
                return feature
        return None
    
    def export_roadmap(self, format: str = "json") -> str:
        """Export roadmap in specified format"""
        roadmap = self.get_product_roadmap()
        
        if format == "json":
            # Convert dataclasses to dicts for JSON serialization
            json_roadmap = {}
            for status, features in roadmap.items():
                json_roadmap[status] = [asdict(f) for f in features]
            
            return json.dumps(json_roadmap, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            md_content = "# 🎵 蕾拉酱的AI留学顾问 - Product Roadmap\n\n"
            
            for status, features in roadmap.items():
                if not features:
                    continue
                    
                status_titles = {
                    "now": "🚀 In Progress",
                    "next": "📋 Planned Next",
                    "later": "🔮 Future",
                    "launched": "✅ Launched"
                }
                
                md_content += f"## {status_titles.get(status, status.title())}\n\n"
                
                for feature in features:
                    priority_emoji = {
                        "critical": "🔥",
                        "high": "⚡",
                        "medium": "📊",
                        "low": "💡"
                    }
                    
                    md_content += f"### {priority_emoji.get(feature.priority.value, '📋')} {feature.name}\n"
                    md_content += f"**Description:** {feature.description}\n\n"
                    md_content += f"**Priority:** {feature.priority.value.title()}\n\n"
                    md_content += f"**Effort:** {feature.estimated_effort} story points\n\n"
                    md_content += f"**Business Value:** {feature.business_value}/10\n\n"
                    
                    if feature.target_users:
                        md_content += f"**Target Users:** {', '.join(feature.target_users)}\n\n"
                    
                    if feature.success_metrics:
                        md_content += f"**Success Metrics:** {', '.join(feature.success_metrics)}\n\n"
                    
                    md_content += "---\n\n"
            
            return md_content
        
        return str(roadmap)

# Global PM Agent instance
pm_agent = None

def get_pm_agent(db_manager: DatabaseManager = None) -> ProductManagerAgent:
    """Get or create the global PM agent instance"""
    global pm_agent
    if pm_agent is None and db_manager:
        pm_agent = ProductManagerAgent(db_manager)
    return pm_agent

def analyze_session_for_insights(session_data: Dict, db_manager: DatabaseManager) -> Dict[str, Any]:
    """Analyze a user session and return PM insights"""
    agent = get_pm_agent(db_manager)
    if not agent:
        return {"error": "PM Agent not initialized"}
    
    insights = agent.analyze_user_behavior(session_data)
    return {
        "insights": [asdict(insight) for insight in insights],
        "recommendations": agent.generate_recommendations(),
        "timestamp": datetime.datetime.now().isoformat()
    }
