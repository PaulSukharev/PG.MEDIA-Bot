FROM node:20

WORKDIR /usr/src/app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

RUN npm run build \
    && npm cache clean --force

ENV NODE_ENV=$NODE_ENV

CMD ["node", "dist/index.js"]