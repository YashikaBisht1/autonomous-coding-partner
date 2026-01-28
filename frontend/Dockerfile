FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Ensure files are owned by the non-root node user
RUN chown -R node /app
USER node

CMD ["npm", "run", "dev"]
