# enhanced_setup_vectorstore.py

import os
import json
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def create_enhanced_knowledge_base():
    """Create enhanced knowledge base with evidence-based psychological interventions"""
    
    knowledge_base_dir = Path("enhanced_knowledge_base")
    knowledge_base_dir.mkdir(exist_ok=True)
    
    # Evidence-based psychological content
    knowledge_content = {
        "cognitive_behavioral_interventions.txt": """
# Cognitive Behavioral Interventions for Workplace Stress

## Cognitive Restructuring Techniques

### Thought Records and Cognitive Distortions
- Catastrophic thinking: "If I make one mistake, I'll lose my job"
- All-or-nothing thinking: "I'm either perfect or a complete failure"
- Mind reading: "My boss thinks I'm incompetent"
- Fortune telling: "This presentation will be a disaster"

### CBT Techniques for Stress Management:
1. **The ABC Model**: Antecedent → Belief → Consequence
2. **Thought challenging**: What's the evidence for/against this thought?
3. **Behavioral experiments**: Testing out feared scenarios
4. **Activity scheduling**: Balancing work and pleasant activities
5. **Problem-solving training**: Define → Generate → Evaluate → Implement

### Workplace-Specific CBT Applications:
- Deadline anxiety: Breaking tasks into smaller, manageable chunks
- Perfectionism: Setting "good enough" standards for different tasks
- Impostor syndrome: Collecting evidence of competence and achievements
- Conflict avoidance: Assertiveness training and communication skills

## Research Evidence:
Meta-analyses show CBT for workplace stress has medium to large effect sizes (d = 0.68)
Particularly effective for anxiety-related workplace issues and burnout prevention.
        """,
        
        "mindfulness_based_interventions.txt": """
# Mindfulness-Based Stress Reduction (MBSR) for Workplace Wellness

## Core Mindfulness Practices

### Daily Mindfulness Exercises:
1. **Mindful Breathing**: 5-minute breathing awareness exercises
2. **Body Scan**: Progressive body awareness for tension release
3. **Mindful Walking**: Incorporating mindfulness into daily movement
4. **Loving-kindness meditation**: Improving workplace relationships

### Workplace-Integrated Mindfulness:
- **Mindful Email**: Pausing before responding to stressful emails
- **Meeting Mindfulness**: Brief centering before important meetings
- **Transition Rituals**: Mindful moments between tasks/meetings
- **Mindful Listening**: Full presence during conversations

## Micro-Interventions (1-3 minutes):
- **3-3-3 Technique**: Notice 3 things you see, 3 sounds, move 3 body parts
- **Box Breathing**: 4-4-4-4 breathing pattern
- **STOP Technique**: Stop, Take a breath, Observe, Proceed mindfully
- **Five Senses Check-in**: Grounding technique using all senses

## Research Evidence:
- 28% reduction in stress levels after 8-week MBSR program
- Improved emotional regulation and reduced burnout
- Enhanced focus and cognitive flexibility
- Better interpersonal relationships at work

## Implementation Guidelines:
Start with 2-3 minutes daily, gradually increase to 10-20 minutes
Consistency more important than duration
Use apps like Headspace for Work or Calm for Business
        """,
        
        "burnout_recovery_protocols.txt": """
# Evidence-Based Burnout Recovery Protocols

## Maslach Burnout Inventory Intervention Mapping

### For High Emotional Exhaustion:
1. **Energy Management**: 
   - Sleep hygiene optimization (7-9 hours quality sleep)
   - Nutrition planning (regular meals, reduced caffeine/alcohol)
   - Exercise prescription (150 min moderate activity/week)
   - Micro-recovery periods (5-10 minutes every 90 minutes)

2. **Workload Management**:
   - Task prioritization using Eisenhower Matrix
   - Delegation strategies and saying "no" effectively
   - Time blocking and calendar management
   - Boundary setting with supervisors and colleagues

### For High Depersonalization:
1. **Reconnection Strategies**:
   - Values clarification exercises
   - Meaning-making activities (connecting work to larger purpose)
   - Social connection initiatives (team building, peer support)
   - Empathy training and perspective-taking exercises

2. **Communication Enhancement**:
   - Active listening skills development
   - Conflict resolution training
   - Assertiveness training
   - Feedback giving and receiving skills

### For Low Personal Accomplishment:
1. **Achievement Recognition**:
   - Daily accomplishment logging
   - Skill inventory and strength identification
   - Progress tracking and milestone celebration
   - Portfolio development and career planning

2. **Professional Development**:
   - Learning opportunities and skill building
   - Mentoring relationships (as mentor and mentee)
   - Goal setting using SMART criteria
   - Regular performance feedback sessions

## Recovery Phases:
- **Phase 1 (0-4 weeks)**: Stabilization and symptom management
- **Phase 2 (1-3 months)**: Skill building and coping strategy development
- **Phase 3 (3-6 months)**: Integration and lifestyle changes
- **Phase 4 (6-12 months)**: Maintenance and prevention planning

## Warning Signs Requiring Professional Help:
- Persistent sleep disturbances for >2 weeks
- Significant appetite changes or weight loss/gain
- Substance use increases
- Thoughts of self-harm or suicide
- Complete inability to function at work for >3-5 days
        """,
        
        "work_life_balance_strategies.txt": """
# Evidence-Based Work-Life Balance Strategies

## The Four Domains of Work-Life Balance

### 1. Work Domain Optimization:
- **Time Management**: Pomodoro Technique, time-blocking, priority matrices
- **Technology Boundaries**: Email curfews, notification management
- **Workspace Design**: Ergonomics, lighting, personalization
- **Task Efficiency**: Automation, delegation, streamlining processes

### 2. Personal Domain Enhancement:
- **Self-Care Routines**: Daily, weekly, and monthly self-care activities
- **Hobby Cultivation**: Creative outlets, learning new skills
- **Physical Health**: Exercise, nutrition, sleep hygiene
- **Mental Health**: Therapy, meditation, journaling

### 3. Family/Relationship Domain:
- **Quality Time**: Undivided attention during family interactions
- **Communication**: Regular check-ins, active listening
- **Shared Responsibilities**: Equitable distribution of household tasks
- **Couple/Family Meetings**: Regular relationship maintenance

### 4. Community Domain:
- **Social Connections**: Maintaining friendships, social activities
- **Volunteer Work**: Giving back and finding purpose
- **Professional Networks**: Industry connections, mentoring
- **Neighborhood Involvement**: Local community participation

## Boundary Management Strategies:

### Physical Boundaries:
- Separate workspaces when working from home
- Changing clothes as a transition ritual
- Physical movement between work and personal time
- Technology placement and usage rules

### Temporal Boundaries:
- Set start and end times for work
- Protected time for personal activities
- Transition rituals between work and home
- Weekend and vacation protection strategies

### Emotional Boundaries:
- Compartmentalization techniques
- Emotional regulation strategies
- Stress inoculation training
- Mindfulness and present-moment awareness

## Work-Life Integration vs. Balance:
Integration focuses on synergy between domains rather than separation
Examples: Job crafting, flextime arrangements, remote work optimization
Research shows integration may be more sustainable for some personality types

## Measurement and Monitoring:
- Weekly work-life balance assessment
- Energy level tracking
- Relationship satisfaction monitoring
- Achievement and fulfillment evaluation
        """,
        
        "job_satisfaction_enhancement.txt": """
# Job Satisfaction Enhancement: Research-Based Approaches

## Herzberg's Two-Factor Theory Application

### Hygiene Factors (Prevent Dissatisfaction):
- **Compensation**: Fair pay, benefits, job security
- **Working Conditions**: Safe, comfortable, well-equipped environment
- **Company Policies**: Clear, fair, consistently applied policies
- **Supervision**: Supportive, competent, accessible management
- **Interpersonal Relations**: Positive relationships with colleagues

### Motivators (Create Satisfaction):
- **Achievement**: Completing challenging tasks, reaching goals
- **Recognition**: Acknowledgment of contributions and successes
- **Work Itself**: Engaging, meaningful, varied tasks
- **Responsibility**: Autonomy and decision-making authority
- **Advancement**: Career growth and promotion opportunities

## Job Crafting Strategies:

### Task Crafting:
- Modify the number, type, or scope of tasks
- Take on additional responsibilities that align with interests
- Change how tasks are performed to increase engagement
- Eliminate or minimize unsatisfying tasks where possible

### Relational Crafting:
- Build stronger relationships with colleagues
- Expand interactions with clients or beneficiaries
- Seek mentoring relationships
- Collaborate on projects with inspiring team members

### Cognitive Crafting:
- Reframe job purpose and meaning
- Connect individual tasks to larger organizational goals
- Focus on the positive impact of your work
- Develop a growth mindset about challenges

## PERMA Model for Workplace Wellbeing:

### Positive Emotions:
- Gratitude practices in the workplace
- Celebrating successes and milestones
- Humor and playfulness when appropriate
- Optimism and positive communication

### Engagement:
- Flow state cultivation through skill-challenge balance
- Focus on strengths utilization
- Minimize distractions and multitasking
- Create clear goals and feedback loops

### Relationships:
- Build positive workplace relationships
- Practice active-constructive responding
- Develop emotional intelligence
- Engage in prosocial behaviors

### Meaning:
- Connect work to personal values
- Understand impact on others and society
- Participate in meaningful projects
- Volunteer for causes aligned with company values

### Achievement:
- Set and pursue meaningful goals
- Develop skills and competencies
- Seek challenging assignments
- Celebrate progress and accomplishments

## Organizational Interventions:
- Job rotation and cross-training programs
- Employee recognition systems
- Professional development opportunities
- Flexible work arrangements
- Team building and social events
        """,
        
        "anxiety_depression_workplace.txt": """
# Workplace Anxiety and Depression: Clinical Interventions

## Anxiety Disorders in the Workplace

### Common Workplace Anxiety Presentations:
- **Performance Anxiety**: Fear of evaluation, presentations, meetings
- **Social Anxiety**: Interpersonal interactions, networking events
- **Generalized Anxiety**: Chronic worry about work performance
- **Panic Disorder**: Unexpected panic attacks during work hours

### Evidence-Based Interventions:

#### Cognitive Interventions:
1. **Probability Estimation**: "What's the realistic likelihood of this feared outcome?"
2. **Decatastrophizing**: "Even if the worst happens, how would I cope?"
3. **Cost-Benefit Analysis**: Weighing the pros and cons of anxiety-driven behaviors
4. **Cognitive Defusion**: Observing thoughts without being controlled by them

#### Behavioral Interventions:
1. **Graduated Exposure**: Systematic desensitization to feared situations
2. **Response Prevention**: Avoiding safety behaviors that maintain anxiety
3. **Assertiveness Training**: Building confidence in workplace communication
4. **Relaxation Training**: Progressive muscle relaxation, diaphragmatic breathing

### Accommodation Strategies:
- Flexible work arrangements
- Modified work schedules
- Quiet workspaces
- Written rather than verbal instructions
- Regular check-ins with supervisors

## Depression in the Workplace

### Workplace Depression Symptoms:
- Decreased productivity and concentration
- Increased absenteeism and presenteeism
- Social withdrawal from colleagues
- Reduced motivation and energy
- Difficulty making decisions

### Behavioral Activation Techniques:
1. **Activity Scheduling**: Planning rewarding and meaningful activities
2. **Mastery and Pleasure Ratings**: Tracking engagement in daily activities
3. **Graded Task Assignment**: Breaking large tasks into manageable steps
4. **Social Activation**: Increasing interpersonal interactions

### Cognitive Restructuring for Depression:
- Challenging negative automatic thoughts
- Identifying cognitive distortions (mental filter, personalization)
- Developing balanced thinking patterns
- Building self-compassion and reducing self-criticism

## Return-to-Work Protocols:

### Graduated Return:
- Phase 1: Part-time hours with essential tasks only
- Phase 2: Increased hours with moderate responsibilities
- Phase 3: Full-time with gradual return of all duties
- Phase 4: Full regular duties with ongoing support

### Workplace Modifications:
- Reduced or modified workload
- Flexible scheduling
- Work-from-home options
- Ergonomic assessments
- Access to employee assistance programs

## Crisis Intervention:
- Immediate supervisor notification protocols
- Employee assistance program referrals
- Mental health first aid training for managers
- Suicide risk assessment and safety planning
- Collaboration with healthcare providers
        """,
        
        "positive_psychology_interventions.txt": """
# Positive Psychology Interventions for Workplace Wellbeing

## Character Strengths Application

### VIA Character Strengths in the Workplace:
1. **Wisdom Strengths**: Creativity, curiosity, judgment, love of learning, perspective
2. **Courage Strengths**: Bravery, perseverance, honesty, zest
3. **Humanity Strengths**: Love, kindness, social intelligence
4. **Justice Strengths**: Teamwork, fairness, leadership
5. **Temperance Strengths**: Forgiveness, humility, prudence, self-regulation
6. **Transcendence Strengths**: Appreciation of beauty, gratitude, hope, humor, spirituality

### Strengths-Based Interventions:
- **Strengths Identification**: VIA Survey completion and interpretation
- **Strengths Spotting**: Recognizing strengths in colleagues
- **Strengths Development**: Deliberate practice of signature strengths
- **Strengths Partnerships**: Collaborating with complementary strengths

## Gratitude Interventions

### Three Good Things Exercise:
Write down three things that went well each day and explain why they were meaningful
Practice for one week, significant increases in happiness and decreases in depression

### Gratitude Letter:
Write a letter to someone who has positively impacted your career
Deliver and read the letter in person for maximum impact
Effects include increased positive emotions and life satisfaction

### Workplace Gratitude Practices:
- Daily gratitude sharing in team meetings
- Gratitude wall or board in common areas
- Thank-you note campaigns
- Appreciation circles and recognition ceremonies

## Flow and Engagement Enhancement

### Flow Conditions:
1. **Clear Goals**: Specific, achievable objectives
2. **Immediate Feedback**: Regular performance information
3. **Balance of Challenge and Skill**: Optimal difficulty level
4. **Concentration**: Single-tasking and deep focus
5. **Present Moment Awareness**: Mindful engagement with tasks

### Job Design for Flow:
- Task variety and complexity adjustment
- Autonomy and decision-making authority
- Skill development opportunities
- Regular feedback systems
- Minimization of interruptions and distractions

## Meaning and Purpose Interventions

### Best Possible Self Exercise:
Write about your ideal future self in vivid detail
Include career aspirations, relationships, and personal growth
Increases optimism and goal-directed behavior

### Values Clarification:
- Identify core personal and professional values
- Align daily actions with identified values
- Make values-based decisions in challenging situations
- Communicate values to supervisors and team members

### Benefit Finding:
- Identify positive aspects of challenging work experiences
- Focus on growth, resilience, and learning opportunities
- Share stories of overcoming workplace obstacles
- Develop post-traumatic growth narratives

## Hope and Optimism Building

### Hope Theory Components:
1. **Goals**: Clear, specific, achievable objectives
2. **Pathways**: Multiple routes to achieve goals
3. **Agency**: Belief in one's ability to pursue goals

### Optimism Training:
- Explanatory style modification (internal, stable, global vs. external, unstable, specific)
- Best possible self visualization
- Positive future scenario planning
- Resilience building through adversity reframing

## Implementation in Organizations:
- Positive leadership training programs
- Strengths-based performance management
- Wellbeing committees and initiatives
- Positive organizational culture development
- Measurement and evaluation of positive outcomes
        """
    }
    
    # Write knowledge base files
    for filename, content in knowledge_content.items():
        file_path = knowledge_base_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Created {len(knowledge_content)} enhanced knowledge base files")
    return knowledge_base_dir

