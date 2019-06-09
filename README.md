# Dissertation Research

Name: Matt Robinson

School: George Washington University

Department: School of Engineering and Applied Science

Degree: PhD, Systems Engineering

Advisors: Dr. Shahram Sarkani, Dr. Thomas Mazzuchi

## Summary

Title: Network Structure and the Effectiveness of Crowd-Based Requirements Processes

Problem Statement: Crowd-based requirements processes enable systems engineers to gather feedback from a large number of stakeholders. However, some researchers have expressed concern that these processes overlook the needs of less connected stakeholders. The problem is to empirically assess how network structure affects the prioritization of crowd-sourced requirements.

Thesis: For large systems, crowd-based requirements processes favor stakeholders with high network centrality, do not adequately address all stakeholder needs, and should be supplemented with traditional stakeholder analysis.

Research Questions and Hypotheses
1. On average, how does the structure of a crowd-sourced stakeholder network change as the number of stakeholders grows?
    - As the number of stakeholders in a crowd-sourced stakeholder network grows, the degree distribution of the network becomes less distributed.
2. How does a stakeholder’s network centrality affect the probability that a system will address the stakeholder’s needs?
    - The lower the network centrality of a stakeholder, the lower the probability that the system will address the stakeholder’s needs.
3. How does the impact of network structure on requirements prioritization change as the size of the network grows?
    - As the number of stakeholders in a network increases, the impact of network structure on prioritization increases.
4. How does the impact of network structure on requirements prioritization change as the number of requirements grows?
    - As the number of requirements increases, the impact of network structure on prioritization increases.
5. Does a stakeholder’s position within a network affect the types of requirements the stakeholder generates?
    - On average, the similarity of the content of two stakeholders’ requirements decreases as the distance between them within the network grows.

## Methodology Map

![Methodology Map](https://github.com/MthwRobinson/dissertation-research/blob/master/img/methodology_map.png?raw=true)

## Research Utils

  The `research_utils` is a software package written in Python to aid with research tasks.
  To install the package, create a Python environment, navigate to `research_utils` and run `pip install -e .`.

  ### CLI Commands

  The following CLI commands are available through the `research_utils` package.

  #### Load Issues
  Example: `$ research_utils load-issues`

  Description: Connects to the Github API to fetch issues for open source packages and load them into a Postgres database for follow on analysis.
