# Deploying FastAPI Application with SQLAlchemy on EC2 using Docker with RDS(Postgre sql) setup on AWS

### Prerequisites
1. AWS Account: Ensure you have access to an AWS account.
2. EC2 Instance: Launch an EC2 instance with a Linux-based AMI.
3. RDS PostgreSQL Database: Set up a PostgreSQL database on AWS RDS.
4. Docker Hub Account: Ensure you have a Docker Hub account to push your Docker image

Clone this repo your directory structure should look like this 
  /.your_project \
|-- .env \
|-- docker-compose.yml \
|-- Dockerfile \
|-- main.py \
|-- requirements.txt 

### Set Up main.py, requirements.txt, Dockerfile, and docker-compose.yml
1. main.py: Define the FastAPI application and SQLAlchemy setup with postgres SQL hosted on AWS and also used guid for a unique id for the users id.
2. requirements.txt: List the project dependencies (e.g., fastapi,uvicorn,sqlalchemy,pydantic,psycopg2-binary).
3. Dockerfile: Created the Dockerfile to containerize the application.
4. docker-compose.yml: Define for Docker Compose setup.

### Build and Push Docker Image
Build your Docker image and push it to Docker Hub:

    ```
    docker build -t your_dockerhub_username/your_image_name:tag .
    docker push your_dockerhub_username/your_image_name:tag
    ```

### EC2 Environment

1. Go to the AWS Management Console.
2. Launch a new EC2 instance with a Linux AMI (e.g., Amazon Linux 2).
3. Configure the security group to allow inbound traffic on port 8080.
4. Connected the EC2 with console.
5. Installed the docker and docker-compose 
    ```
    sudo yum install docker -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```
6. Login the dockerhub by command and enter the dockerhub credentials
    ```
    docker login
    ```
7. Create the docker-compose file and add the repo name of dockerhub 
    ```
    nano docker-compose.yml

    version: '3.8'

    services:
    backend:
        image: dockerhub_username/repo_name:latest  
        command: uvicorn main:app --host 0.0.0.0 --port 8080
        volumes:
        - .:/app  
        ports:
        - "8080:8080"
        env_file:
        - .env
        restart: always

8. Setup the env creds in ec2 instance which will the store the important config values like database url of postgre sql,database username and password
    ```
    echo "DATABASE_URL=postgresql://username:password@RDSURL/dbname" > /home/ec2-user/.env
    echo "POSTGRES_USER=username" > /home/ec2-user/.env
    echo "POSTGRES_PASSWORD=password" > /home/ec2-user/.env
    ```
    This will store all the credantials into the ec2

9. Now everything is set up run the docker-compose file 
    ```
    docker-compose up -d
    ```

10. If everything is working fine then you will the 'success' in console otherwise check the logs for the error 
    ```
    docker ps (current running container will shown here with container details and container id)
    docker logs <container_id>
    ```

11. Go to the instance click for the public IPV4 DNS,In the new tab link will open make the link "http" and add the port,api request ":8080/get_users/" at the end
    ```
    http://<IPV4 DNS>:8080/get_users/
    ```

12. You have successfully FastAPI Application with SQLAlchemy on EC2 using Docker with RDS(Postgre sql) setup on AWS

    
### Output
1. JSON object with a dynamic number of fields and stores this JSON 
![alt text](image.png)


2. JSON with user details and a unique user ID(guid) 
![alt text](image-1.png)