def create_psychological_norms():
    """Create normative data for psychological assessments"""
    
    norms_dir = Path("psychological_norms")
    norms_dir.mkdir(exist_ok=True)
    
    # Normative data for various assessments
    norms_data = {
        "pss10_norms.json": {
            "description": "PSS-10 Normative Data",
            "source": "Cohen, S., Kamarck, T., & Mermelstein, R. (1983)",
            "sample_size": 2387,
            "demographics": {
                "age_range": "18-65",
                "gender_distribution": "55% female, 45% male"
            },
            "percentiles": {
                "10": 6,
                "25": 9,
                "50": 13,
                "75": 17,
                "90": 22
            },
            "categories": {
                "low": {"range": "0-13", "description": "Low perceived stress"},
                "moderate": {"range": "14-26", "description": "Moderate perceived stress"},
                "high": {"range": "27-40", "description": "High perceived stress"}
            },
            "occupational_norms": {
                "healthcare": {"mean": 16.2, "sd": 6.8},
                "education": {"mean": 14.5, "sd": 6.2},
                "finance": {"mean": 15.8, "sd": 7.1},
                "technology": {"mean": 13.9, "sd": 6.5},
                "retail": {"mean": 17.1, "sd": 7.3}
            }
        },
        
        "dass21_norms.json": {
            "description": "DASS-21 Normative Data",
            "source": "Antony, M. M., Bieling, P. J., Cox, B. J., Enns, M. W., & Swinson, R. P. (1998)",
            "categories": {
                "depression": {
                    "normal": {"range": "0-9", "severity": "Normal"},
                    "mild": {"range": "10-13", "severity": "Mild"},
                    "moderate": {"range": "14-20", "severity": "Moderate"},
                    "severe": {"range": "21-27", "severity": "Severe"},
                    "extremely_severe": {"range": "28+", "severity": "Extremely Severe"}
                },
                "anxiety": {
                    "normal": {"range": "0-7", "severity": "Normal"},
                    "mild": {"range": "8-9", "severity": "Mild"},
                    "moderate": {"range": "10-14", "severity": "Moderate"},
                    "severe": {"range": "15-19", "severity": "Severe"},
                    "extremely_severe": {"range": "20+", "severity": "Extremely Severe"}
                },
                "stress": {
                    "normal": {"range": "0-14", "severity": "Normal"},
                    "mild": {"range": "15-18", "severity": "Mild"},
                    "moderate": {"range": "19-25", "severity": "Moderate"},
                    "severe": {"range": "26-33", "severity": "Severe"},
                    "extremely_severe": {"range": "34+", "severity": "Extremely Severe"}
                }
            }
        },
        
        "mbi_norms.json": {
            "description": "Maslach Burnout Inventory Normative Data",
            "source": "Maslach, C., Jackson, S. E., & Leiter, M. P. (1996)",
            "dimensions": {
                "emotional_exhaustion": {
                    "low": {"range": "0-16", "percentile": "Lower third"},
                    "moderate": {"range": "17-26", "percentile": "Middle third"},
                    "high": {"range": "27+", "percentile": "Upper third"}
                },
                "depersonalization": {
                    "low": {"range": "0-8", "percentile": "Lower third"},
                    "moderate": {"range": "9-13", "percentile": "Middle third"},
                    "high": {"range": "14+", "percentile": "Upper third"}
                },
                "personal_accomplishment": {
                    "high": {"range": "32+", "percentile": "Upper third", "interpretation": "Good"},
                    "moderate": {"range": "25-31", "percentile": "Middle third", "interpretation": "Average"},
                    "low": {"range": "0-24", "percentile": "Lower third", "interpretation": "Concerning"}
                }
            }
        }
    }
    
    # Write norms files
    for filename, data in norms_data.items():
        file_path = norms_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {len(norms_data)} psychological norms files")
    return norms_dir

