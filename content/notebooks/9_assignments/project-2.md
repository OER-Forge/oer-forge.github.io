# Project 2 - PDEs, Laplace's Equation, and the Method of Relaxation

**Due 27 Oct 23**

[**Updated Rubric**](./updated_rubric.md)

Project 2 will focus on the topic of partial differential equations, specifically Laplace's equation. For this project, **you will be given a choice to work alone or in a pair**. If you work in a pair, we expect the work to be more in-depth and to explore more aspects of the problem. For example, you should consider one of the extensions listed below to add to your project. If you work alone, we expect the same level of depth as with project 1.

## What do you need to do?

Think about the ways we have explored Laplace's equation in class. We have used separation of variables and the method of relaxation to find the electric potential in rectangular and spherical (azimuthal symmetric) geometries.  This is meant to be an introduction to making your project, so the expectation is that you push these ideas into your own analysis of a problem. 

You can use this project to explore electrostatics, but recall that in various time-independent or steady regimes, Laplace's equation is used to describe _a_ potential. Any curless-vector field can be written as the gradient of a potential function. If the vector has a divergence related to a scalar quantity, then we have a Poisson equation - where that scalar quantity vanishes, we have Laplace's equation. So, you can use this project to explore other physical systems that are described by Laplace's equation. For example,

- [Electrostatics](https://en.wikipedia.org/wiki/Laplace%27s_equation#Electrostatics)
- [Steady-state heat flow](https://en.wikipedia.org/wiki/Heat_equation#Steady-state_heat_equation)
- [Irrotational fluid flow](https://en.wikipedia.org/wiki/Laplace_equation_for_irrotational_flow)

For this second project, we have a list of tasks that you have engaged with in class:

* Describe the physical system and how Laplace's equation can apply.
    - what is it
    - what does it model
    - what assumptions and limitations are baked into it
* Investigate it analytically as best you can
    - Use separation of variables to find a solution
    - Here you might need to deal with tractable but messy integrals, you can use online tools or `sympy` to solve these
    - Take limits to show the solution is reasonable
* Develop a computational investigation to compliment the analytics
    - Set up a relaxation method to solve the problem numerically
    - Compare the numerical solution to the analytical solution
    - Explore the behavior of the numerical solution with different boundary conditions
* Produce visualizations of you work
    - Make graphs that are labeled and titled appropriately for your claims
    - Add mathematics to the notebook is you see fit ($LaTeX$, handwritten, typed are all ok)
* Document your work
    - We should be able to run your notebooks and get exactly what you want us to
    - Comment everything 

## Earning extra credit for more explorations

- Choose a more complicated geometry (e.g. cylindrical, spherical, etc.) and develop a relaxation approach for it
- Explore a higher-dimensional problem (3D)
- Show you can recover the electric field using numerical grid-based differentiation
- Connect your analysis to an experimental set up (a cavity, a heated system, etc)

## Submitting your work

You will upload your work to D2L. It should be a single PDF of your work. If you also write code, please submit the associated files as well. If you do all of this in a Jupyter notebook, please export the notebook as a PDF and submit the notebook and PDF file. If you have any questions, please ask. We want you to enjoy working on these problems.