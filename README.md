# poc-microservice

An app to play with microservice architecture using FastAPI

# Setup

Use VSCode devcontainer feature to install the project using Docker.

# Usage

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
curl -X POST http://localhost:8000/users -d "name=Alice" -d "email=alice@example.com"
```

This should:

- Insert into user-db
- Publish user_created event to RabbitMQ
- Consume event in Order service
- Insert into order-db snapshot table (order_users)
