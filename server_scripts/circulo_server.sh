# Circulo server instructions!
# This script should help with setting up a clean server instance with Circulo

#Currently it requries root access

###
# Requirements before you run this script:
# git
# virtualenv
# virtualenvwrapper
# python3
# pip3
###


if [ "$#" -ne 1 ]; then
        echo "Please provide remote for Circulo Git repo"
        exit 0
fi

CIRCULO_GIT_LOC = $1


# create virtual environment folder and set the proper permissions
cd /home
sudo mkdir .venvs
sudo chgrp -R admin .venvs/
sudo chmod -R 770 .venvs/

# create circulo folder
sudo mkdir circulo
sudo chgrp -R admin circulo/
sudo chmod -R 770 circulo/
echo "created circulo folder"

# set up virtualenv. Requires virtualenvwrapper
cd circulo
export WORKON_HOME='/home/.venvs'
source '/usr/local/bin/virtualenvwrapper.sh'
mkvirtualenv --python=`which python3` circulo
deactivate

# adding a couple minor files for convenience
echo "export WORKON_HOME='/home/.venvs' 
source '/usr/local/bin/virtualenvwrapper.sh' 
workon circulo" > setup

echo "Circulo

To work on circulo on this virtualenv, run

    source setup

Your prompt should start with (circulo) if it worked correctly.

To exit the virtualenv, run

    deactivate


If you need to add new packages to the virtualenv, pip3 should work\
 as expected as long as you are within the virtualenv. However, you may\
  have to install unexpected dependencies that this OS didn't ship with.
" > README

# get circulo!
git clone $CIRCULO_GIT_LOC

# start using the circulo virtualenv
source setup

# add paths to virtualenv
add2virtualenv /home/circulo/ /home/circulo/Circulo/ /home/circulo/Circulo/circulo/

# install dependencies for circulo's dependencies 
# (you may have to add more, depending on your machine
sudo apt-get install gfortran libopenblas-dev liblapack-dev # for scipy
sudo apt-get install libpng12-dev libfreetype6-dev # for matplotlib

# install igraph
pip3 install python-igraph

# install circulo's dependencies
pip3 install numpy
pip3 install scipy
pip3 install matplotlib
pip3 install scikit-learn


# finally, to use circulo, just cd into /home/circulo and run
#     source setup
# if your prompt begins with (circulo), you're ready to go.
