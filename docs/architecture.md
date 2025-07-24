# hitoQ Architecture Documentation

## Overview

hitoQ is a social profile application that allows users to create personalized pages through Q&A responses, profile customization, and goal tracking. Built on a modern web stack with security-first design principles.

## System Architecture

```mermaid
graph TB
    subgraph "Client Browser"
        FE[SvelteKit Frontend]
        UI[User Interface]
        FE --> UI
    end

    subgraph "Backend Services"
        API[FastAPI Backend]
        AUTH[Authentication Service]
        QNA[Q&A Service]
        PROFILE[Profile Service]
        BUCKET[Bucket List Service]
        USER[User Service]
    end

    subgraph "External Services"
        TWITTER[Twitter OAuth 2.0]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL Database)]
        REDIS[(Redis Cache)]
    end

    UI -.->|HTTPS/REST API| API
    API --> AUTH
    API --> QNA
    API --> PROFILE
    API --> BUCKET
    API --> USER

    AUTH -.->|OAuth Flow| TWITTER

    AUTH --> DB
    QNA --> DB
    PROFILE --> DB
    BUCKET --> DB
    USER --> DB

    API -.->|Session Storage| REDIS
```

## Database Schema

```mermaid
erDiagram
    users {
        string user_id PK
        string user_name UK
        string display_name
        string bio
        string icon_url
        datetime created_at
        datetime updated_at
    }

    profile_items {
        uuid profile_item_id PK
        string user_id FK
        string label
        string value
        int display_order
        datetime created_at
        datetime updated_at
    }

    bucket_list_items {
        int bucket_list_item_id PK
        string user_id FK
        string content
        boolean is_completed
        int display_order
        datetime created_at
        datetime updated_at
    }

    questions {
        int question_id PK
        enum category
        string text
        int display_order
        datetime created_at
    }

    answers {
        int answer_id PK
        string user_id FK
        int question_id FK
        string answer_text
        datetime created_at
        datetime updated_at
    }

    users ||--o{ profile_items : has
    users ||--o{ bucket_list_items : has
    users ||--o{ answers : has
    questions ||--o{ answers : has
```

## Frontend Architecture

```mermaid
graph TB
    subgraph "SvelteKit Frontend"
        subgraph "Routes"
            ROOT["/"]
            USER["[user_name]/"]
            PROFILE["[user_name]/+page"]
            BUCKET["[user_name]/bucket"]
            QNA["[user_name]/qna"]
            SETTINGS["[user_name]/settings"]
        end

        subgraph "Layouts"
            GLOBAL["+layout.svelte"]
            USER_LAYOUT["[user_name]/+layout.svelte"]
        end

        subgraph "Components"
            EDIT[Editable.svelte]
            HEADER[ProfileHeader.svelte]
            TABS[TabNavigation.svelte]
            BUCKET_LIST[BucketList.svelte]
            QA_GROUP[QAGroup.svelte]
            QA_ITEM[QAItem.svelte]
        end

        subgraph "Services"
            API_CLIENT[API Client]
            AUTH_SERVICE[Auth Service]
        end
    end

    GLOBAL --> USER_LAYOUT
    USER_LAYOUT --> PROFILE
    USER_LAYOUT --> BUCKET
    USER_LAYOUT --> QNA
    USER_LAYOUT --> SETTINGS

    PROFILE --> EDIT
    PROFILE --> HEADER
    BUCKET --> BUCKET_LIST
    QNA --> QA_GROUP
    QA_GROUP --> QA_ITEM
    QA_ITEM --> EDIT

    PROFILE --> API_CLIENT
    BUCKET --> API_CLIENT
    QNA --> API_CLIENT

    API_CLIENT --> AUTH_SERVICE
```

## Backend Service Architecture

```mermaid
graph TB
    subgraph "FastAPI Backend"
        subgraph "Routers"
            AUTH_ROUTER[Auth Router]
            USER_ROUTER[User Router]
            MAIN_ROUTER[Main Router]
        end

        subgraph "Services"
            USER_SVC[User Service]
            QNA_SVC[Q&A Service]
            PROFILE_SVC[Profile Service]
            BUCKET_SVC[Bucket List Service]
        end

        subgraph "Database"
            TABLES[SQLAlchemy Tables]
            SCHEMAS[Pydantic Schemas]
        end

        subgraph "External"
            TWITTER_API[Twitter API]
        end
    end

    MAIN_ROUTER --> AUTH_ROUTER
    MAIN_ROUTER --> USER_ROUTER

    AUTH_ROUTER --> USER_SVC
    AUTH_ROUTER --> TWITTER_API

    USER_ROUTER --> USER_SVC
    USER_ROUTER --> QNA_SVC
    USER_ROUTER --> PROFILE_SVC
    USER_ROUTER --> BUCKET_SVC

    USER_SVC --> TABLES
    QNA_SVC --> TABLES
    PROFILE_SVC --> TABLES
    BUCKET_SVC --> TABLES

    TABLES --> SCHEMAS
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Twitter

    User->>Frontend: Click "Login with Twitter"
    Frontend->>Backend: GET /auth/login/twitter
    Backend->>Backend: Generate PKCE challenge
    Backend->>Twitter: Redirect to Twitter OAuth
    Twitter->>User: Show authorization page
    User->>Twitter: Authorize application
    Twitter->>Backend: Callback with auth code
    Backend->>Twitter: Exchange code for tokens
    Twitter->>Backend: Return access/refresh tokens
    Backend->>Backend: Create/update user record
    Backend->>Backend: Generate JWT tokens
    Backend->>Frontend: Set HTTP-only cookies
    Frontend->>Frontend: Redirect to user profile
```

