# Phase 2 Implementation Checklist

Use this checklist to track your progress on the Phase 2 term paper.

## 📋 Pre-Implementation

- [ ] Read `SUMMARY.md` for complete overview
- [ ] Review `QUICK_START.md` for step-by-step guide
- [ ] Check that all Phase 1 data files exist:
  - [ ] `data/processed/nodes.csv`
  - [ ] `data/processed/edges.csv`
  - [ ] `data/processed/posts.jsonl`
- [ ] Install LaTeX distribution (if not already installed)
- [ ] Set up Python environment

## 📝 LaTeX Paper Review

- [ ] Open `main.tex` in editor or Overleaf
- [ ] Read through the entire paper (skim is okay)
- [ ] Verify all sections are present:
  - [ ] Abstract
  - [ ] Introduction
  - [ ] Background
  - [ ] Literature Survey (12 papers)
  - [ ] Comparative Analysis
  - [ ] Implementation
  - [ ] Conclusions
  - [ ] Bibliography
- [ ] Check if any modifications needed for your context
- [ ] Compile LaTeX to ensure it works:
  - [ ] Run `./compile.sh` or manual compilation
  - [ ] Verify PDF is generated without errors

## 💻 Python Implementation

### Setup
- [ ] Navigate to `term_paper/implementation/`
- [ ] Create virtual environment (optional):
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verify data paths in `content_weighted_pagerank.py`

### Running the Code
- [ ] Run the main implementation:
  ```bash
  python content_weighted_pagerank.py
  ```
- [ ] Check that it completes without errors
- [ ] Verify output files are created:
  - [ ] `results/method_comparison.csv`
  - [ ] `../figures/score_distribution.pdf`

### Collect Results
- [ ] Note convergence iterations
- [ ] Save top-10 authors output
- [ ] Record performance metrics:
  - [ ] Precision@10
  - [ ] Precision@20
  - [ ] nDCG@10
  - [ ] nDCG@20
- [ ] Take screenshots or save console output

## 📊 Update Paper with Results

### Section 5.5.1: Ranking Performance
- [ ] Update Table: "Ranking Performance Comparison"
  - [ ] Fill in actual Precision@10, @20 values
  - [ ] Fill in actual nDCG@10, @20 values
- [ ] Update text describing performance improvements

### Section 5.5.2: Top-10 Authors
- [ ] Complete Table: "Top-10 Authors Identified by CW-PR"
  - [ ] Replace placeholders with actual authors
  - [ ] Add actual CW-PR scores
  - [ ] Add post counts
  - [ ] Add average relevance scores

### Section 5.5.3: Convergence Analysis
- [ ] Add convergence plot if generated
- [ ] Update convergence iteration count
- [ ] Describe convergence behavior

### Section 5.5.4: Qualitative Analysis
- [ ] Update case study with top-ranked author details
- [ ] Add specific examples from your data
- [ ] Compare with baseline rankings

## 📈 Add Figures

- [ ] Generate score distribution plot
- [ ] Generate convergence plot (if not auto-generated)
- [ ] Optional: Create network visualization
- [ ] Optional: Create method comparison bar chart
- [ ] Place all figures in `term_paper/figures/` directory
- [ ] Verify LaTeX can find and include figures

## 🔍 Review and Polish

### Content Review
- [ ] Read through entire paper again
- [ ] Check all mathematical notation is consistent
- [ ] Verify all citations are correct
- [ ] Ensure results section is complete
- [ ] Check that conclusions match findings

### Technical Review
- [ ] Verify all tables are properly formatted
- [ ] Check all figures have captions
- [ ] Ensure all sections are referenced correctly
- [ ] Verify bibliography is complete

### Writing Quality
- [ ] Proofread for typos
- [ ] Check grammar
- [ ] Ensure consistent terminology
- [ ] Verify section transitions are smooth
- [ ] Check that abstract accurately summarizes paper

## 🔧 Final Compilation

