# Software Engineering for Data Science

Instructor: Nick Ross 

Office Hours: I am on campus most days of the week and will have office hours right after class. However, the best way to get help is by emailing.

Office Location: Ryerson 257H

How to contact: My contact information is on Canvas.

## Course Description

This course is designed to equip students with the practical skills and theoretical knowledge necessary to excel at the intersection of data science and software engineering. Through a hands-on approach, students will delve into the core tools and concepts that form the backbone of this interdisciplinary field, including data modeling, building data pipelines, and software development best practices. Emphasis will be placed on real-world applications, enabling students to work on projects that simulate professional scenarios and challenges. This course is ideal for those looking to deepen their understanding of how data-focused technologies are developed and deployed.

## Prerequisites

This course assumes that you are familiar with the basic concepts of Python programming as you would find in the core data science courses. 

If you are unsure or are looking for a refresher on what is expected, please take a look at this [prerequisite doc](./docs/prerequisites.md).

## Course Overview

This course is designed to expose data science students to deeper computing concepts that are likely needed throughout their careers. We will do this in a project-based approach where students will work in small groups using common data science tools to build an entire pipeline from raw data to putting the data into a relational database to serving that data through an API. We will then layer on an MCP Server so that we can access our API using tools like ChatGPT, Claude and agentic frameworks.

As a by-product of this effort, after taking this course, students should have experience managing their own computing environment and be able to build software with an understanding of best practices. 

## Course Assessment

The final grade of this course will be determined by five components:

| Component | Percent of Grade | 
| --- | --- | 
| Professionalism (Ind.) | 5\% | 
| Project (Group) | 30\% | 
| Quizzes (Ind.) | 30\% | 
| Final Project Deliverable (Group) | 15\% | 
| Final Exam (Ind.) | 20\% | 

