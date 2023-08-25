# Overview

The goal of this tutorial is: 

- To motivate small containerized applications
- Get familiar with some of docker's functionalities

# Monoliths -> Microservices

When developing an application, it is hard to design a fully-functional
distributed system upfront without understanding how the different components
will interact.

This is especially true in the case of developing a dynamic application with an
unbounded set of features. A small service created today with little
functionality, might in the future become a hard to maintain service with too
much functionality. The bigger a service becomes, the harder it becomes: to make
reliable changes to the codebase; to scale the service; and to update the codebase
(deploy time). Considering the case a component of the monolith has a bug that
shuts down the service, the other features are also unreachable if the service
is down. The monolith may then become less reliable as the codebase increases.

> Example of extracting a monolith into a microservice: 
> https://microservices.io/refactoring/example-of-extracting-a-service.html

Provided a good seperation of concerns is in place for the distributed system,
the developer's can focus their attention into optimizing a service's codebase
for a specific functionality. It also becomes easier to understand what an
application's bottleneck is, and how it can be scaled into a more performant
system.

However, there are some difficulties when developing microservices that cannot
be ignored. A few examples are:

- Organizational complexity
- Service deployment management
- Data consistency
- Unreliable communication
- Monitoring the distributed system

# Docker

Motivated by the first part of this tutorial, we now start working with one of
the most important building blocks of distributed systems nowadays,
**containers**.

Docker engine is a container runtime that virtualizes a host's operating
system. 

## Installation

> We will mostly follow this reference: 
> https://docs.docker.com/engine/install/ubuntu/

To install docker we run: 

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
```

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash 
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
sudo apt-get update
```

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify that it is working with: 
```bash
sudo docker run hello-world
```

## Post-Install

> To run docker without `sudo`, we have to go through the following reference:
> https://docs.docker.com/engine/install/linux-postinstall/

```bash
sudo groupadd docker
```

```bash
sudo usermod -aG docker $USER
```

Try running this command. Only if the changes don't take effect, then we will have to restart the virtual
machine.

```bash
newgrp docker
# sudo reboot
```

```bash
docker run hello-world
```

## Images & Containers


An image is a template to create containers. It is often the case that an image
is based on another image, e.g., you build an image based on `ubuntu` but
installs python and other dependencies to run a specific application. 

The image is composed of multiple stacked layers, each changing something in the
filesystem environment. They also contain the code or binary, runtimes,
dependencies and other fs objects.

> To read more about images: 
> docker: https://docs.docker.com/get-started/overview/#images
> circle-ci: https://circleci.com/blog/docker-image-vs-container/

The dockerfile is the file that creates a new image based upon an already
exisitng image. 

The goal of this section is to acquire a simple understanding of the
instructions `FROM`, `COPY`, `ADD`, `RUN`, `ENV`, `ENTRYPOINT`, `CMD`;
understand the difference between the exec and shell format of the `ENTRYPOINT`
and `CMD` instructions; Getting an intuition of what an image and a container
is.

### Demo

We will use the following python script to understand some nuances when
creating Dockerfiles.

```python
# main.py
import time
import signal
import sys

def signal_handler(sig, frame):
    print('EXITING SAFELY!')
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)

print("Starting")
print(sys.argv)
i = 0
while True:
    print(i)
    time.sleep(1)
    i += 1
```

There are a few things to note about this script: 

- A signal handler is registered for SIGTERM; 
- The arguments passed to the program on startup are printed to stdout; 
- The program enters an infinite loop;

Through this program we are now going to analyze 2 similar but fundamentally
different Dockerfiles. The first Dockerfile uses exec format of the `CMD` and
`ENTRYPOINT` instructions. 

```Dockerfile
# Dockerfile-exec

FROM python:3.7

WORKDIR /usr/src/app

COPY main.py .

CMD ["hello", "this", "is", "CMD"]

ENTRYPOINT ["python3", "main.py"]
```

Our second Dockerfile uses a shell form of what might look like the same
image. 

```Dockerfile
# Dockerfile-shell

FROM python:3.7

WORKDIR /usr/src/app

COPY main.py .

CMD ["hello", "this", "is", "CMD"]

ENTRYPOINT python3 main.py
```

Let's start with building both Dockerfiles: 
```bash
# These commands create 2 images with tags `d1i-exec` and `d1i-shell`.
docker build -t d1i-exec -f Dockerfile-exec .
docker build -t d1i-shell -f Dockerfile-shell .
```

We will start with the container in exec form, and analyze what the `CMD` and
`ENTRYPOINT` instructions are doing:
```bash
docker run --name t1c --rm -d d1i-exec
docker logs -f t1c
# Starting
# ['main.py', 'hello', 'this', 'is', 'CMD']
# 0
# 1
# 2
```

```bash
docker stop t1c
```

We now execute the same container, but we now specify the arguments to pass into
our `ENTRYPOINT`:
```bash
docker run --name t1c --rm -d d1i-exec arg1 arg2
docker logs -f t1c
# Starting
# ['main.py', 'arg1', 'arg2']
# 0
# 1
# 2
```
Notice how what we specified in the `CMD` instruction is ignored.

Lets have a look at how signal propagation works in the exec form. Get an
interactive shell from the container: 
```bash
docker exec -it t1c /bin/sh
```

List the running processes in the container:
```bash
ps -ef
# UID          PID    PPID  C STIME TTY          TIME CMD
# root           1       0  0 08:36 ?        00:00:00 python3 -u main.py hello this is CMD
# root           7       0  0 08:39 pts/0    00:00:00 /bin/sh
# root          13       7  0 08:39 pts/0    00:00:00 ps -ef
```