## Data Flow Patterns

### Page Loading Flow

```mermaid
sequenceDiagram
    participant Browser
    participant SvelteKit
    participant Backend
    participant Database

    Browser->>SvelteKit: Navigate to /username/qna
    SvelteKit->>Backend: GET /users/by-username/{username}/qna
    Backend->>Database: Query user answers grouped by category
    Database->>Backend: Return user answer groups
    Backend->>Database: Query available Q&A templates
    Database->>Backend: Return available templates
    Backend->>SvelteKit: Return composite page data
    SvelteKit->>Browser: Render Q&A page with data
```

### User Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Component
    participant API_Client
    participant Backend
    participant Database

    User->>Component: Edit profile item
    Component->>Component: Update local state (optimistic)
    Component->>API_Client: POST /users/{id}/profile-items
    API_Client->>Backend: HTTP request with auth
    Backend->>Database: Update profile item
    Database->>Backend: Confirm update
    Backend->>API_Client: Return updated item
    API_Client->>Component: Confirm success

    Note over Component: If error occurs, revert local state
```

## Key Features

### 1. Profile Management

- **Editable Profile Items**: Dynamic key-value pairs with drag-and-drop ordering
- **Real-time Updates**: Optimistic UI updates with backend synchronization
- **Profile Header**: User avatar, display name, and bio from Twitter

### 2. Q&A System

- **Template-based Questions**: Predefined categories (self-introduction, values, otaku, misc)
- **Answer Grouping**: Questions grouped by category with expandable UI
- **Progress Tracking**: Visual indication of answered vs. unanswered questions

### 3. Bucket List

- **Goal Tracking**: Add, edit, and mark goals as completed
- **Drag-and-Drop**: Reorder goals with visual feedback
- **Completion Status**: Toggle completion with visual indicators

### 4. Security Features

- **OAuth 2.0 with PKCE**: Secure Twitter authentication
- **JWT Tokens**: Short-lived access tokens with refresh mechanism
- **HTTP-only Cookies**: Secure token storage preventing XSS
- **CORS Protection**: Configured for production environments

## Technology Choices

### Frontend

- **SvelteKit**: Full-stack framework with SSR/SPA capabilities
- **TypeScript**: Type safety throughout the application
- **TailwindCSS**: Utility-first CSS framework
- **Svelte 5 Runes**: Modern reactivity system

### Backend

- **FastAPI**: High-performance async Python framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Alembic**: Database migration management

### Infrastructure

- **PostgreSQL**: Primary database for relational data
- **Redis**: Session storage and caching (planned)
- **Docker**: Containerization for development and deployment

## Development Patterns

### Frontend Patterns

- **Load Functions**: Server-side data fetching for SSR
- **Optimistic Updates**: Immediate UI feedback with error handling
- **Component Composition**: Reusable components with clear interfaces
- **Type-safe API Client**: Generated types for API responses

### Backend Patterns

- **Service Layer**: Business logic separated from HTTP handlers
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: FastAPI's built-in DI system
- **Schema Validation**: Pydantic models for request/response validation

## Performance Considerations

- **Server-Side Rendering**: Fast initial page loads
- **Optimistic Updates**: Perceived performance improvements
- **Database Indexing**: Proper indexes on frequently queried columns
- **Connection Pooling**: Efficient database connection management
- **Static Asset Optimization**: Build-time optimization of CSS/JS

## Security Measures

- **Authentication**: Twitter OAuth 2.0 with PKCE
- **Authorization**: User-scoped resource access
- **Token Management**: Short-lived tokens with secure refresh
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: ORM-based queries
- **XSS Prevention**: HTTP-only cookies and content security

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Frontend"
            CDN[CDN/Static Hosting]
            SVELTE[SvelteKit App]
        end

        subgraph "Backend"
            LB[Load Balancer]
            API1[FastAPI Instance 1]
            API2[FastAPI Instance 2]
        end

        subgraph "Data"
            PG_PRIMARY[(PostgreSQL Primary)]
            PG_REPLICA[(PostgreSQL Replica)]
            REDIS_CLUSTER[(Redis Cluster)]
        end

        subgraph "Monitoring"
            LOGS[Log Aggregation]
            METRICS[Metrics Collection]
            ALERTS[Alert Manager]
        end
    end

    CDN --> SVELTE
    SVELTE --> LB
    LB --> API1
    LB --> API2

    API1 --> PG_PRIMARY
    API2 --> PG_PRIMARY
    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER

    PG_PRIMARY --> PG_REPLICA

    API1 --> LOGS
    API2 --> LOGS
    API1 --> METRICS
    API2 --> METRICS

    LOGS --> ALERTS
    METRICS --> ALERTS
```

## Future Enhancements

### Planned Features

- **Real-time Notifications**: WebSocket integration for live updates
- **Advanced Search**: Full-text search across user profiles
- **Social Features**: Following/followers, activity feeds
- **Content Moderation**: Automated content filtering
- **Analytics Dashboard**: User engagement metrics

### Technical Improvements

- **Caching Layer**: Redis integration for performance
- **Image Optimization**: CDN with automatic image resizing
- **API Rate Limiting**: Protection against abuse
- **Monitoring**: Comprehensive observability stack
- **Testing**: Increased test coverage and E2E testing

This architecture provides a solid foundation for a social profile application with room for growth and scalability as the user base expands.
