# Fundamentele Inteligentei Artificiale Course

## Lab 1: Expert Systems


## Task 1

I chose the flag domain because it contains many examples with both shared and distinct features, which makes it suitable for an expert-system approach.

I selected a set of countries whose flags all contain crosses, but with different variations. This helped me include a third type of question in addition to yes/no and single-choice questions, namely a question that allows selecting multiple attributes of the cross.

I organized the flags into several classes based on their common properties and then combined those classes into a goal tree. While refining the descriptions of the flags, I also identified the OR nodes in the tree.

{show report_related/forward checking}

![alt text](report_related/forward_checking.drawio.png)

## Task 3

I implemented and tested the rules with:

```bash
python test_task_2.py
```

using the following data set:

```python
# Sweden
FLAG_DATA = (
     'flag is bicolor',
     'flag is off-center cross',
     'flag is yellow cross'
 )
```

This produced the correct result.

```text
Rule: IF(OR('(?x) is small cross', '(?x) is off-center cross'), THEN('(?x) is small cross or off-center cross'))
Added: flag is small cross or off-center cross
Rule: IF(OR('(?x) is big cross and not outlined cross', '(?x) is bicolor'), THEN('(?x) is big cross and not outlined cross or bicolor'))
Added: flag is big cross and not outlined cross or bicolor
Rule: IF(AND('(?x) is big cross and not outlined cross or bicolor', '(?x) is off-center cross'), THEN('(?x) is big cross and not outlined cross or bicolor and off-center cross'))
Added: flag is big cross and not outlined cross or bicolor and off-center cross
Rule: IF(AND('(?x) is big cross and not outlined cross or bicolor and off-center cross', '(?x) is yellow cross'), THEN('(?x) is Sweden'))
Added: flag is Sweden

--- Final Inferred Facts ---
flag is Sweden
flag is bicolor
flag is big cross and not outlined cross or bicolor
flag is big cross and not outlined cross or bicolor and off-center cross
flag is off-center cross
flag is small cross or off-center cross
flag is yellow cross
```

{show report_related/forward checking illustration}

![alt text](<report_related/forward checking illustration.drawio.png>)

## Task 4

I implemented backward chaining.

Example outputs:

```text
--- Resulting Goal Tree for flag is Greece ---
OR:
  AND:
    - flag is small cross
    - flag is bicolor
    - flag is off-center cross
  AND:
    OR:
      - flag is small cross
      - flag is off-center cross
    - flag has stripes
```

```text
--- Resulting Goal Tree for flag is Iceland ---
AND:
  OR:
    AND:
      - flag is outlined cross
      - flag is big cross
    - flag is tricolor
  - flag is off-center cross
  - flag is red cross
```

## Task 5

```text
Questions:
  Question 1
    Path 1
      1a. How many colors does the flag have (2, 3, >4 - leads to unknown flag)
    Path 2
      1b. Is the flag bicolor (y/n - leads to 1c)
      1c. Is the flag tricolor (y/n - still no, unknown)

  Question 2
  2. Does the flag have a cross (y/n -> unknown flag)

  Question 3
  3. Does the flag have stripes (y/n)

  Question 4
    Path 1
      4a. What is the color of the cross (red, blue, yellow, white, other - unknown flag)
    Path 2
      4b-4e. Ask red first; if no, ask blue; if no, ask yellow; if no, ask white; otherwise unknown


  Questions 5-7
    Path 1
      Question 5
        Path 1
          5a. Where is the cross positioned (centered, off-centered)
        Path 2
          5b. Is the cross centered? (y/n - means it is not centered)

      Question 6
      Path 1
        6a. Is the cross big or small?
      Path 2
        6b. Is the cross big (y/n - means it is small)

      Question 7
      7. Does the cross have an outline (y/n)

    Path 2 (multiple choice)
      Check the box that describes the cross: big, outlined, centered

      big, outlined, centered -> not existing
      big, outlined, not centered -> yes (example: Norway, Iceland)
      big, not outlined, centered -> not existing
      big, not outlined, not centered -> yes (example: Sweden, Finland)

      not big, outlined, centered -> not existing
      not big, outlined, not centered -> not existing
      not big, not outlined, centered -> yes (example: Switzerland)
      not big, not outlined, not centered -> yes (example: Greece)
```

## Task 6

```text
Welcome to the Flag Expert System!

Does the flag have a cross on it?
(y/n): y
Is the cross centered on the flag?
(y/n): n
Is the cross big?
(y/n): y
How many colors does the flag have?
Enter a natural number greater than 0: 2
What color is the cross?
  1. Red
  2. Blue
  3. Yellow
  4. White
  5. Other
Choose 1-5: 3

Based on your answers, this flag is Sweden.
```