Note how our program is PID 1. Now lets try and stop the container with: 
```bash
docker stop t1c
```

When we stop a container with `docker stop` it sends a `SIGTERM`, waits ten
seconds and if the container hasn't stopped it then sends a `SIGKILL`. In this
case, because we have registered a signal handler for SIGTERM, our process will
exit as soon as it has handled the signal. 

How does signal propagation work in the shell form container? We can start the
shell form container with:
```bash
docker run --name t1c --rm -d d1i-shell
docker logs -f t1c
# Starting
# ['main.py']
# 0
# 1
```

The first thing to note is how there are no arguments passed into our program.
When using the shell form, docker runs our command via `/bin/sh -c
'our-command'`. This will be important to understand the behaviour of signal
propagation in the shell form dockerfile. Using the shell form also prevents any
commands from the `CMD` or from the `docker run` instruction to be passed into
our executable.

Lets attach an interactive shell to the container:
```bash
docker exec -it t1c /bin/sh
ps -ef
# UID          PID    PPID  C STIME TTY          TIME CMD
# root           1       0  0 09:15 ?        00:00:00 /bin/sh -c python3 -u main.py hello this is CMD
# root           7       1  0 09:15 ?        00:00:00 python3 -u main.py
# root           8       0  0 09:22 pts/0    00:00:00 /bin/sh
# root          13       8  0 09:22 pts/0    00:00:00 ps -ef
```

Our container started as an executable with the `/bin/sh` program and this
process was responsible for executing the `python3 -u main.py` string passed to
the `-c` option. Because the other options were passed into `/bin/sh` as the
other set of arguments, these were not included in the command being executed by
the option. 

Lets stop our container and have a look at how it behaves: 
```bash
docker stop t1c
```

The program seems to hang for 10 seconds, and then terminate. This means that
our program did not receive the `SIGTERM` signal, and did not exit gracefully.
This happens because programs started by `/bin/sh` are usually forked. While the
program is executing, any signal received by `/bin/sh` is queued to be processed
after the program that is executing terminated, i.e., the `/bin/sh` program does
not propagate the `SIGTERM` to its child processes.

> For further reading on what we have just discussed: 
> https://www.kaggle.com/code/residentmario/best-practices-for-propagating-signals-on-docker
> 
> Docker entrypoint references: 
> https://docs.docker.com/engine/reference/builder/#entrypoint

## Volumes

> Docker volumes reference: 
> https://docs.docker.com/storage/volumes/

Volumse are used to share data between containers and/or persist data across
different container executions. Without volumes the data stored in containers is
lost as soon as the container is removed.

E.g. If we containerize a database, we would most likely want the database
data persisted.

We can manage volumes specifically with the `docker volumes` CLI, or they can be
created automatically when passing the `-v` option to the `docker run` command.
When passing the `-v` option, there are 3 colon seperated fields:

1. Name of the volume / host directory path
2. Container mount path
3. Mount options (read, read/write, ...)

### Demo

We are going to resort to a simple Dockerfile to experiment with Docker volumes: 
```Dockerfile
# Dockerfile

FROM busybox:latest

RUN mkdir -p /usr/src/data && \
    touch /usr/src/data/save_file && \
    echo "first line" >> /usr/src/data/save_file

VOLUME ["/usr/src/data"]

WORKDIR /usr/src/app
COPY entrypoint.sh .

CMD ["./entrypoint.sh", "../data/save_file"]
```

We start by creating a directory `/usr/src/data`, create a new file `save_file`,
and write "first line" to the newly created file.

The `VOLUME` instruction serves as documentation as to what directory we expect
will be mounted.

We then copy the `entrypoint.sh` script to the `/usr/src/app` directory.

The script has the following structure: 
```bash
#!/bin/sh
# entrypoint.sh

function terminate {
  echo "terminating"
  exit 0
}

trap terminate SIGTERM SIGINT

echo "reading $1"
tail -f $1 &
wait
```

We now build our image with: 
```bash
docker build -t t2i .
```

The first container we will run, will simply run the entrypoint script, which is
reading the data that is being written to the `/usr/src/data/save_file` (as a
result of the CMD instruction in the dockerfile). To run it, execute:
```bash
docker run \
    -d --rm \
    --name t2c-1 \
    --volume t2v:/usr/src/data \
    t2i
```

As for our second container, because we will be passing arguments to the `docker
run` command, the `CMD` instruction is ignored, effectively `exec`ing what we
pass as arguments. This happens to be a bash instruction `echo "sharing" >>
../data/save_file`. 

```bash
docker run \
    -d --rm \
    --name t2c-2 \
    --volume t2v:/usr/src/data \
    t2i \
    /bin/sh -c 'echo "sharing" >> ../data/save_file'
```

If our intuition about volumes is correct then because we are sharing the same
volume between both containers, the first container should be able to see the
data that has been written by this second command. Run the following command to
validate whether this is the case: 
```bash
docker logs -f t2c-2
```

Alternatively, instead of using docker's named volumes, we could indicate the
volume to be a directory in our host's filesystem. We can do this with the
following command: 
```bash
docker run \
    -d --rm \
    --name t2c-1 \
    --volume $(pwd)/data:/usr/src/data \
    t2i
```

We can run our second container now with the command:
```bash
docker run \
    -d --rm \
    --name t2c-2 \
    --volume "$(pwd)/data":/usr/src/data \
    t2i \
    /bin/sh -c 'echo "hello" >> ../data/save_file'
```

We can also read the data that has been written to our host file:
```bash
cat ./data/save_file
```

To clean our setup we can run:
```bash
docker stop t2c-1
docker volume rm t2v
```

## Networks

### Demo