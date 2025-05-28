---
layout: home
permalink: index.html

# Please update this with your repository name and title
repository-name: eYY-4yp-Machine-Learning-Based-Automated-PAR-Index-Calculation-for-Orthodontic-Treatment
title: Machine-Learning-Based-Automated-PAR-Index-Calculation-for-Orthodontic-Treatment
---

[comment]: # "This is the standard layout for the project, but you can clean this and use your own template"

# Machine-Learning-Based-Automated-PAR-Index-Calculation-for-Orthodontic-Treatment

#### Team

- E/19/006, Dhinushika Abrew, [email](mailto:e19006@eng.pdn.ac.lk)
- E/19/017, Sajani Amanda, [email](mailto:e19017@eng.pdn.ac.lk)
- E/19/240, Shenal Mendis, [email](mailto:e19240@eng.pdn.ac.lk)

#### Supervisors

- Dr. Asitha Bandaranayake, [email](mailto:asithab@eng.pdn.ac.lk)
- Dr. H.S.K. Ratnatilake, [email](mailto:ksandamala2002@dental.pdn.ac.lk)

#### Table of content

1. [Abstract](#abstract)
2. [Related works](#related-works)
3. [Methodology](#methodology)
4. [Experiment Setup and Implementation](#experiment-setup-and-implementation)
5. [Results and Analysis](#results-and-analysis)
6. [Conclusion](#conclusion)
7. [Publications](#publications)
8. [Links](#links)

---

<!-- 
DELETE THIS SAMPLE before publishing to GitHub Pages !!!
This is a sample image, to show how to add images to your page. To learn more options, please refer [this](https://projects.ce.pdn.ac.lk/docs/faq/how-to-add-an-image/)
![Sample Image](./images/sample.png) 
-->


## Abstract

This project proposes a machine-learning-based solution to automate the Peer Assessment Rating (PAR) Index calculation, a key metric used in orthodontics to assess malocclusion and treatment outcomes. Traditional manual methods are time-consuming and subjective. Leveraging deep learning and 3D visualization technologies, our system detects dental landmarks on 3D models and computes the PAR score automatically. The aim is to enhance accuracy, consistency, and accessibility through a cloud-deployed web application, supporting both clinical practice and education.

## Related works

Existing research has explored manual and semi-automated PAR scoring tools, deep learning methods for dental landmark detection, and cost-effective digital orthodontic solutions. Tools like CHaRNet and Ortho Analyzer have shown promise in landmark localization and treatment analysis. However, gaps remain in affordability, user interaction, and real-time performance—particularly in integrating automated scoring with interactive 3D environments for practitioners.

## Methodology

**Data Collection**

Obtain .PLY/.STL dental models from clinics and public datasets.

**Annotation** <br>

Manually label landmarks with expert supervision for training data.

**ML Model Development** <br>

Train landmark detection models using architectures like PointNet and CHaRNet.

**PAR Index Calculation** <br>

Automate scoring based on landmark positions, using weighted metrics.

**Web Application** <br>

Build an interface using React (frontend) and Spring Boot (backend), with AWS deployment.

**User Interaction** <br>

Orthodontists can verify and adjust suggested landmark placements, creating a feedback loop to improve the model.

## Experiment Setup and Implementation

**Environment** <br>

AWS Free Tier (Amplify, Lambda, S3, RDS), local machines for development.

**3D Rendering** <br>

Three.js used for interactive display of dental models in the browser.

**ML Training** <br>

Initial model trained on annotated datasets; evaluated using metrics like MAE, RMSE, and Euclidean Distance Error.

**Model Used** <br>

CHaRNet with a point cloud encoder-decoder and conditioned heatmap regression for robust landmark detection.

**Backend** <br>

Spring Boot APIs for processing and scoring.

**Frontend** <br>

React + Three.js for model upload, landmark editing, and visualization of results.

## Results and Analysis

**Accuracy** <br>

The model achieved <1 mm mean Euclidean distance error for most landmarks.

**Efficiency** <br>

Automated scoring reduced evaluation time by 50–70% compared to manual methods.

**User Feedback** <br>

Early testing showed high acceptance of AI-suggested points, especially by novice users.

**Validation** <br>

Cross-checked with expert-annotated ground truth using statistical reliability tests.

## Conclusion

The integration of ML and 3D modeling has made PAR Index evaluation more efficient, accurate, and accessible. Our system supports faster orthodontic assessments while maintaining expert-level reliability. Future work includes dataset expansion, model optimization for real-time inference, and enhanced UI for broader adoption in clinics and dental schools.

## Publications
[//]: # "Note: Uncomment each once you uploaded the files to the repository"

<!-- 1. [Semester 7 report](./) -->
<!-- 2. [Semester 7 slides](./) -->
<!-- 3. [Semester 8 report](./) -->
<!-- 4. [Semester 8 slides](./) -->
<!-- 5. Author 1, Author 2 and Author 3 "Research paper title" (2021). [PDF](./). -->


## Links

[//]: # ( NOTE: EDIT THIS LINKS WITH YOUR REPO DETAILS )

- [Project Repository](https://github.com/cepdnaclk/e19-4yp-Machine-Learning-Based-Automated-PAR-Index-Calculation-for-Orthodontic-Treatment)
- [Project Page](https://cepdnaclk.github.io/e19-4yp-Machine-Learning-Based-Automated-PAR-Index-Calculation-for-Orthodontic-Treatment)
- [Department of Computer Engineering](http://www.ce.pdn.ac.lk/)
- [University of Peradeniya](https://eng.pdn.ac.lk/)

[//]: # "Please refer this to learn more about Markdown syntax"
[//]: # "https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet"
