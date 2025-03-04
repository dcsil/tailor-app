# Tailor

## Installation instructions

### Tech Stack
1. Ensure you have [Python3](https://www.python.org/downloads/) (for backend) and [Node.js >= 18.0](https://nodejs.org/en) (for frontend) installed.
2. Install [Docker / Docker Compose](https://www.docker.com/products/docker-desktop/)
3. Make sure docker is running by opening docker desktop app.

### Running
1. Clone our repo `git clone https://github.com/dcsil/tailor-app.git`
2. `cd tailor-app`
3. Add `.env` file by copying over `.env.example` file and replacing the fake credentials with your own.
4. Run `script/bootstrap` 
5. Go to http://127.0.0.1:5173

## Testing
### Backend:
```
docker compose run --rm backend pytest tests 
```
### Frontend:
```
docker compose run --rm frontend sh -c "npm install --save-dev jest && npm test"
```

## Logs and debugging
### Backend:
```
docker compose logs backend -f
```

### Frontend:
```
docker compose logs frontend -f
```

## Production
[Tailor website](https://tailor-4d71417e9aab.herokuapp.com/)