FROM gmart2002/auto_pattern-frontend:22.22.1

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 3000

ENV VITE_HOST=localhost
ENV VITE_PORT=3000

CMD ["npm", "run", "dev:web"]