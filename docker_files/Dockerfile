FROM tethysplatform/tethys-core:4.0.0

#########
# SETUP #
#########

# # Speed up APT installs
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
 && echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache \
 && echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/no-check-valid

# # Install APT Package
RUN apt-get clean && apt-get update --allow-releaseinfo-change -qq && apt-get -yqq install apt-utils gcc libgdal-dev g++ libhdf5-dev > /dev/null

# # Quiet pip installs
RUN mkdir -p $HOME/.config/pip && echo "[global]\nquiet = True" > $HOME/.config/pip/pip.conf

# # Clone repository
RUN mkdir ${TETHYS_HOME}/tethys_apps && cd ${TETHYS_HOME}/tethys_apps && git clone https://github.com/BYU-Hydroinformatics/tethys_nasaaccess.git

RUN mkdir -p ${TETHYS_PERSIST}/keys
# ###########
# # INSTALL #
# ###########

# install mamba much better than conda ##

RUN ${CONDA_HOME}/envs/tethys/bin/conda install -n base -c conda-forge mamba

RUN ${CONDA_HOME}/envs/tethys/bin/mamba install --yes -c conda-forge r-base


# install requirements with mamba ##
RUN /bin/bash -c "cd ${TETHYS_HOME}/tethys_apps/tethys_nasaaccess \
  ;${CONDA_HOME}/envs/tethys/bin/mamba install --yes --file requirements.txt -c conda-forge"


# For some reason the subsprocess command in "/usr/lib/tethys/tethys/tethys_cli/install_commands.py", line 693, in the install_command function, it is not 
# using the /opt/conda/envs/tethys/bin/pip but it wans to use /usr/bin/pip which does not extis that is why the error
# FileNotFoundError: [Errno 2] No such file or directory: 'pip'
RUN cp /opt/conda/envs/tethys/bin/pip /usr/bin
RUN cp /opt/conda/envs/tethys/bin/pip3 /usr/bin


RUN /bin/bash -c "cd ${TETHYS_HOME}/tethys_apps/tethys_nasaaccess \
  ; ${CONDA_HOME}/envs/tethys/bin/tethys install -N -w -v"

RUN /bin/bash -c "${CONDA_HOME}/envs/tethys/bin/pip install psycopg2==2.8.6"

# Configure the nasaacess to work with r-raster version 3.5_11
RUN ${CONDA_HOME}/envs/tethys/bin/mamba install r-raster==3.5_11 --yes -c conda-forge

######################################################
# CHANGE THE PROXY TIME REPLACING THE NGINX TEMPLATE #
######################################################

# CHOWN #
#########
RUN export NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}') \
  ; find ${TETHYSAPP_DIR} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${WORKSPACE_ROOT} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${STATIC_ROOT} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${TETHYS_PERSIST}/keys ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {} \
  ; find ${TETHYS_HOME}/tethys ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {}


#########################
# CONFIGURE ENVIRONMENT #
#########################
EXPOSE 80

##########################
# ADD THE EXTRA MIDDLEWARE 
##########################

ADD custom_middleware.py ${TETHYS_HOME}/tethys/tethys_portal/

###################
# ADD THE DATA PATH 
###################

RUN mkdir -p ${TETHYS_HOME}/data_nasa

######################################################
# CHANGE THE PROXY TIME REPLACING THE NGINX TEMPLATE #
######################################################

ADD nginx ${TETHYS_HOME}/tethys/tethys_cli/gen_templates/


################
# COPY IN SALT #
################

## Be sure to be inside the docker_files folder ##
ADD /salt/ /srv/salt/

# #####################################
# # ADDITIONAL DATABASE CONFIGURATION #
# #####################################
ADD fix.sql $HOME
ADD configure_db.sh $HOME


# ######################
# # CONFIGURE FINAL_RUN #
# ######################
ADD final_run.sh $HOME



# #######
# # RUN #
# #######
CMD bash final_run.sh
