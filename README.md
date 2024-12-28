# learning-udacity-flying-car

## Demo

### Course 2. Backyard flyer

![image info](./course2/backyard_flyer.gif)

## Setup

### Setup with Anaconda


```powershell
$env:Path += ';D:\Apps\anaconda\condabin'
conda init powershell
powershell -nologo

# cd to FCND-Term1-Starter-Kit directory first
conda env create -f environment.yml
conda info --envs
conda activate fcnd
conda info

# ensure udacidrone was installed
conda list

# Start coding
ipython


# clean up
conda remove --name fcnd --all
```

### Setup with venv

```shell
python3 -m venv ~/.virtualenvs/fcnd

```

## API





## Resources

### General 

* https://www.udacity.com/course/flying-car-nanodegree--nd787
* https://udacity.github.io/udacidrone/docs/getting-started.html
* https://community.udacity.com/


### Refferences throught the course

#### Course 2. Introduction to Autonomous Flight

##### 2.1 Welcome

* https://medium.com/udacity/tagged/flying-cars
* https://dronecode.org/
* https://www.uber.com/us/en/elevate/vision/
  * https://d1nyezh1ys8wfo.cloudfront.net/static/PDFs/Elevate%2BWhitepaper.pdf?uclick_id=0a568618-6d54-4d3e-ae89-e909258a1f03
* https://evtol.news/

* https://www.youtube.com/watch?v=kuNEtnVnTGE
* https://www.youtube.com/watch?v=w6bP7l2o81s
* https://www.youtube.com/watch?v=ZUYHuAa9xfo

##### 2.2 Autonomous Flight

* http://www.quantumdev.com/brushless-motors-vs-brush-motors-whats-the-difference/
* http://www.electronicdesign.com/electromechanical/what-s-difference-between-brush-dc-and-brushless-dc-motors
* https://en.wikipedia.org/wiki/Electronic_speed_control
* RC Basics - Understanding Electronic Speed Controllers (ESC) - https://www.youtube.com/watch?v=OZNxbxL7cdc
* https://drones.stackexchange.com/questions/415/how-does-a-quadcopter-yaw
