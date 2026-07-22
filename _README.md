# ⚡ PersonaMesh: AI-Powered Workforce & Team Optimization Engine

PersonaMesh is an end-to-end Machine Learning and Evolutionary Computing framework that clusters candidate psychometric profiles and synthesizes Pareto-optimal engineering teams.

## 🌟 Benchmark Metrics
* **Clustering Cohesion:** Achieved a Silhouette Score of 0.2715 
(isolated behavioral clustering) vs 0.2545 (contaminated), 
confirming feature isolation improves profiling quality..
* **Algorithmic Benchmarking:** Evaluated K-Means++ (0.254) against Hierarchical Clustering (0.254), Gaussian Mixture Models (0.167), and DBSCAN (-0.147).
* **Multi-Objective Optimization:** Deployed an **NSGA-II genetic algorithm** balancing Technical Competence, Behavioral Synergy, and Seniority Balance.
* **Operational Performance Gain:** Outperformed random team allocation by +9.36% on Composite 
Team Fitness Index, with +18.24% behavioral diversity gain 
and 16.89% reduction in experience variance..

## 🏗️ System Architecture
1. **Psychometric Clustering:** Maps candidates into 4 macro-archetypes (*Collaborative Facilitators, Isolated Specialists, Proactive Visionaries, Autonomous Executors*).
2. **2D PCA Projection:** Projects 40-dimensional psychometric vectors onto a 2D Principal Component space for visual diagnostics.
3. **Pareto Decision Support:** Uses non-dominated sorting to recommend balanced team configurations without interpersonal friction.

## 🚀 Local Setup & Installation
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/PersonaMesh.git](https://github.com/YOUR_USERNAME/PersonaMesh.git)

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
