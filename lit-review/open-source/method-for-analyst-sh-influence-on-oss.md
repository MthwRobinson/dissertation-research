# A method for analyzing stakeholders’ influence on an open source software ecosystem’s requirements engineering process

Linåker, Johan, Björn Regnell, and Daniela Damian. "A method for analyzing stakeholders’ influence on an open source software ecosystem’s requirements engineering process." Requirements Engineering (2019): 1-16

## Summary

- Users of OSS may also be contributors
- Project management for OSS informal and decentralized
    - SHs prove merit by actively engaging
- Goal of paper: develop a way to measure the level of influence of a SH in the RE process for an OSS project.
- Stakeholder Influence Analysis:
    1. Determine the goal of the analysis
    2. Limit the scope of the analysis to the goal
    3. Analyze requirements (this will be GitHub issues in our case)
    4. Classify participants (users vs contributors in our case)
    5. Create SH networks
        - Note, in this method, connections can be weighted based on the magnitude of the interaction.
    6. Create influence profiles using network centrality measures
    7. Analyze the SH networks.
- Alternatives
    - Which SHs hold seats on committees within the governance process for the OSS project
    - Use count based measures instead of newtork centrality
- Potential downfalls
    - Gives weight based on number of lines of code added / removed, may overly weight non-meaningful contributions (i.e. when a ipynb notebook is changed)
    - Considering all issues as requirements: could be addressed with natural language processing
    - Figuring out the affiliaiton of SHs in the system
  - Goal: help firms determine their contribution strategy to an OSS ecosystem so they can drive development in a way that is consistent with their interests.


## Thoughts

- This paper is very similar to ours, but focuses on the role of firms instead of crowds. I think this is a different subset of OSS than we are looking at.
- We are not competing with this paper, we're users of its methodology.

## Follow on Reading

1. Scacchi W (2002) Understanding the requirements for develop- ing open source software systems. In: Software, IEE proceed- ings, vol 149, pp 24–39. IET
2. Frooman J (1999) Stakeholder influence strategies. Acad Manag Rev 24(2):191–205
3. Pacheco C, Garcia I (2012) A systematic literature review of stakeholder identification methods in requirements elicitation. J Syst Softw 85(9):2171–2181
4. Freeman RE (1984) Strategic management: a stakeholder approach. Cambridge University Press, Cambridge
5. Wasserman S, Faust K (1994) Social network analysis: methods and applications, vol 8. Cambridge University Press, Cambridge
6. Linåker J, Rempel P, Regnell B, Mäder P, (2016) How firms adapt and interact in open source ecosystems: analyzing stake- holder influence and collaboration patterns. In: Daneva M, Pas- tor O (eds) Requirements engineering: foundation for software quality, REFSQ, (2016) Lecture Notes in Computer Science, vol 9619. Springer, Cham
7. Newcombe Robert (2003) From client to project stakehold- ers: a stakeholder mapping approach. Constr Manag Econ 21(8):841–848
8. Munir H, Linåker J, Wnuk K, Runeson P, Regnell Björn (2018) Open innovation using open source tools: a case study at sony mobile. Empir Softw Eng 23(1):186–223
9. Mitchell RK, Agle BR, Wood DJ (1997) Toward a theory of stakeholder identification and salience: defining the principle of who and what really counts. Acad Manag Rev 22(4):853–886
10. Freeman LC (1978) Centrality in social networks conceptual clari- fication. Soc Netw 1(3):215–239
11. Joblin M, Apel S, Hunsen C, Mauerer W (2017) Classifying devel- opers into core and peripheral: an empirical study on count and network metrics. In: Proceedings of the 39th international confer- ence on software engineering, pp 164–174. IEEE Press
12. O’Mahony S (2007) The governance of open source initiatives: what does it mean to be community managed? J Manag Gov 11(2):139–150
