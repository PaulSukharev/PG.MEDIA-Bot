FROM node:20

WORKDIR /usr/src/app

COPY package.json package-lock.json tsconfig.json ./

RUN npm ci

COPY dist/ ./dist
COPY src/assets/ ./src/assets/

# RUN npm run start:prod \
#     && npm cache clean --force

# RUN [ "npm", "install" ]
ENTRYPOINT [ "npm", "run", "start:prod" ]
