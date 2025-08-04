# ml_predictive_models.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, mean_squared_error
import joblib
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MLPrediction:
    """Data class for ML prediction results"""
    prediction: float
    confidence: float
    risk_level: str
    factors: List[str]
    recommendations: List[str]
    model_version: str

@dataclass
class InterventionRecommendation:
    """Data class for personalized intervention recommendations"""
    intervention_type: str
    priority: int
    effectiveness_score: float
    time_to_effect: str
    effort_level: str
    evidence_level: str

class PsychologicalMLEngine:
    """Advanced ML engine for psychological assessment predictions"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.is_trained = False
        self.setup_synthetic_training_data()
        self.train_models()
    
    def setup_synthetic_training_data(self):
        """Generate realistic synthetic training data for psychological assessments"""
        np.random.seed(42)
        n_samples = 5000
        
        # Generate synthetic features
        data = {
            # Demographic features
            'age': np.random.normal(35, 10, n_samples).clip(18, 65),
            'years_experience': np.random.normal(8, 5, n_samples).clip(0, 40),
            'education_level': np.random.choice([1, 2, 3, 4], n_samples, p=[0.1, 0.3, 0.4, 0.2]),
            'management_role': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            
            # Work environment features
            'work_hours_per_week': np.random.normal(45, 8, n_samples).clip(20, 80),
            'commute_time': np.random.normal(30, 15, n_samples).clip(0, 120),
            'team_size': np.random.poisson(8, n_samples).clip(1, 50),
            'workplace_flexibility': np.random.uniform(0, 10, n_samples),
            'job_security': np.random.uniform(0, 10, n_samples),
            
            # Lifestyle features
            'sleep_hours': np.random.normal(7, 1.5, n_samples).clip(4, 12),
            'exercise_frequency': np.random.poisson(3, n_samples).clip(0, 7),
            'social_support': np.random.uniform(0, 10, n_samples),
            'work_life_balance': np.random.uniform(0, 10, n_samples),
            
            # Previous assessment scores (simulated)
            'prev_pss10': np.random.normal(16, 6, n_samples).clip(0, 40),
            'prev_anxiety': np.random.normal(8, 5, n_samples).clip(0, 21),
            'prev_depression': np.random.normal(6, 4, n_samples).clip(0, 21),
        }
        
        # Create complex relationships for target variables
        base_stress = (
            0.3 * data['work_hours_per_week'] / 40 +
            0.2 * (10 - data['workplace_flexibility']) / 10 +
            0.2 * (10 - data['job_security']) / 10 +
            0.1 * data['commute_time'] / 60 +
            0.1 * (8 - data['sleep_hours']) / 4 +
            0.1 * (10 - data['social_support']) / 10
        ) * 40
        
        # Add noise and individual variation
        data['current_pss10'] = (base_stress + np.random.normal(0, 3, n_samples)).clip(0, 40)
        
        # Risk categories based on multiple factors
        risk_scores = (
            (data['current_pss10'] > 20).astype(int) * 2 +
            (data['prev_anxiety'] > 10).astype(int) +
            (data['prev_depression'] > 9).astype(int) +
            (data['work_hours_per_week'] > 50).astype(int) +
            (data['sleep_hours'] < 6).astype(int)
        )
        
        data['risk_level'] = np.where(risk_scores >= 4, 2,  # High risk
                                    np.where(risk_scores >= 2, 1, 0))  # Medium risk, Low risk
        
        # Intervention effectiveness (synthetic)
        data['intervention_effectiveness'] = np.random.uniform(0.2, 0.9, n_samples)
        
        # Time to improvement (weeks)
        data['time_to_improvement'] = np.random.exponential(8, n_samples).clip(2, 52)
        
        self.training_data = pd.DataFrame(data)
        print(f"✅ Generated {n_samples} synthetic training samples")
    
    def prepare_features(self, data: Dict) -> np.array:
        """Prepare features for ML models"""
        feature_vector = []
        
        # Map input data to feature vector
        feature_mapping = {
            'age': data.get('age', 35),
            'years_experience': data.get('years_experience', 5),
            'education_level': data.get('education_level', 2),
            'management_role': data.get('management_role', 0),
            'work_hours_per_week': data.get('work_hours_per_week', 40),
            'commute_time': data.get('commute_time', 30),
            'team_size': data.get('team_size', 8),
            'workplace_flexibility': data.get('workplace_flexibility', 5),
            'job_security': data.get('job_security', 5),
            'sleep_hours': data.get('sleep_hours', 7),
            'exercise_frequency': data.get('exercise_frequency', 2),
            'social_support': data.get('social_support', 5),
            'work_life_balance': data.get('work_life_balance', 5),
            'prev_pss10': data.get('prev_pss10', 15),
            'prev_anxiety': data.get('prev_anxiety', 7),
            'prev_depression': data.get('prev_depression', 5),
        }
        
        return np.array(list(feature_mapping.values())).reshape(1, -1)
    
    def train_models(self):
        """Train ML models for different prediction tasks"""
        print("🤖 Training ML models...")
        
        # Prepare features and targets
        feature_cols = ['age', 'years_experience', 'education_level', 'management_role',
                       'work_hours_per_week', 'commute_time', 'team_size', 
                       'workplace_flexibility', 'job_security', 'sleep_hours',
                       'exercise_frequency', 'social_support', 'work_life_balance',
                       'prev_pss10', 'prev_anxiety', 'prev_depression']
        
        X = self.training_data[feature_cols]
        
        # Scale features
        self.scalers['main'] = StandardScaler()
        X_scaled = self.scalers['main'].fit_transform(X)
        
        # 1. Risk Assessment Model
        y_risk = self.training_data['risk_level']
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_risk, test_size=0.2, random_state=42)
        
        self.models['risk_classifier'] = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
        )
        self.models['risk_classifier'].fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.models['risk_classifier'].predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Risk Assessment Model Accuracy: {accuracy:.3f}")
        
        # 2. Stress Score Prediction Model
        y_stress = self.training_data['current_pss10']
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_stress, test_size=0.2, random_state=42)
        
        self.models['stress_predictor'] = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.models['stress_predictor'].fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.models['stress_predictor'].predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Stress Prediction Model MSE: {mse:.3f}")
        
        # 3. Intervention Effectiveness Model
        y_effectiveness = self.training_data['intervention_effectiveness']
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_effectiveness, test_size=0.2, random_state=42)
        
        self.models['intervention_effectiveness'] = RandomForestRegressor(
            n_estimators=100, max_depth=8, random_state=42
        )
        self.models['intervention_effectiveness'].fit(X_train, y_train)
        
        # 4. Time to Improvement Model
        y_time = self.training_data['time_to_improvement']
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_time, test_size=0.2, random_state=42)
        
        self.models['time_predictor'] = RandomForestRegressor(
            n_estimators=100, max_depth=8, random_state=42
        )
        self.models['time_predictor'].fit(X_train, y_train)
        
        # Feature importance
        self.feature_importance['risk'] = dict(zip(feature_cols, 
            self.models['risk_classifier'].feature_importances_))
        self.feature_importance['stress'] = dict(zip(feature_cols,
            self.models['stress_predictor'].feature_importances_))
        
        self.is_trained = True
        print("✅ All ML models trained successfully")
    
    def predict_risk_assessment(self, user_data: Dict) -> MLPrediction:
        """Predict comprehensive risk assessment"""
        if not self.is_trained:
            raise ValueError("Models not trained yet")
        
        features = self.prepare_features(user_data)
        features_scaled = self.scalers['main'].transform(features)
        
        # Risk prediction
        risk_proba = self.models['risk_classifier'].predict_proba(features_scaled)[0]
        risk_class = self.models['risk_classifier'].predict(features_scaled)[0]
        confidence = max(risk_proba)
        
        risk_levels = ['Low', 'Moderate', 'High']
        risk_level = risk_levels[risk_class]
        
        # Identify key risk factors
        feature_names = ['age', 'years_experience', 'education_level', 'management_role',
                        'work_hours_per_week', 'commute_time', 'team_size', 
                        'workplace_flexibility', 'job_security', 'sleep_hours',
                        'exercise_frequency', 'social_support', 'work_life_balance',
                        'prev_pss10', 'prev_anxiety', 'prev_depression']
        
        importance_scores = self.feature_importance['risk']
        top_factors = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        factors = [factor[0].replace('_', ' ').title() for factor in top_factors]
        
        # Generate recommendations based on prediction
        recommendations = self.generate_ml_recommendations(user_data, risk_level)
        
        return MLPrediction(
            prediction=float(risk_class),
            confidence=float(confidence),
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            model_version="1.0"
        )
    
    def predict_stress_trajectory(self, user_data: Dict, timeline_weeks: int = 12) -> Dict:
        """Predict stress level trajectory over time"""
        features = self.prepare_features(user_data)
        features_scaled = self.scalers['main'].transform(features)
        
        current_stress = self.models['stress_predictor'].predict(features_scaled)[0]
        
        # Simulate trajectory with interventions
        trajectory = {'weeks': [], 'predicted_stress': [], 'with_intervention': []}
        
        for week in range(timeline_weeks + 1):
            # Natural progression (slight improvement over time)
            natural_stress = current_stress * (0.98 ** week)
            
            # With intervention (faster improvement)
            intervention_stress = current_stress * (0.94 ** week)
            
            trajectory['weeks'].append(week)
            trajectory['predicted_stress'].append(max(0, natural_stress))
            trajectory['with_intervention'].append(max(0, intervention_stress))
        
        return trajectory
    
    def generate_ml_recommendations(self, user_data: Dict, risk_level: str) -> List[str]:
        """Generate ML-powered personalized recommendations"""
        recommendations = []
        
        # Analyze key risk factors
        work_hours = user_data.get('work_hours_per_week', 40)
        sleep_hours = user_data.get('sleep_hours', 7)
        exercise_freq = user_data.get('exercise_frequency', 2)
        workplace_flex = user_data.get('workplace_flexibility', 5)
        social_support = user_data.get('social_support', 5)
        
        # Work-related recommendations
        if work_hours > 50:
            recommendations.append("⏰ Prioritize workload management - consider delegation or time-blocking strategies")
        
        if workplace_flex < 4:
            recommendations.append("🏢 Discuss flexible work arrangements with your supervisor")
        
        # Lifestyle recommendations
        if sleep_hours < 6.5:
            recommendations.append("😴 Implement sleep hygiene protocol - aim for 7-8 hours nightly")
        
        if exercise_freq < 2:
            recommendations.append("🏃‍♂️ Start with 20-minute walks 3x per week, gradually increase intensity")
        
        if social_support < 4:
            recommendations.append("👥 Strengthen social connections - schedule regular check-ins with colleagues/friends")
        
        # Risk-specific recommendations
        if risk_level == 'High':
            recommendations.extend([
                "🚨 Consider professional counseling within 2 weeks",
                "📞 Contact Employee Assistance Program if available",
                "🏥 Schedule medical check-up to rule out underlying conditions"
            ])
        elif risk_level == 'Moderate':
            recommendations.extend([
                "🧘‍♀️ Implement daily 10-minute mindfulness practice",
                "📚 Consider stress management workshop or online course"
            ])
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def predict_intervention_outcomes(self, user_data: Dict, interventions: List[str]) -> Dict:
        """Predict outcomes for specific interventions"""
        features = self.prepare_features(user_data)
        features_scaled = self.scalers['main'].transform(features)
        
        # Predict baseline effectiveness
        base_effectiveness = self.models['intervention_effectiveness'].predict(features_scaled)[0]
        time_to_improvement = self.models['time_predictor'].predict(features_scaled)[0]
        
        # Intervention-specific modifiers
        intervention_modifiers = {
            'mindfulness': {'effectiveness': 1.2, 'time_factor': 0.8},
            'exercise': {'effectiveness': 1.15, 'time_factor': 0.9},
            'therapy': {'effectiveness': 1.4, 'time_factor': 0.7},
            'workplace_change': {'effectiveness': 1.3, 'time_factor': 1.2},
            'social_support': {'effectiveness': 1.1, 'time_factor': 0.85}
        }
        
        results = {}
        for intervention in interventions:
            # Map intervention to modifier
            modifier_key = 'therapy'  # default
            for key in intervention_modifiers:
                if key in intervention.lower():
                    modifier_key = key
                    break
            
            modifier = intervention_modifiers[modifier_key]
            
            results[intervention] = {
                'effectiveness_score': min(0.95, base_effectiveness * modifier['effectiveness']),
                'estimated_weeks': max(2, time_to_improvement * modifier['time_factor']),
                'confidence': 0.75 + (base_effectiveness * 0.2)
            }
        
        return results
    
    def save_models(self, filepath: str = "ml_models"):
        """Save trained models to disk"""
        import os
        os.makedirs(filepath, exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, f"{filepath}/{name}.joblib")
        
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f"{filepath}/scaler_{name}.joblib")
        
        # Save metadata
        with open(f"{filepath}/model_metadata.json", 'w') as f:
            json.dump({
                'feature_importance': self.feature_importance,
                'model_version': '1.0',
                'training_samples': len(self.training_data)
            }, f, indent=2)
        
        print(f"✅ Models saved to {filepath}")
    
    def load_models(self, filepath: str = "ml_models"):
        """Load trained models from disk"""
        import os
        if not os.path.exists(filepath):
            print("⚠️ No saved models found, using freshly trained models")
            return
        
        try:
            model_files = [f for f in os.listdir(filepath) if f.endswith('.joblib') and not f.startswith('scaler_')]
            
            for model_file in model_files:
                model_name = model_file.replace('.joblib', '')
                self.models[model_name] = joblib.load(f"{filepath}/{model_file}")
            
            scaler_files = [f for f in os.listdir(filepath) if f.startswith('scaler_')]
            for scaler_file in scaler_files:
                scaler_name = scaler_file.replace('scaler_', '').replace('.joblib', '')
                self.scalers[scaler_name] = joblib.load(f"{filepath}/{scaler_file}")
            
            # Load metadata
            with open(f"{filepath}/model_metadata.json", 'r') as f:
                metadata = json.load(f)
                self.feature_importance = metadata['feature_importance']
            
            self.is_trained = True
            print(f"✅ Models loaded from {filepath}")
            
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            print("Using freshly trained models instead")

class PersonalizedInterventionEngine:
    """Advanced engine for personalized intervention recommendations"""
    
    def __init__(self, ml_engine: PsychologicalMLEngine):
        self.ml_engine = ml_engine
        self.intervention_database = self.build_intervention_database()
    
    def build_intervention_database(self) -> Dict:
        """Build comprehensive intervention database with effectiveness data"""
        return {
            'mindfulness_interventions': [
                {
                    'name': 'Daily Mindfulness Meditation',
                    'description': '10-15 minutes guided meditation daily',
                    'effectiveness_research': 0.78,
                    'time_to_effect': '2-4 weeks',
                    'effort_level': 'Low',
                    'evidence_level': 'Strong',
                    'target_conditions': ['stress', 'anxiety', 'burnout']
                },
                {
                    'name': 'Mindful Breathing Exercises',
                    'description': '4-7-8 breathing technique during stressful moments',
                    'effectiveness_research': 0.65,
                    'time_to_effect': 'Immediate-1 week',
                    'effort_level': 'Very Low',
                    'evidence_level': 'Moderate',
                    'target_conditions': ['acute_stress', 'anxiety']
                }
            ],
            'cognitive_interventions': [
                {
                    'name': 'Cognitive Restructuring',
                    'description': 'Challenge and reframe negative thought patterns',
                    'effectiveness_research': 0.82,
                    'time_to_effect': '3-6 weeks',
                    'effort_level': 'Moderate',
                    'evidence_level': 'Very Strong',
                    'target_conditions': ['depression', 'anxiety', 'stress']
                },
                {
                    'name': 'Thought Records',
                    'description': 'Daily logging of thoughts, emotions, and situations',
                    'effectiveness_research': 0.71,
                    'time_to_effect': '2-4 weeks',
                    'effort_level': 'Low-Moderate',
                    'evidence_level': 'Strong',
                    'target_conditions': ['negative_thinking', 'depression']
                }
            ],
            'behavioral_interventions': [
                {
                    'name': 'Progressive Exercise Program',
                    'description': 'Structured 30-minute exercise 3-4x per week',
                    'effectiveness_research': 0.77,
                    'time_to_effect': '3-4 weeks',
                    'effort_level': 'Moderate-High',
                    'evidence_level': 'Very Strong',
                    'target_conditions': ['depression', 'stress', 'general_wellbeing']
                },
                {
                    'name': 'Sleep Hygiene Protocol',
                    'description': 'Consistent sleep schedule and environment optimization',
                    'effectiveness_research': 0.68,
                    'time_to_effect': '1-2 weeks',
                    'effort_level': 'Low',
                    'evidence_level': 'Strong',
                    'target_conditions': ['sleep_issues', 'fatigue', 'stress']
                }
            ],
            'workplace_interventions': [
                {
                    'name': 'Time Management Training',
                    'description': 'Prioritization and scheduling optimization',
                    'effectiveness_research': 0.63,
                    'time_to_effect': '2-3 weeks',
                    'effort_level': 'Moderate',
                    'evidence_level': 'Moderate',
                    'target_conditions': ['work_stress', 'overwhelm']
                },
                {
                    'name': 'Boundary Setting Workshop',
                    'description': 'Learn to set healthy work-life boundaries',
                    'effectiveness_research': 0.69,
                    'time_to_effect': '3-5 weeks',
                    'effort_level': 'Moderate',
                    'evidence_level': 'Strong',
                    'target_conditions': ['work_life_balance', 'burnout']
                }
            ]
        }
    
    def recommend_personalized_interventions(self, user_data: Dict, 
                                           assessment_results: Dict,
                                           max_recommendations: int = 5) -> List[InterventionRecommendation]:
        """Generate personalized intervention recommendations using ML"""
        
        # Get ML prediction for user
        ml_prediction = self.ml_engine.predict_risk_assessment(user_data)
        
        # Identify primary concerns from assessment results
        primary_concerns = self.identify_primary_concerns(assessment_results)
        
        # Get all potential interventions
        all_interventions = []
        for category, interventions in self.intervention_database.items():
            for intervention in interventions:
                all_interventions.append((category, intervention))
        
        # Score interventions based on relevance and ML predictions
        scored_interventions = []
        
        for category, intervention in all_interventions:
            # Calculate relevance score
            relevance_score = self.calculate_intervention_relevance(
                intervention, primary_concerns, user_data
            )
            
            # Get ML prediction for this intervention
            ml_outcomes = self.ml_engine.predict_intervention_outcomes(
                user_data, [intervention['name']]
            )
            
            if intervention['name'] in ml_outcomes:
                ml_effectiveness = ml_outcomes[intervention['name']]['effectiveness_score']
                estimated_weeks = ml_outcomes[intervention['name']]['estimated_weeks']
            else:
                ml_effectiveness = intervention['effectiveness_research']
                estimated_weeks = 4  # default
            
            # Combined score
            combined_score = (relevance_score * 0.4 + 
                            ml_effectiveness * 0.4 + 
                            intervention['effectiveness_research'] * 0.2)
            
            recommendation = InterventionRecommendation(
                intervention_type=intervention['name'],
                priority=0,  # Will be set after sorting
                effectiveness_score=combined_score,
                time_to_effect=f"{estimated_weeks:.0f} weeks",
                effort_level=intervention['effort_level'],
                evidence_level=intervention['evidence_level']
            )
            
            scored_interventions.append((combined_score, recommendation))
        
        # Sort by score and assign priorities
        scored_interventions.sort(key=lambda x: x[0], reverse=True)
        final_recommendations = []
        
        for i, (score, recommendation) in enumerate(scored_interventions[:max_recommendations]):
            recommendation.priority = i + 1
            final_recommendations.append(recommendation)
        
        return final_recommendations
    
    def identify_primary_concerns(self, assessment_results: Dict) -> List[str]:
        """Identify primary psychological concerns from assessment results"""
        concerns = []
        
        if 'pss10' in assessment_results:
            if assessment_results['pss10'] >= 20:
                concerns.append('stress')
            if assessment_results['pss10'] >= 27:
                concerns.append('severe_stress')
        
        if 'dass21_depression' in assessment_results:
            if assessment_results['dass21_depression'] >= 14:
                concerns.append('depression')
        
        if 'dass21_anxiety' in assessment_results:
            if assessment_results['dass21_anxiety'] >= 10:
                concerns.append('anxiety')
        
        if 'burnout_emotional_exhaustion' in assessment_results:
            if assessment_results['burnout_emotional_exhaustion'] >= 27:
                concerns.append('burnout')
        
        return concerns
    
    def calculate_intervention_relevance(self, intervention: Dict, 
                                       concerns: List[str], user_data: Dict) -> float:
        """Calculate how relevant an intervention is for specific user"""
        relevance_score = 0.0
        
        # Check if intervention targets user's concerns
        target_conditions = intervention.get('target_conditions', [])
        for concern in concerns:
            if concern in target_conditions:
                relevance_score += 0.3
        
        # User-specific factors
        work_hours = user_data.get('work_hours_per_week', 40)
        if work_hours > 50 and 'work' in intervention['name'].lower():
            relevance_score += 0.2
        
        sleep_hours = user_data.get('sleep_hours', 7)
        if sleep_hours < 6 and 'sleep' in intervention['name'].lower():
            relevance_score += 0.3
        
        exercise_freq = user_data.get('exercise_frequency', 2)
        if exercise_freq < 2 and 'exercise' in intervention['name'].lower():
            relevance_score += 0.2
        
        return min(1.0, relevance_score)

# Usage example and testing
if __name__ == "__main__":
    # Initialize ML engine
    ml_engine = PsychologicalMLEngine()
    
    # Test prediction
    test_user = {
        'age': 32,
        'years_experience': 8,
        'work_hours_per_week': 55,
        'sleep_hours': 5.5,
        'exercise_frequency': 1,
        'social_support': 4,
        'prev_pss10': 22
    }
    
    # Test risk prediction
    risk_prediction = ml_engine.predict_risk_assessment(test_user)
    print(f"Risk Level: {risk_prediction.risk_level}")
    print(f"Confidence: {risk_prediction.confidence:.3f}")
    print(f"Key Factors: {risk_prediction.factors}")
    
    # Test intervention recommendations
    intervention_engine = PersonalizedInterventionEngine(ml_engine)
    recommendations = intervention_engine.recommend_personalized_interventions(
        test_user, {'pss10': 25, 'dass21_anxiety': 12}
    )
    
    print("\nPersonalized Recommendations:")
    for rec in recommendations:
        print(f"{rec.priority}. {rec.intervention_type} (Score: {rec.effectiveness_score:.3f})")
    
    # Save models
    ml_engine.save_models()