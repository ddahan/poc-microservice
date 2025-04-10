# poc-microservice

## 🧠 How it works

This project demonstrates a simple event-driven microservices architecture using Python, FastAPI, RabbitMQ, and SQLite.

### 🧱 Services

- **User Service**: FastAPI app that exposes an HTTP POST /users endpoint. When a user is created, it saves the user to its own local SQLite database and publishes a `user_created` event to RabbitMQ.

- **Order Service**: A background Python process that subscribes to the `user_created` queue in RabbitMQ. When it receives an event, it creates or updates a local (partial) copy of the user (called a snapshot) in its own SQLite database.

This demonstrates decoupling, event publishing/consuming, and eventual consistency between services — each service has its own database and communicates via messages, not HTTP.

## ⚙️ Setup

Use VSCode devcontainer feature to install the project using Docker.

## 🚀 Usage

### 1. Run the infrastracture

- Either locally, running this devcontainer
- Or with `docker-compose -f docker-compose.local.yml up`

### 2. Start the services

In one terminal: run `User` service (publisher):

```sh
cd services/user
uvicorn app.main:app --reload --port 8000
```

In another terminal: run `Order` service (consumer):

```sh
cd services/order
python -m app.consumer
```

### 3. Create a user (simulate event)

```sh
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

This should:

- Insert into user-db
- Publish user_created event to RabbitMQ
- Consume event in Order service
- Insert into order-db snapshot table (order_users)