Note that you can find historical examples of all assignments on the [previous year's Github page](https://github.com/NickRoss/2024-Data-24100). Keep in mind that much has changed, but this is a good starting point. From last year I know which quizzes, exams and issues were too difficult as well as too easy and have adjusted accordingly. The material itself is also updated (assignments, notes, etc.)

### Professionalism (Ind.)

In this class professionalism means:

- Showing up on time
- Showing up prepared
- Contributing to class
- Being responsible to your group when doing group work
- Communicating respectfully and appropriately to your peers, TAs and faculty

Students who show up on time and pay attention in class have a tendency to do extremely well in this class. The opposite is also true; students who fail to make an effort, fail to contribute in class, and fail to pay attention have a tendency to do poorly in this class. 

This grade is assigned individually.

### Project (Group)

Over the course of the quarter you and your group will be working on a large software engineering project. This project will have multiple deliverables during the quarter that you will need to complete as we build up to our final API and backend.

This grade is assigned as a group. You can find the project's grading and late policy [here](./assignments/regrade_policy.md). Please read before asking for a regrade.


### Quizzes (Ind.)

Each Wednesday (starting week \#2) there will be a short quiz (15–30 minutes) given at the start of the class. These quizzes are _cumulative_ over the course of the quarter. Note that the lowest quiz grade will be dropped at the end.

More information on the quizzes is provided in the [course material](#course-material) section below.

This grade is assigned individually. You can find the quiz regrade policy [here](./assignments/regrade_policy.md). Please read before asking for a regrade.


### Final Project Deliverable (Group)

At the end of the quarter your group's final GitHub repository will undergo a significant assessment to make sure that it meets the criteria established during the course. 

This grade is assigned as a group.

### Final Exam (Ind.)

There will be a final exam given according to the exam calendar. This will be cumulative from the material in the quarter and will be similar in style and difficulty to the quizzes. The final will be held per the [final exam calendar](https://registrar.uchicago.edu/calendars/final-exams/) and be held in person.  Please make sure that you verify your availability.

This grade is assigned individually. There is more information about the final [here](./lesson_plan/finals_week.md).

## Expectations (How to work with me)

We are all busy people and to help get everyone on the same page this section contains a bit of expectations and how to get the most out of this course.

#### Material / Philosophy

The material in this course is chosen based on my experience working with data scientists in both academic and industry settings. 

I believe that Data Science is a vocational practice and that getting fingers to the keys repetitions and experience with the most common technologies is the number one way to improve outcomes (career, job interviews, etc.).

I believe that AI/LLM tools are incredibly powerful and useful. They could probably get an ``A" in this course. 

I believe also that AI/LLMs are ``tools" used most effectively by people with a baseline knowledge level. Most of this course is focused on the baseline knowledge required to use these tools effectively.

A _LOT_ of the material in this course was taken based off of common issues that I see when interviewing candidates for data science and data engineering roles. This is especially true for systems and tools around working collaboratively (github, code writing, abstractions, etc. ). 

#### Communications

Canvas is the single most important place to be for information on this course. All announcements will be made via Canvas. 

When communicating with me, email is the best way to reach me. A few notes:

- I have spent a lot of time putting together information on this github page. If you ask me information that can be found here it makes me grumpy. Don't be lazy and look before you ask. If I send you a screenshot of information from the course website it is _not_ a good sign and may affect your professionalism score. 
- If you wish to ask a question about the group project, _include everyone on the project on the email_. I will not answer questions about the project that do not include your entire team.
  - The purpose of group work is to _work as a group_. The data science curriculum at UChicago is diverse and there may be a class or experience that someone in your group has which can help.
  - This not to say that I won't help, but scheduling time to meet with me when your teammates are able to assist more quickly will lead to more efficient learning outcomes.

- During class, please ask questions! 

#### Respect

I do not tolerate disrespectful or unprofessional behavior. One of my values is ``Respectful Disagreement". It is okay for us to disagree, but we will do so respectfully.

This is universal: when working with your teams, the TAs, etc. 

#### Transparency

As you will see in the next section, there is nothing hidden in this course. My goal when designing courses is to make _the material_ difficult, not the logistics and organization of the course. 

If there is anything missing from the material or something that you are not sure of in my class notes -- let me know! I always want to improve these notes.

## Course Material

Lectures will be traditional chalk-talks and computer-aided demonstrations. While there aren't slides, my lecture notes will be provided in this repository for reference.

These notes represent the content of the course and what is expected to be covered on the quiz. I strongly recommend students attend the lecture for the full experience. 

During lecture we will be doing some hands-on activities and verifications that, while described in the notes, are better experienced in-person rather than via the notes.

### Quiz Material

After each lecture (roughly) the lecture notes will be provided. Appended to the end of the lecture notes will be a set of quiz objectives that describe the material that can appear on the quiz. 

These quiz objectives _do not_ cover all of the material from the lecture but are the only material that will be asked for on the quiz.

That being said, it is important to internalize these concepts because, while the list of learning objectives at the end describe the basic building blocks of what is asked, they may be combined into a single quiz question.

For example: Consider two quiz objectives of `use wildcards to match files which follow a pattern` and another  `move files within a file system`. It is perfectly reasonable to ask a question on the quiz such as `move all .txt files from the /data subdirectory to the /text_data subdirectory` which would require using both. 

## Course Outline

In this course we will cover the following topics which will enable us to build a full data pipeline, diagnose issues, and serve data via an API. Each topic will last approximately a week.

Course Notes can be found linked inside each lesson plan.

| Topic | Topics | Assignments | Notes \& Plan | 
| --- | --- | --- | --- | 
| 1: Introduction | <ul><li>The Terminal</li><li>File Management</li><li>Environments</li></ul> | <ul><li>[Software Preliminaries](./assignments/prelims.md)</li><li>[Prerequisites](./docs/prerequisites.md)</li></ul> | <ul><li>[Lesson Plan](./lesson_plan/week_1.md)</li></ul>
| 2: Docker, Make and Git | <ul><li>Docker</li><li>Make</li><li>Git</li><li>Environments</li></ul> | <ul><li>[Project Part 0 Due](./project_assignments/part_0.md)</li><li>[Quiz 1A](./quiz/quiz1A.pdf)/[Quiz 1B](./quiz/quiz1B.pdf)</li><li>[Answer Key](./quiz/quiz1AK.md)</li></ul> | <ul><li>[Lesson Plan](./lesson_plan/week_2.md)</li></ul> |
| 3: Flask | <ul><li>Flask</li><li>Requests</li></ul> | <ul><li>[Project Part 1 Due](./project_assignments/part_1.md)</li><li>[Quiz 2A](./quiz/quiz2A.pdf)/[Quiz 2B](./quiz/quiz2B.pdf)</li><li>[Answer Key](./quiz/quiz2AK.md)</li></ul>  | <ul><li>[Lesson Plan](./lesson_plan/week_3.md)</li></ul> |
| 4: Flask & Code Quality | <ul><li>Advanced Requests</li><li>Organizing code</li><li>DRY</li><li>Separation of Concerns</li></ul> | <ul><li>[Project Part 2 Due](./project_assignments/part_2.md)</li><li>[Quiz 3A](./quiz/quiz3A.pdf)</li><li>[Answer Key](./quiz/quiz3AK.md)</li></ul>  | <ul><li>[Lesson Plan](./lesson_plan/week_4.md)</li></ul> |
| 5: SQLite & Management Commands | <ul><li>SQLite</li><li>Management Commands</li><li>CRUD</li><li>POST Requests</li></ul> | <ul><li>[Project Part 3 Due](./project_assignments/part_3.md)</li><li>[Quiz 4A](./quiz/quiz4A.pdf)/[Quiz 4B](./quiz/quiz4B.pdf)</li><li>[Answer Key](./quiz/quiz4AK.md)</li></ul>  | <ul><li>[Lesson Plan](./lesson_plan/week_5.md)</li></ul> |
| 6: Static Analysis, CRUD & Logging | <ul><li>Static Analysis</li><li>Ruff & Pre-commit</li><li>More CRUD</li><li>Logging</li></ul> | <ul><li>[Project Part 4 Due](./project_assignments/part_4.md)</li><li>[Quiz 5A](./quiz/quiz5A.pdf)</li><li>[Answer Key](./quiz/quiz5AK.md)</li></ul>  | <ul><li>[Lesson Plan](./lesson_plan/week_6.md)</li></ul> |
| 7: Adding Features | <ul><li>Logging in Python</li><li>Autodocs with MkDocs</li></ul> | <ul><li>[Project Part 5 Due](./project_assignments/part_5.md)</li><li>[Quiz 6A](./quiz/quiz6A.pdf)</li><li>[Answer Key](./quiz/quiz6AK.md)</li></ul>  | <ul><li>[Lesson Plan](./lesson_plan/week_7.md)</li></ul> |
| 8: MCP | <ul><li>MCP</li></ul> | <ul><li>[Project Part 7 Due](./project_assignments/part_7.md)</li><li>Quiz \#7</li></ul>  | <ul><li>[Lesson Plan](./lesson_plan/week_8.md)</li></ul> |
| 9: MCP (cont.) and Testing | <ul><li>MCP</li><li>Testing</li></ul> | <ul><li>Project Part VII</li><li>Quiz \#8</li></ul>  | |
| 10: Finals Week |  | <ul><li>Final Project Assignment</li><li>In person Final</li></ul>  | |

## Canvas

All grades (and due dates) will be posted on Canvas. If you do not have access to Canvas, please send me an email as soon as possible. 

## Odds and Ends

- **Cheating is not tolerated. At all.** Unless an assignment is clearly designated as group work, I expect it to be done alone. The University's code of academic integrity can be found online, and I expect it to be followed. Disciplinary action will be taken against any student found violating this code. This includes:
  - **Plagiarism** — intentionally or unintentionally representing the words or ideas of another person as your own; failure to properly cite references; manufacturing references.
  - Working with another person when independent work is required.
  - Submission of the same paper in more than one course without the specific permission of each instructor.
  - Submitting a paper written by another person or obtained from the internet.
  - The penalties for violation of the policy may include a failing grade on the assignment, a failing grade in the course, and/or a referral to the Academic Integrity Committee.

- **Attendance is expected.** All exams are in-person and use pencil and paper.

- The quickest way to reach me is via email.

- **Class participation is expected.**

- **Accommodations:** If you require any accommodations for this course, as soon as possible please provide the instructor with a copy of your Accommodation Determination Letter (provided to you by the Student Disability Services office) so that you may discuss with them how your accommodations may be implemented in this course. The University of Chicago is committed to ensuring the full participation of all students in its programs. If you have a documented disability (or think you may have a disability) and, as a result, need a reasonable accommodation to participate in class, complete course requirements, or benefit from the University's programs or services, you are encouraged to contact Student Disability Services as soon as possible. To receive reasonable accommodation, you must be appropriately registered with Student Disability Services. Please contact the office at (773) 702-6000, TTY (773) 795-1186, disabilities@uchicago.edu, or visit the website at [disabilities.uchicago.edu](https://disabilities.uchicago.edu). Student Disability Services is located at 5501 S. Ellis Avenue.

- As an instructor, one of my responsibilities is to help create a safe learning environment on our campus. I also have a mandatory reporting responsibility related to my role as a faculty member. I am required to share information regarding sexual misconduct or information about a crime that may have occurred with the University.

- The University of Chicago is a community of scholars dedicated to research, academic excellence, and the pursuit and cultivation of learning. Members of the University community cannot thrive unless each is accepted as an autonomous individual and is treated without regard to characteristics irrelevant to participation in the life of the University. Our university is committed to fostering a safe, productive learning environment. Title IX and our school policy prohibits discrimination on the basis of sex. Sexual misconduct — including harassment, domestic and dating violence, sexual assault, and stalking — is also prohibited at our university.

- Our university encourages anyone experiencing sexual misconduct to talk to someone about what happened, so they can get the support they need and our university can respond appropriately. If you wish to speak confidentially about an incident of sexual misconduct, want more information about filing a report, or have questions about school policies and procedures, please contact Bridget Collier (Associate Provost for Equal Opportunity Programs and Title IX Coordinator for the University) at [bcollier@uchicago.edu](mailto:bcollier@uchicago.edu) or (773) 834-6367.

- Our university is legally obligated to investigate reports of sexual misconduct, and therefore it cannot guarantee the confidentiality of a report, but it will consider a request for confidentiality and respect it to the extent possible. As instructors, we are also required by our school to report incidents of sexual misconduct and thus cannot guarantee confidentiality. We must provide our Title IX coordinator with relevant details such as the names of those involved in the incident.
