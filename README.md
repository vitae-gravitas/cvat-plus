# cvat-plus 
## Clone this repo 
-   Title...
## Docker installation 
-   Download [Docker for Mac](https://download.docker.com/mac/stable/Docker.dmg).
    Double-click Docker.dmg to open the installer, then drag Moby the whale
    to the Applications folder. Double-click Docker.app in the Applications
    folder to start Docker. More instructions can be found
    [here](https://docs.docker.com/v17.12/docker-for-mac/install/#install-and-run-docker-for-mac). 
-   Once you have the docker application make sure to make an account. Then sign into docker [here](https://docs.docker.com/v17.12/docker-for-mac/install/#install-and-run-docker-for-mac).

## Set up cvat

-   Make sure `./cvat-plus/cvat/Lifting-Videos` exists. If it does not just make that directory yourself.

-   Build docker images by default. It will take some time to download public
    docker image ubuntu:16.04 and install all necessary ubuntu packages to run
    CVAT server.

    ```bash
    docker-compose build
    ```

-   Run docker containers. It will take some time to download public docker
    images like postgres:10.3-alpine, redis:4.0.5-alpine and create containers.

    ```sh
    docker-compose up -d
    ```
-   You can register a user but by default it will not have rights even to view
    list of tasks. Thus you should create a superuser. A superuser can use an
    admin panel to assign correct groups to other users. Please use the command
    below. Take a note of this password because you will use it in the next step.

    ```sh
    docker exec -it cvat bash -ic 'python3 ~/manage.py createsuperuser'
    ``` 
-   Open Google Chrome and go to [localhost:8080](http://localhost:8080).
    Type your login/password for the superuser on the login page and press the _Login_
    button.

## Configuring Annotations
-   The instructions in this section are specific to the way I have setup CVAT for us. I have automated a couple processes that would otherwise be quite tedious when annotating on a large scale

-	Next, open up `./cvat-plus/config.py` and put your user and password that you created in the last step.

### Load Videos
-   Go to `./cvat-plus/cvat/Lifting-Videos` and put all the videos that you are going to annotate there.
-   In order to be able to view and annotate all the images in `./cvat-plus/cvat/Lifting-Videos` you must first load all these videos as tasks. Run the following command:

    ```sh
    cd ./cvat-plus
    python load.py
    ```
### Download Annotation Files
-	After you are done annotating you will need to download all annotation files. Make sure `./cvat-plus/annotations` exists. If it does not just make that directory yourself. Then run the following command:

    ```sh
    cd ./cvat-plus
    python download.py
    ```
### Delete all Video Tasks
-	Let's say you placed a bunch of wrong videos into `./cvat-plus/cvat/Lifting-Videos` and ran `python load.py` you can use `delete.py`. However be careful because this will delete all the work on your localhost. To run this just do the following:

    ```sh
    cd ./cvat-plus
    python delete.py
    ```
## Using the CVAT USER Interface
-    Go to [localhost:8080](http://localhost:8080). If you loaded the videos from the previous section you should see a bunch of video tasks.  It make take a while for these videos to show up. User the user guide provide by CVAT to understand the GUI [guide](https://github.com/opencv/cvat/blob/develop/cvat/apps/documentation/user_guide.md)