def setup_enhanced_vectorstore():
    """Setup enhanced vector store with all knowledge base"""
    
    print("🚀 Setting up Enhanced Strive Pro Vector Store...")
    
    # Create enhanced knowledge base
    kb_dir = create_enhanced_knowledge_base()
    
    # Create psychological norms
    norms_dir = create_psychological_norms()
    
    # Check if knowledge base exists and has content
    if not kb_dir.exists() or not any(kb_dir.iterdir()):
        print("❌ Error: Enhanced knowledge base directory is empty")
        return False
    
    print(f"📚 Processing knowledge base from: {kb_dir}")
    
    try:
        # Load documents from the enhanced knowledge base
        loader = DirectoryLoader(
            str(kb_dir),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={'autodetect_encoding': True}
        )
        documents = loader.load()
        print(f"✅ Loaded {len(documents)} documents")
        
        if not documents:
            print("❌ No documents found to process")
            return False
        
        # Enhanced text splitting with overlap for better context
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        texts = text_splitter.split_documents(documents)
        print(f"📄 Split into {len(texts)} text chunks")
        
        # Add metadata for better retrieval
        for i, text in enumerate(texts):
            text.metadata['chunk_id'] = i
            text.metadata['source_type'] = 'knowledge_base'
            
            # Add content-based metadata
            content_lower = text.page_content.lower()
            if 'anxiety' in content_lower:
                text.metadata['topic'] = 'anxiety'
            elif 'depression' in content_lower:
                text.metadata['topic'] = 'depression'
            elif 'burnout' in content_lower:
                text.metadata['topic'] = 'burnout'
            elif 'stress' in content_lower:
                text.metadata['topic'] = 'stress'
            elif 'work-life' in content_lower or 'balance' in content_lower:
                text.metadata['topic'] = 'work_life_balance'
            else:
                text.metadata['topic'] = 'general'
        
        # Create embeddings using a high-quality model
        print("🧠 Creating embeddings... (This may take a few minutes)")
        embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Ensure CPU usage for compatibility
        )
        
        # Create and save FAISS vector store
        print("💾 Building FAISS vector store...")
        vectorstore = FAISS.from_documents(texts, embeddings)
        
        # Save the vector store
        vectorstore.save_local("faiss_index_strive_enhanced")
        
        print("\n" + "="*60)
        print("🎉 ENHANCED VECTOR STORE SUCCESSFULLY CREATED!")
        print("="*60)
        print(f"📊 Total documents processed: {len(documents)}")
        print(f"📄 Total text chunks: {len(texts)}")
        print("💾 Saved as: faiss_index_strive_enhanced")
        print("\n🔄 Update your app.py to use 'faiss_index_strive_enhanced'")
        print("="*60)
        
        # Test the vector store
        print("\n🧪 Testing vector store with sample queries...")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        test_queries = [
            "stress management techniques",
            "burnout recovery strategies", 
            "anxiety interventions workplace",
            "mindfulness exercises"
        ]
        
        for query in test_queries:
            results = retriever.invoke(query)
            print(f"Query: '{query}' -> Found {len(results)} relevant chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return False

if __name__ == "__main__":
    setup_enhanced_vectorstore()