To run the docker-compose:
docker-compose up --build -d 

To run the client: 
update firebaseConfig.template.ts
Remove "template" from the file name
cd client
npm install
npm run dev

To run backend: 
Update adminsdk.template.json
docker-compose up --build -d 