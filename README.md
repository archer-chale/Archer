# Archer Initial Starter

## Running the Docker Compose

To run the docker-compose:
```sh
docker-compose up --build -d 
```

## Running the Client

1. Update `firebaseConfig.template.ts`
2. Remove "template" from the file name
3. Navigate to the client directory:
    ```sh
    cd client
    ```
4. Install dependencies:
    ```sh
    npm install
    ```
5. Run the development server:
    ```sh
    npm run dev
    ```

## Running the Backend

1. Update `adminsdk.template.json`
2. Run the docker-compose:
    ```sh
    docker-compose up --build -d
    ```