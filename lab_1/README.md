Fundamentele Inteligentei Artificiale Course

Lab1: Expert (hopefully) Systems

Raw version, improve later


Task 1

I read that we could switch the topic so i decided to do Flags because there is many of them so that means there are some which share none, some and a lot of features

I choose {specify the countries}, because all of the have crosses and different types of them so i thought it would help me have the 3rd type of question (besides tes/no, select one, to have a select many attributes of the cross).

I grouped them in several classes stating what they have in common all then creating a new class, this way i created the goal tree, then i was checking for new ways to describe a flag and got the OR nodes

{show report_related/forward checking}
![alt text](report_related/forward_checking.drawio.png)
Task 3

(below i forgot to use english please translate)

Am introdus regulile mele si le-am testat cu 

python test_task_2.py

cu acest parametru

#Sweden
FLAG_DATA = (
     'flag is bicolor',
     'flag is off-center cross',
     'flag is yellow cross'
 )
 

 mi-a dat raspunsul corect

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

{show report_related/forward checking illustration}
![alt text](<report_related/forward checking illustration.drawio.png>)

task 4

i implemented the BC

here are example outputs

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

Task 5:

Questions:
  Question 1
    Path 1
      1a. How many colors the flag has (2, 3, >4 - leads to unknown flag)
    Path 2
      1b. Is flag bicolor (y/ n - leads to 1c)
      1c. Is flag tricolor (y/n - still no, unknown)
      
  Question 2
  2. does the flag have a cross (y, n -> unkown flag)

  Question 3
  3. Does the flag have stripes (y/n)

  Question 4
    Path 1
      4a. What is the color of the cross (red, blue, yellow, white, other - unknown flag)
    Path 2
      4b-4e. ask red if no, then ask blue, if no ask yellow, if no ask white, if no unknown


  Questions 5-7
    Path 1
      Question 5
        Path 1
          5a. Where is the cross positioned (in the center, off-centered)
        Path 2
          5b. Is the cross centered? (y, n - means its not-centered)

      Question 6
      Path 1
        6a. Is the cross big or small?
      Path 2
        6b. Is the cross big (y, n - means its small)

      Qusetion 7
      7. does the cross have an outline (yes/no)

    Path 2 (multiple choice) 
      Check the box for which describe your cross: big, outlined, centered

      big, outlined, centered -> not existing
      big, outlined, not centered -> yes (example: nor, ice)
      big, not outlined, centered -> not existing
      big, not outlined, not centered -> yes (example: swe, fin)
      
      not big, outlined, centered -> not existing
      not big, outlined, not centered -> not existing
      not big, not outlined, centered -> yes (example: switzerland)
      not big, not outlined, not centered -> yes (example: greece)

