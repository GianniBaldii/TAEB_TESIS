FROM node:22-alpine

WORKDIR /workspace/mobile

COPY mobile/package*.json ./
RUN npm ci

COPY mobile/ ./

EXPOSE 8100

CMD ["npm", "run", "start"]
