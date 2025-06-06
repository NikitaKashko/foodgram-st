# build env
FROM node:21.7.1-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

# The CMD is not needed; this container's purpose is to run the
# build stages above and populate the volume mounted at /app/build.