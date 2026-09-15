# FCIM.FIA Autumn 2026
## Lab: Expert (hopefully) Systems
**Handed out:** Wednesday, September 2, 2026

### Searching for tourists, expertly

Finally, your dream came true and you have landed a job at "HeinleinAI" the biggest AI company in the whole Luna-City! You're on a testing period so you will want to make sure that you do your best.

While you are daydreaming about free lunch, the mentor comes and hands you your first task: you'll need to build an expert system. They say that while going through the central library database they stumbled upon this ancient approach that looked like it could solve a particular lunar problem: detecting tourists.

The tourists in Luna-City are a big source of income, and while almost every salesman and hotel administrator can easily tell one from a Loonie, our mentor researches a more systematic way of detecting them. While this would prove a trivial task to the city's main computer, resources are scarce these days, and so you will be researching alternative, more specialised approaches.

For starters, research the types of tourists that visit Luna-City and collect a knowledge base of at least 5 tourist types and the criteria by which they can be distinguished from Loonies and between themselves (e.g. clothes, accent, gait, height or opinion on politics). After your knowledge base is done, create a system that would allow the user to answer some questions about a possible tourist. If the set of given answers matches a type of tourist from the knowledge base, this should be the system's answer. If, on the other hand, the system determines that the person in question is a Loonie, the answer should be returned accordingly. Make sure to consider the case when the set of answers does not find a match in the knowledge base (highly improbable if you've done your research well).

Watch out! The Company has a very strict grading policy and guidelines which you should follow! Both of them are described on the next page. If you want to be sure that the company appreciates your work, follow them rigorously.

---

### General Guidelines

* Submit your solution containing `.ipynb` and/or `.py` code files, and a report describing what you have implemented, on ELSE, in the dedicated fields.
* For this laboratory, you can use the provided code from the archive. Alternatively, you can implement your code for the Expert System. Suggested development environments are Google Colab or JupyterLab.
* The suggested report template can be found here. In case you are planning on writing the report in Google Colab, please create a copy on your disk before using it (do not modify the provided document).
* You are allowed to use ANY programming language of your choice.
* Do NOT host your solution in public repositories (e.g. Github etc). You can use private repositories if you need to.
* Plagiarism is NOT tolerated! Abusive usage of LLMs and vibe-coding are treated the same as plagiarism!

---

### Grading Policy

| Task | Description | Points |
| :--- | :--- | :--- |
| **Task 1** | Define at least 5 types of tourists that visit Luna-City. Draw the Goal Tree representing these types of tourists. | 1.0p |
| **Task 2** | Implement the rules from the defined tree in Task 1 in your code (use the `IF`, `AND`, `OR` and `THEN` rules which are already implemented). | 1.0p |
| **Task 3** | If you are using the provided code, check how the Forward Chaining algorithm works and illustrate an example. If you are implementing your own code, implement the Forward Chaining algorithm yourself. | 0.5p |
| **Task 4** | Implement the Backward Chaining algorithm for the Goal Tree. | 2.0p |
| **Task 5** | Implement a system for generating questions from the Goal Tree. Have at least 3 types of questions (e.g. yes/no, multiple choice, etc). | 2.0p |
| **Task 6** | Wrap up everything in an interactive Expert System that will dynamically ask questions based on the input from the user. Both Forward Chaining and Backward Chaining should be working together within the dynamic system you have designed. | 2.0p |
| **Task 7** | Format the output and questions in a human-readable format (they should respect the grammatical rules of the English language). | 0.5p |
| **Report & Presentation** | Clear explanations, report formatting, code quality, comments in the code, docstrings, visualisations if relevant etc. | 1.0p |

---

**Good Luck!**

*The source code and materials were inspired by and adapted from 6.034 Artificial Intelligence Lab 1 MIT OpenCourse Ware http://ocw.mit.edu.*
