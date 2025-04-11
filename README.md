# poc-microservice

## 🧠 How it works

This project demonstrates a simple event-driven microservices architecture using Python, FastAPI, RabbitMQ, and SQLite.

### 🧱 Services

- **User Service**  
  A FastAPI app exposing a `POST /users` endpoint. When a user is created:
  - It saves the user to its own local SQLite database
  - It publishes a `user_created` event to the `queue_dispatch` queue

- **Notification Service**  
  - A background consumer that listens to the `queue_dispatch` queue and routes incoming events to other queues based on a routing table.

- **Order Service**  
  - A background consumer that listens to the `queue_order` queue.  
  - When it receives a `user_created` event, it stores a **snapshot** of the user in its own SQLite database.

This demonstrates:
- **Loose coupling** between services
- **Asynchronous event dispatching**
- **Eventual consistency** using RabbitMQ and dedicated databases per service


### ✍🏻 Diagram

```ascii
+----------------------------+
|  User Service              |
|  (FastAPI: /users)         |
+----------------------------+
          |
          | 1. Publishes `user_created` event
          v
+----------------------------+
|  RabbitMQ Queue:           |
|  queue_dispatch            |
+----------------------------+
          |
          | 2. Consumed by
          v
+----------------------------+
|  Notification Service      |
|  (consumer + router)       |
+----------------------------+
          |
          | 3. Forwards to (using routing table)
          v
+----------------------------+
|  RabbitMQ Queue:           |
|  queue_order              |
+----------------------------+
          |
          | 4. Consumed by
          v
+----------------------------+
|  Order Service             |
|  (snapshot store)          |
+----------------------------+

```

## ⚙️ Setup

Use VSCode devcontainer feature to install the project using Docker.

## 🚀 Usage

### 1. Run the infrastracture

- Either locally, running this devcontainer
- Or with `docker-compose -f docker-compose.local.yml up`

### 2. Start the services

```sh
cd services/notification && python -m app.consumer
cd services/order        && python -m app.consumer
cd services/user         && uvicorn app.main:app --reload --port 8000
```

### 3. Create a user (simulate event)

```sh
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

This will:
- Insert the user into the User Service’s SQLite DB
- Publish a `user_created` event to RabbitMQ (`queue_dispatch` queue)
- Trigger the Notification Service to forward the event to `queue_order`
- Order Service will store a **snapshot** of the user in its own DB