- [ ] Recompile LaTeX with updated content:
  ```bash
  ./compile.sh
  ```
- [ ] Verify PDF is generated successfully
- [ ] Check PDF page count (~50-70 pages expected)
- [ ] Review PDF for formatting issues:
  - [ ] Tables fit on pages properly
  - [ ] Figures are clear and legible
  - [ ] No orphaned headers
  - [ ] Page numbers are correct

## 📤 Submission Preparation

### Documentation
- [ ] Ensure all README files are updated
- [ ] Verify implementation code is well-commented
- [ ] Check that all results files are included

### Package Contents
Create submission package with:
- [ ] `main.pdf` - Final compiled paper
- [ ] `main.tex` - LaTeX source
- [ ] `implementation/` - Python code directory
- [ ] `figures/` - All generated figures
- [ ] `results/` - Result CSV files
- [ ] README or SUMMARY document

### Final Checks
- [ ] Verify all author names and IDs are correct
- [ ] Check date is current
- [ ] Ensure course name and instructor name are correct
- [ ] Verify no placeholder text remains (search for "TODO", "[to be computed]")
- [ ] Check that all 12 papers are properly cited

## ✅ Pre-Submission Review

- [ ] Have another team member review the paper
- [ ] Check against assignment requirements:
  - [ ] Survey of 10+ papers? (We have 12 ✓)
  - [ ] Comparison table? (Multiple tables ✓)
  - [ ] Best method selected and justified? (CW-PR ✓)
  - [ ] Implementation included? (Complete code ✓)
  - [ ] Results on dataset? (To be added)
  - [ ] Proper citations? (15 references ✓)

## 🎯 Submission

- [ ] Create final submission archive:
  ```bash
  tar -czf phase2_term_paper.tar.gz term_paper/
  # or
  zip -r phase2_term_paper.zip term_paper/
  ```
- [ ] Verify archive contains all necessary files
- [ ] Upload to submission platform
- [ ] Confirm submission was successful
- [ ] Keep backup copy

## 📊 Optional Enhancements (If Time Permits)

- [ ] Add more visualizations (network graphs, heatmaps)
- [ ] Extend evaluation with additional metrics
- [ ] Add temporal analysis section
- [ ] Create presentation slides
- [ ] Write executive summary
- [ ] Generate alternative comparison formats
- [ ] Test on different parameter settings
- [ ] Add sensitivity analysis

## 🐛 Troubleshooting

### Common Issues

**LaTeX won't compile:**
- [ ] Check for missing packages
- [ ] Look for syntax errors in log file
- [ ] Try compiling on Overleaf
- [ ] Verify all citation keys exist

**Python code errors:**
- [ ] Check data file paths
- [ ] Verify all dependencies installed
- [ ] Look for version conflicts
- [ ] Test with smaller dataset first

**Results look wrong:**
- [ ] Verify data loading is correct
- [ ] Check normalization steps
- [ ] Compare with Phase 1 results
- [ ] Validate edge type weights

## 📝 Notes Section

Use this space to track issues, decisions, or important observations:

```
Date: ___________
Issue/Note:


Resolution/Action:


---

Date: ___________
Issue/Note:


Resolution/Action:


---

Date: ___________
Issue/Note:


Resolution/Action:


```

## ⏱️ Time Tracking

Estimated time for each phase:

- Pre-Implementation Review: 2-3 hours
- Run Python Implementation: 1-2 hours
- Update Paper with Results: 2-3 hours
- Add Figures: 1-2 hours
- Review and Polish: 2-3 hours
- Final Compilation: 1 hour

**Total Estimated Time: 9-14 hours (1-2 full working days)**

---

## 🎉 Completion

- [ ] All checklist items complete
- [ ] Paper successfully compiled
- [ ] Results added and verified
- [ ] Submission uploaded
- [ ] Backup created

**Submission Date:** ___________  
**Grade/Feedback:** ___________

---

**Good luck with your term paper!** 🚀
