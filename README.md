Kolam craft🎨
A web application that uses a rule-based computer vision model to deconstruct and recreate traditional South Indian Kolam art, based on the principles from the academic paper, "The Kolam Drawing: A Point Lattice System."

This project was developed for a hackathon to explore the intersection of artificial intelligence and cultural heritage.

Demo
(Here, you should add a screenshot of your final application showing the three-phase pipeline, like this one:)

Core Concept
Inspired by the research paper from MIT's DesignIssues, the goal was to use AI not just to generate art, but to analyze and understand the foundational, rule-based principles of a 5,000-year-old traditional art form. The model first deconstructs an existing Kolam to identify its core structure (the dot lattice) and then uses that information to generate a step-by-step, animated recreation.

Features
Upload single-stroke Kolam images for analysis.

Identifies the core Point Lattice (dot grid) using a multi-stage computer vision pipeline.

Displays a full visual summary of the analysis process: Isolate Dots -> Detect Dots -> Recreate.

Generates a clean, animated SVG that recreates the art with a single, continuous stroke.

Tech Stack
Language: Python

Frameworks & Libraries:

Flask: Web application server

OpenCV: Computer vision and image processing

NumPy: Numerical operations

svgwrite: SVG generation for the animation

How It Works: The AI Pipeline
The model follows a three-stage methodology:

Deconstruction (The Analyzer): An uploaded image is converted to a high-contrast binary format. A series of morphological operations (Closing and Erosion) isolate the dot features from the lines. A clustering algorithm then processes these features to identify the precise coordinates of the final Point Lattice.

Recreation (The Recreator): The model traces the continuous outline of the original Kolam. This outline is converted into a mathematical SVG path, and CSS animation rules are embedded to render a step-by-step drawing effect.

Presentation (The Frontend): A Flask server displays the full visual summary of the pipeline—the isolated dots, the detected lattice, and the final animated recreation—in a user-friendly web interface.

Future Work
Support for Multi-Stroke Designs: Enhance the model to analyze and recreate more complex Kolams that consist of multiple, separate components.

Advanced Pattern Recognition: Implement a feature-based matching system (e.g., using ORB) to recognize the individual shapes from the "Kolam Alphabet" (Figure 5 of the research paper), even when rotated.

Graph-Based Recreation: Upgrade the Recreator to build a mathematical graph of the Kolam and calculate a true Eulerian path for a more authentic, human-like drawing animation.

Reference
Title: The Kolam Drawing: A Point Lattice System

Author: Anika Sarin

Publication: DesignIssues, Volume 38, Number 3 (Summer 2022)
