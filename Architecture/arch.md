# IRCTC Backend System - Architecture Diagrams

This document contains Mermaid diagrams illustrating the system architecture, database relationships, API flows, and key processes.

---

## 1. System Architecture Overview

```mermaid
graph TB
    Client[Client Application]
    API[Django REST API]
    MySQL[(MySQL Database)]
    Mongo[(MongoDB)]
    
    Client -->|HTTP/JSON + JWT| API
    API -->|Transactional Data| MySQL
    API -->|Logs & Analytics| Mongo
    
    subgraph "Django Backend"
        API --> Auth[Authentication Layer]
        API --> Train[Train Management]
        API --> Booking[Booking System]
        API --> Analytics[Analytics Engine]
    end
    
    Auth -->|User Data| MySQL
    Train -->|Train Data| MySQL
    Booking -->|Booking Data + Race Control| MySQL
    Analytics -->|Aggregation| Mongo
    Train -->|Search Logs| Mongo
```

---

## 2. Database Schema (MySQL)

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : makes
    TRAINS ||--o{ BOOKINGS : has
    
    USERS {
        int id PK
        string email UK
        string password
        string first_name
        string last_name
        string phone
        boolean is_staff
        boolean is_active
        datetime date_joined
    }
    
    TRAINS {
        int id PK
        string train_number UK
        string name
        string source
        string destination
        time departure_time
        time arrival_time
        int total_seats
        int available_seats
    }
    
    BOOKINGS {
        int id PK
        int user_id FK
        int train_id FK
        int num_seats
        string status
        datetime booking_date
    }
```

---

## 3. MongoDB Schema

```mermaid
graph LR
    A[MongoDB: irctc_logs] --> B[Collection: search_logs]
    
    B --> C[Document Structure]
    
    C --> D[endpoint: string]
    C --> E[user_id: int]
    C --> F[params: object]
    C --> G[execution_time_ms: float]
    C --> H[result_count: int]
    C --> I[timestamp: date]
    
    F --> F1[source: string]
    F --> F2[destination: string]
```

---

## 4. Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant MySQL
    participant JWT
    
    Note over Client,JWT: User Registration
    Client->>API: POST /api/register/
    API->>Auth: Validate data
    Auth->>Auth: Hash password
    Auth->>MySQL: Create user
    MySQL-->>Auth: User created
    Auth->>JWT: Generate tokens
    JWT-->>API: Access + Refresh tokens
    API-->>Client: 201 Created + tokens
    
    Note over Client,JWT: User Login
    Client->>API: POST /api/login/
    API->>Auth: Authenticate(email, password)
    Auth->>MySQL: Query user
    MySQL-->>Auth: User data
    Auth->>Auth: Verify password
    Auth->>JWT: Generate tokens
    JWT-->>API: Access + Refresh tokens
    API-->>Client: 200 OK + tokens
```

---

## 5. Train Search Flow with Logging

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant MySQL
    participant MongoDB
    
    Client->>API: GET /api/trains/search/?source=Delhi&destination=Mumbai
    Note over API: Start timer
    API->>API: Validate JWT token
    API->>API: Parse query params
    API->>MySQL: SELECT trains WHERE source='Delhi' AND destination='Mumbai'
    MySQL-->>API: Train records
    API->>API: Apply pagination
    API->>API: Serialize data
    Note over API: Calculate execution time
    API->>MongoDB: Log search request (async)
    MongoDB-->>API: Log saved
    API-->>Client: 200 OK + train results
```

---

## 6. Booking Flow (Race Condition Prevention)

```mermaid
sequenceDiagram
    participant User1
    participant User2
    participant API
    participant DB
    
    Note over User1,DB: Two users booking simultaneously
    
    par User 1 booking
        User1->>API: POST /bookings/ (2 seats)
        API->>DB: BEGIN TRANSACTION
        API->>DB: SELECT ... FOR UPDATE (Lock row)
        Note over DB: Train row LOCKED
        DB-->>API: Train data (locked)
        API->>API: Check: available_seats >= 2
        API->>DB: UPDATE available_seats = available_seats - 2
        API->>DB: INSERT booking
        API->>DB: COMMIT
        Note over DB: Train row UNLOCKED
        API-->>User1: 201 Created
    and User 2 booking
        User2->>API: POST /bookings/ (2 seats)
        API->>DB: BEGIN TRANSACTION
        API->>DB: SELECT ... FOR UPDATE
        Note over DB: WAITING for lock...
        Note over DB: Lock released by User1
        DB-->>API: Train data (updated)
        API->>API: Check: available_seats >= 2
        API->>DB: UPDATE available_seats = available_seats - 2
        API->>DB: INSERT booking
        API->>DB: COMMIT
        API-->>User2: 201 Created
    end
```

---

## 7. Complete API Request Flow

```mermaid
flowchart TD
    Start([Client Request]) --> Auth{JWT Token Valid?}
    Auth -->|No| Reject[401 Unauthorized]
    Auth -->|Yes| Parse[Parse Request Data]
    
    Parse --> Route{Which Endpoint?}
    
    Route -->|/register| Register[Create User]
    Route -->|/login| Login[Authenticate User]
    Route -->|/trains/search| Search[Search Trains]
    Route -->|/trains/| CreateTrain{Is Admin?}
    Route -->|/bookings/| Book[Create Booking]
    Route -->|/bookings/my/| MyBook[Get My Bookings]
    Route -->|/analytics/top-routes| TopRoutes[Aggregate Analytics]
    
    CreateTrain -->|No| Reject2[403 Forbidden]
    CreateTrain -->|Yes| CreateTrainDB[Save Train]
    
    Register --> GenToken[Generate JWT]
    Login --> GenToken
    
    Search --> QueryMySQL[Query MySQL]
    Search --> LogMongo[Log to MongoDB]
    
    Book --> Lock[SELECT FOR UPDATE]
    Lock --> CheckSeats{Seats Available?}
    CheckSeats -->|No| Error[400 Bad Request]
    CheckSeats -->|Yes| Deduct[Deduct Seats]
    Deduct --> CreateBooking[Create Booking Record]
    
    MyBook --> QueryBookings[Query User Bookings]
    
    TopRoutes --> AggMongo[MongoDB Aggregation]
    
    GenToken --> Success[Return Response]
    QueryMySQL --> Success
    LogMongo --> Success
    CreateTrainDB --> Success
    CreateBooking --> Success
    QueryBookings --> Success
    AggMongo --> Success
    
    Success --> End([200/201 Response])
    Reject --> End
    Reject2 --> End
    Error --> End
```

---

## 8. Admin vs User Access Control

```mermaid
graph TD
    Request[API Request] --> HasToken{Has JWT Token?}
    HasToken -->|No| Denied1[401 Unauthorized]
    HasToken -->|Yes| ValidToken{Token Valid?}
    ValidToken -->|No| Denied2[401 Unauthorized]
    ValidToken -->|Yes| CheckEndpoint{Which Endpoint?}
    
    CheckEndpoint -->|Public: register, login| Allow[Process Request]
    CheckEndpoint -->|User: search, book, my-bookings| CheckAuth{Authenticated?}
    CheckEndpoint -->|Admin: create/update train| CheckAdmin{Is Staff?}
    
    CheckAuth -->|No| Denied3[401 Unauthorized]
    CheckAuth -->|Yes| Allow
    
    CheckAdmin -->|No| Denied4[403 Forbidden]
    CheckAdmin -->|Yes| Allow
    
    Allow --> Process[Execute Business Logic]
    Process --> Response[Return Response]
```

---

## 9. Booking State Machine

```mermaid
stateDiagram-v2
    [*] --> Draft: User initiates booking
    Draft --> Validating: Submit booking request
    
    Validating --> Failed: Validation error
    Validating --> Locking: Valid request
    
    Locking --> RowLocked: SELECT FOR UPDATE
    
    RowLocked --> CheckingSeats: Lock acquired
    
    CheckingSeats --> Insufficient: Not enough seats
    CheckingSeats --> Deducting: Seats available
    
    Deducting --> Creating: Update available_seats
    Creating --> Confirmed: Insert booking record
    
    Confirmed --> [*]: Booking complete
    Insufficient --> [*]: Return error
    Failed --> [*]: Return error
    
    note right of RowLocked
        Critical Section:
        Row locked to prevent
        race conditions
    end note
```

---

## 10. Analytics Pipeline

```mermaid
flowchart LR
    A[Train Search API] --> B[Log to MongoDB]
    B --> C[(MongoDB: search_logs)]
    
    C --> D[Analytics API Called]
    D --> E[Aggregation Pipeline]
    
    E --> F[Group by route]
    F --> G[Count searches]
    G --> H[Sort by count]
    H --> I[Limit to top 5]
    
    I --> J[Format response]
    J --> K[Return to client]
    
    style C fill:#47A248
    style E fill:#FF6B6B
```

---

## 11. Data Flow Architecture

```mermaid
graph LR
    subgraph "Client Layer"
        Web[Web App]
        Mobile[Mobile App]
        API_Client[API Client]
    end
    
    subgraph "API Gateway"
        JWT_Auth[JWT Authentication]
        Rate_Limiter[Rate Limiter]
    end
    
    subgraph "Application Layer"
        Users_API[Users API]
        Trains_API[Trains API]
        Bookings_API[Bookings API]
        Analytics_API[Analytics API]
    end
    
    subgraph "Data Layer"
        MySQL[(MySQL)]
        MongoDB[(MongoDB)]
    end
    
    Web --> JWT_Auth
    Mobile --> JWT_Auth
    API_Client --> JWT_Auth
    
    JWT_Auth --> Rate_Limiter
    Rate_Limiter --> Users_API
    Rate_Limiter --> Trains_API
    Rate_Limiter --> Bookings_API
    Rate_Limiter --> Analytics_API
    
    Users_API --> MySQL
    Trains_API --> MySQL
    Trains_API --> MongoDB
    Bookings_API --> MySQL
    Analytics_API --> MongoDB
```

---


---

## 13. Error Handling Flow

```mermaid
flowchart TD
    Request[API Request] --> Try{Try Block}
    
    Try --> Business[Business Logic]
    Business --> Success{Success?}
    
    Success -->|Yes| Return200[200/201 Response]
    Success -->|No| CatchError[Catch Exception]
    
    CatchError --> ErrorType{Error Type?}
    
    ErrorType -->|Validation| Return400[400 Bad Request]
    ErrorType -->|Not Found| Return404[404 Not Found]
    ErrorType -->|Unauthorized| Return401[401 Unauthorized]
    ErrorType -->|Forbidden| Return403[403 Forbidden]
    ErrorType -->|Server Error| Return500[500 Internal Server Error]
    
    Return400 --> Log[Log Error]
    Return404 --> Log
    Return401 --> Log
    Return403 --> Log
    Return500 --> Log
    
    Log --> Response[Return Error Response]
    Return200 --> End([End])
    Response --> End
```

---