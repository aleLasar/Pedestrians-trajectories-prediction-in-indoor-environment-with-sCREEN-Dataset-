# Prediction of pedestrian trajectories in indoor environment
## Master's degree thesis project

The ability to predict the behavior of people in crowded environments is fundamental in many applications such as video surveillance, autonomous driving or automatic perception of the scene. Prediction is a research field extensively studied in various fields of artificial intelligence and over the years different types of algorithms have been proposed that differ not only from the methodology used, but also from the type of data used.

Mainly the scientific community has focused on predicting the trajectories of pedestrians or moving objects in open scenarios, such as streets or squares. However, with the emergence of new applications, both in the domestic and industrial environment, such as the use of autonomous robots to clean the house or move goods, attention has also been drawn to prediction in smaller spaces, with a potentially greater number of obstacles.

The goal of this thesis work is to explore the use of the sCREEN dataset, created in an indoor environment, to predict future positions. The first part analyzes the dataset, which contains data on the positions of the shopping trolleys used by the customers of a German supermarket, and which interpolation and clustering methods have been proposed to extract the most significant and non-redundant trajectories.
In the second part I show the models, also based on Deep Learning, to predict future positions at fixed time instants using the initial part of the trajectory under observation as input. Finally, an analysis of various evaluation protocols suitable for this type of forecast is proposed.
