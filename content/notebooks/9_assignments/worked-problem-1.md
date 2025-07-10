# Worked Problem Assignment 1

**Due 15 Sep 23**

In this first few class periods, we have discussed formulating mechanics using Lagrangian Dynamics to produce equations of motion and how we can use numerical integration to solve for trajectories.

[**Grading Rubric**](../0_course/8_worked_problems.md)

Remember that a worked problem means the scale of a detailed (e.g., parts a-h) homework problem.

## Places to find candidate problems:
- Classical mechanics textbooks; look at the problems in the Lagrangian chapters
-  Differential equations textbooks; look at ODEs that represent real systems
-  Wikipedia has lists of named differential equations and problems
    - [List of named Diffy Qs](https://en.wikipedia.org/wiki/List_of_named_differential_equations)
	- [List of nonlinear differential equations](https://en.wikipedia.org/wiki/List_of_nonlinear_ordinary_differential_equations)
    - Ask on Slack 

## Developing Equations of Motion

Remember that the process we have developed is:
1. Identify problem and motivate assumptions
2. Develop a Lagrangian using relevant general coordinates
3. Use the Euler-Lagrange equations to produce equations of motion

This "pipeline" is really how we formulate a mechanics problem into something we can do mathematics with. In this assignment, you will develop your own Lagrangian for a system and solve for the equations of motion. 

## Investigating the System

After we produce our equations of motion, we used both approximation techniques and numerical techniques to find solutions to the equations of motion. Here we developed "trajectories" for the system, that is, how the system evolves in time. In the approximate cases, we often sought frequencies of small oscillations to say something about how the system behaves near stable equilibria. In the numerical cases, we could choose particular initial conditions and see how they evolved in time.

In this assignment, you will take your equations of motion and solve them numerically to produce trajectories. Approximate solutions, where you look into equilibria and frequencies of oscillation, should be included as well.

## Assignment

1. Choose a mechanical (or dynamical) system with two degrees of freedom (e.g., $x$ and $\dot{x}$). This could be a system you have already worked with, or something new.
2. Develop a Lagrangian for the system. You may need to make some assumptions to simplify the problem. You may also need to introduce some new variables to make the problem work. Make sure that is explained.
3. Use the Euler-Lagrange equations to produce the equations of motion for the system.
4. Solve the equations of motion numerically to produce trajectories for the system. You should include at least two different initial conditions.
5. Use the approximate techniques we have discussed to find frequencies of oscillation and stable equilibria. Compare these to the numerical results.

## Looking ahead (earn extra credit)

If you are looking into these systems and finding them interesting here's two things you can do to earn extra credit that we will discuss later in the course.

1. Develop a phase space diagram for your system to show what families of solutions exist.
2. Investigate the stability of the equilibria that you find.

## Submitting your work

You will upload your work to D2L. It should be a single PDF of your work. If you also write code, please submit the associated files as well. If you do all of this in a Jupyter notebook, please export the notebook as a PDF and submit the notebook and PDF file. If you have any questions, please ask. We want you to enjoy working on these problems.