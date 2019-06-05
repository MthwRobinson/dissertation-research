## The Crowd in Requirements Engineering

Chicago citation: Groen, Eduard C., Norbert Seyff, Raian Ali, Fabiano Dalpiaz, Joerg Doerr, Emitza Guzman, Mahmood Hosseini et al. "The crowd in requirements engineering: The landscape and challenges." IEEE software 34, no. 2 (2017): 44-52.

### Summary
- Useful when there are a large number of users who do not directly interact with product manageers.
- Traditional RE process do not allow product managers to receive continuous feedback from a large, diverse group of users.
- CrowdRE: process for producing validated users requirements based on feedback from a crowd. Ideally should be automated or semi-automated. **Note, other papers have not put as much emphasis on automations, and simply consider crowd sourced requirements**
- Crowd: "A large group of current or potential users of a software product who interact among themselves or with representatives of the product (software development team)"
    - Target group of stakeholders is very large and potentially diverse
- CrowdRE Approach:
    - "Depends on a continuous flow of user feedback". Question: what rate of flow is needed?
    - Users providing feedback need to be motivated. Question: do motivated users dominate the conversation to the detriment of requirements coverage?
    - Solicit feedback from users with different backgrounds and epxectations to avoid bias.
    - Crowd based feedback can supplement traditional requirements processes.
    - Claim: techniques to automatically analyze feedback avoids bias on the parts of requirements analysts. Noted text analysis / natural language processing as potential ways to automate.
- Crowd Member Types:
    1. Privacy Tolerant / Socially Ostentatious
    2. Privacy fanatical but generous
    3. Loyal and passionate
    4. Incentive seekers
    5. Perfectionists and complainers
    6. Impact seekers
- Similar Approaches:
    1. Customer Specific RE
    2. Crowd Sourcing -- difference, Crowd Based RE relies on crowed members who are interested in the product, whereas crowd sourcing normally provides some sort of reward for participating (i.e. bug bounties, or mechanical turk)
- Challenges:
    1. Need to motivated crowd members
    2. Forum for eliciting feedback
    3. Analyzing a large amount of feedback -- -they note that it's hard to identify subgroups of users, and that there's a risk that minority groups (ie peripheral members of the stakeholder network) may have their feedback overlooked.
    4. Monitoring context and usage -- focused on the impact of contradictory feedback
- Good quote: "empirical research and case studies are needed to validate CrowdRE and show that it provides the promised benefits" (this is what our research is doing)

### Thoughts
- For research: given how the requirements were managed for the open source project, could it have been improved if automated techniques were incorporated into the stakeholder analysis process?
- Since we're looking at open source software projects, we're dealing with a unique type of stakeholder. Namely, the stakeholders are (mostly) technical rather than lay users of a consumer software product. The examples in the paper seem more targeted at non-techincal users of software platforms.
- Challenge: analyzing a large amount of feedback. In our research, we assert that as the namount of information that needs to be managed increases, the greater the likelihood that project managed bias in favor of highly active members of the stakeholder network.

### Follow on reading
1. V. Dheepa, D.J. Aravindhar, and C. Vijayalakshmi, “A Novel Method for Large Scale Requirement Elicitation,” Int’l J. Eng. and Innovative Technol- ogy, vol. 2, no. 7, 2013, pp. 375–379.
2. W. Maalej, H.-J. Happel, and A. Rashid, “When Users Become Collaborators: Towards Continu- ous and Context-Aware User Input,” Proc. 24th ACM SIGPLAN Conf. Object-Oriented Programming Sys- tems, Languages, and Applications (OOPSLA 09), 2009, pp. 981–990.
3. E.C. Groen, “Crowd Out the Competition: Gaining Market Advantage through Crowd-Based Requirements Engineering,” Proc. 1st Int’l Workshop Crowd-Based Requirements Eng. (CrowdRE 15), 2015, article 3.
Competition: Gaining Market Advantage through Crowd-Based Requirements Engineering,” Proc. 1st Int’l Workshop Crowd-Based Requirements Eng. (CrowdRE 15), 2015,
4. E.C. Groen, J. Doerr, and S. Adam, “Towards Crowd-Based Requirements Engineering: A Re- search Preview,” Requirements En- gineering: Foundation for Software Quality, LNCS 9013, 2015, pp. 247–253.
5. I. Morales-Ramirez, A. Perini, and M. Ceccato, “Towards Supporting the Analysis of Online Discussions in OSS Communities: A Speech- Act Based Approach,” Information Systems Engineering in Complex Environments, Springer, 2014, pp. 215-232.
6. L.V. Galvis Carreño and K. Win- bladh, “Analysis of User Comments: An Approach for Software Require- ments Evolution,” Proc. 35th Int’l Conf. Software Eng. (ICSE 13), 2013, pp. 582-591.
