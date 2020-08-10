  
# AirUX

  

## Project Brief

Replicate a traditional device (mouse) using SensorTile. Create a new user experience for Human-Computer Interaction (HCI) utilizing motion sensors for gesture commands.

  

Based on the analysis of SensorTile measurements, we reimagined HCI interaction control (mouse moves and clicks) and enabled swipe commands using machine learning (Random Forest classification model). The demo of the implemented gestures could be seen [here](https://www.youtube.com/watch?v=qL_FcSm2bJ4&feature=youtu.be).

  

## Team & Contribution

![Team](https://github.com/mariam-gogia/AirUX/blob/master/images/Team.png)

  

## Tech Stack

Our tech stack consists of three main components: hardware, software, and intelligence.  
  
The hardware control was implemented using C language within the Workbench IDE.

The software and intelligence part of the project was handled exclusively by Python and its libraries such as:

-   PyAutoGUI - cursor control.
    
-   Pandas, NumPy and Matplotlib - data analysis and data visualization.
    
-   Scikit-learn, Tensor-Flow, and Keras - machine learning model development.
    

  
The IDE selection for software and intelligence included Jupyter Notebook, Sublime, and VS Code.

  
##  Hardware

SensorTile, MCU - ST Nucleo Board, Laptops, Peripherals: USB, Miro-USB, Mini-USB.

  

## Set-Up & Overview

  

1. In order to obtain measurements from a sensorTile, a DataLog program provided in [sensor_tile_src/v1.2-3.0](https://github.com/mariam-gogia/AirUX/tree/master/sensor_tile_src/v1.2-3.0) folder needs to be flashed on the device. Given version of the DataLog program obtains measurements of r (magnitude), phi (azimuth), theta (inclination), accelerometer and gyroscope on x, y, and z axes. It is a modified version of STMicroelectronics Sensortile Tutorial 3 which can be found [here](https://drive.google.com/file/d/1Xf-TZg9yErff3C9yOtBsvXd0sC9HHD0M/view).

2. mouse_move.py provided in [src](https://github.com/mariam-gogia/AirUX/tree/master/src) folder is the main driver of the system. It utilizes serial_reader.py to get the measurement readings and issues mouse commands using pyautogui. It also employs the rf_model.sav and process_signal.py to execute gestures that are implemented via machine learning.

  

3. Mouse click and coordination were implemented by analyzing thresholds from sensorTile signals; swipe gestures were implemented by employing machine learning techniques. As these two implementations follow different processes we will review them as Process 1 and Process 2.

  
  

## Process 1 - Implementation of moves & click

## Data Collection

  

sensorTile readings were recorded in five positions.

Recordings are provided in [data](https://github.com/mariam-gogia/AirUX/tree/master/data) folder.

1. Stationary - holding it still horizontally.

2. Tilted Forward (down) 90 degrees.

3. Tilted Up 90 degrees.

4. Tilted Right 90 degrees.

5. Tilted Left 90 degrees.

  

As these movements are the ones we are interested in to move the mouse, we needed to analyze how holding a sensorTile in different positions affects the features (accelerometer, gyroscope, magnitude, azimuth, and inclination).

  

## Data Analysis & Inference

  
Looking at the raw data, it became clear that theta (inclination) is a very accurate measure of sensorTile's spherical position. While holding the device 90 degrees in any direction the measurements unmistakably output a number close to 90 and while holding it in stationary position, it outputs a number close to 0. We observed that sensorTile's directions, as to which side the device is tilted can be determined by looking at the accelerometer measurements. For example, if the device is held tilted left the acceleration on the x axis (A_x) = ~ - 1000, but if the device is held tilted right (A_x) = ~ 1000.

  

![data](https://github.com/mariam-gogia/AirUX/blob/master/images/InputPipeline.png)

  
  

## Implementation of Mouse Moves

Based on the analysis of raw data we determined thresholds for our mouse coordination. We identified the acceleration and inclination thresholds. For example, if the acceleration on an appropriate axis is above 300 and the inclination is more than 25 degrees, move right 10 pixels.

  

Mouse movements are implemented using the following function: **pyautogui.moveRel(x, y)**

This function moves the mouse relative to its location by indicated pixel amounts, which in our case is 10.

  

## Implementation of a Click

Click is implemented by altering the DataLog program flashed on a sensorTile. Using a simple State Machine in a DataLog application we get a flipping gesture recognition.

The State Machine works the following way:

- Hold the sensortile such that A_z < -z_threshold for at least t milliseconds.

- Within next t milliseconds, reorient the sensorTile such that A_z > +z threshold.

  

![stateMachine](https://github.com/mariam-gogia/AirUX/blob/master/images/state_machine.png)

  

Since we need the click to be fast, we made time (t) 3 milliseconds long, which means in order for the click to be recognized a sensorTile needs to be flipped fast.

Once flip is detected by the DataLog program, it outputs a string - "flipped" which is handled in serial_reader.py, a file that handles sensorTile outputs and reads data.

Click is executed by issuing the following command: **pyautogui.click()**

  
  
  

# Process 2 - Implementation of swipes using a machine learning algorithm

  

## Data Labeling

  

- 2 scripts were developed for data labelling: store_data.py and record_data.py. store_data.py records measurements in every 0.01 second and outputs them in a csv file. Using this script, we get the measurements during swipes as well as during sensorTile's stationary position; in this case labelling is not automatic but manual. record_data.py collects measurements during the motion only. It prompts the user to swipe in every 3 seconds and collects just the next 4 frames. The output csv file already includes labels.

- We collected 110 left and 110 right swipes total. The labeled data can be found [here](https://github.com/mariam-gogia/AirUX/tree/master/labeled_data)

  

After obtaining labeled data for each type of swipe, we determined that the swipe consists of 4 frames and all of these 4 frames show the same pattern in its magnitude ( r ) parameter, however, we could not find a feature which would consistently discriminate between left and right swipes. For this reason, we decided to add 'deltas' to our parameters' list. Deltas measure the change of each parameter from its previous reading.

  
  

## Data Visualization & Feature Extraction

  

***Please see [jupyternotebook](https://github.com/mariam-gogia/AirUX/blob/master/jupyter_notebooks/The%20analysis%20of%20features%20and%20models%20for%20swipes.ipynb) for detailed explanations of visualization and ML model exploration process.

  

We visualized the data in various ways in order to observe the relationships between features. Our goal was to identify the correct features to extract for our Machine Learning model.

We observe that 1 swipe corresponds to 4 data frames, in other words, each four rows of our data represents one swipe. We manipulated the data by compressing these 4 frames into one. This was done by taking, mean, standard deviation, maximum and minimum points of certain features of each four row of the data. At the end, we took the manipulated data and fed it to different ML models to determine the best model type for our problem. The analysis of effectiveness of different ML models was done by using logarithmic loss coefficients.

  

The results are displayed below:

![logloss](https://github.com/mariam-gogia/AirUX/blob/master/images/log_loss.png)

  
It was obvious that the issue is coming from the data. We decided to aggregate and shuffle all the data. Then conduct detailed feature analysis by comparing change between certain action (swipe left/right) and no action, as well as between actions (swipe right vs swipe left). Then remove the least correlated features, focusing on fewer features. We ended up using acceleration modified features as such as acceleration X standard deviation, acceleration X mean, acceleration X max mean, and so on repeating it for all axes. It was done becasue due to limited sample size overexecisive features representations noises model, in this case the less the better. 
  

## Model Implementation

The final model predicts swipe gesture with ~90% accuracy. That's what we ended using in our real-time model integration. 
There are many improvements that we can implement moving forward, including feature-selection automation, which will allows us to select features automatically based on model prediction accuracy. One of the things we discovered that certain axes of certain parameters have higher correlation with the movement than others. There are oppportunities to utilize hybrid measurement units to gain higher accuracy. 

![Team](https://github.com/mariam-gogia/AirUX/blob/master/images/model.png)

More details about the model can be found here: [model](https://github.com/mariam-gogia/AirUX/blob/master/jupyter_notebooks/air_gesture_model.ipynb)
    

## Slides & Demo Video
See demo video [here](https://www.youtube.com/watch?v=qL_FcSm2bJ4&feature=youtu.be)

See presentation [here](https://docs.google.com/presentation/d/1nJDLNLOWU7jkE5T9yonzKxsSi_w1LN9vJsfU9uoG6Ak/edit)
