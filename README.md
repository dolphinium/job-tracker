# Job Tracker

Job Tracker is a full-stack web application designed to help users manage and track their job applications. It features a FastAPI backend, a Vue.js frontend with Vuetify, and uses MongoDB for data storage. A key feature is its ability to automatically scrape job details from LinkedIn URLs.

## Features

*   **User Authentication:** Secure user registration and login using JWT.
*   **Application Management:** Create, Read, Update, and Delete (CRUD) job applications.
*   **LinkedIn Integration:** Automatically fetches job details (Title, Company, Location, Description, Date Posted) from a provided LinkedIn job URL using a web crawler.
*   **Status Tracking:** Track the status of each application (Wishlist, Applied, Interview, Offer, etc.) with a history log.
*   **Notes & Details:** Add personal notes and store relevant application details.
*   **Responsive UI:** A clean user interface built with Vue.js and Vuetify 3.
*   **Dashboard:** Provides a quick overview of application statistics (Total, Active, Interview Stage) and recent activity.
*   **Containerized:** Easily run the backend and database using Docker Compose.

## Tech Stack

*   **Backend:**
    *   Python 3.11
    *   FastAPI
    *   Motor (Async MongoDB Driver)
    *   Pydantic (Data Validation)
    *   Passlib, python-jose (Authentication & Security)
    *   BeautifulSoup4, Requests (LinkedIn Crawler)
    *   Uvicorn (ASGI Server)
*   **Frontend:**
    *   Vue.js 3
    *   Vue Router 4
    *   Vuex 4 (State Management)
    *   Vuetify 3 (UI Component Library)
    *   Axios (HTTP Client)
*   **Database:** MongoDB
*   **Containerization:** Docker, Docker Compose

## Prerequisites

Before you begin, ensure you have the following installed:

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/) (Usually included with Docker Desktop)
*   [Node.js](https://nodejs.org/) (v16 or later recommended) and [npm](https://www.npmjs.com/) (usually included with Node.js) - *Required for frontend development*

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dolphinium/job-tracker.git
    cd dolphinium-job-tracker
    ```

2.  **Configure Environment Variables (Optional but Recommended):**
    The backend uses environment variables defined in `docker-compose.yml` for development. For production or more complex setups, consider creating a `.env` file in the project root:
    ```dotenv
    # .env
    MONGODB_URL=mongodb://mongodb:27017
    DATABASE_NAME=job_tracker_prod # Or keep as job_tracker
    SECRET_KEY=generate-a-strong-random-secret-key # CHANGE THIS!
    ACCESS_TOKEN_EXPIRE_MINUTES=43200 # e.g., 30 days
    ```
    *Note: The `docker-compose.yml` file currently sets these for the `api` service directly. Using a `.env` file requires adjusting `docker-compose.yml` to load it.*

3.  **Build and Run Backend Services (API & MongoDB):**
    From the project root directory :
    ```bash
    docker-compose up -d --build
    ```
    This command will:
    *   Build the Docker image for the FastAPI application (`api` service).
    *   Pull the official MongoDB image (`mongodb` service).
    *   Create and start the containers in detached mode (`-d`).
    *   Set up a shared network for the services.
    *   Create a volume (`mongodb_data`) to persist database data.

4.  **Install Frontend Dependencies:**
    Navigate to the frontend directory and install the required Node.js packages:
    ```bash
    cd job-tracker-frontend
    npm install
    ```

## Running the Application

1.  **Backend:** The backend API and database should already be running via `docker-compose up -d` (from the Getting Started steps).
    *   API Base URL: `http://localhost:8000`
    *   API Docs (Swagger UI): `http://localhost:8000/docs`
    *   Health Check: `http://localhost:8000/health`

2.  **Frontend:**
    Navigate to the frontend directory and start the Vue development server:
    ```bash
    cd job-tracker-frontend
    npm run serve
    ```
    The frontend application will be accessible at `http://localhost:8080` (or another port if 8080 is busy - check the terminal output).

## Running Tests

Tests are located in the `tests/` directory. To run the backend tests (currently limited), execute the following command from the project root directory after starting the services with `docker-compose up`:

```bash
docker-compose exec api pytest
```
*Note: Ensure `pytest` and `httpx` are listed in `requirements.txt` (which they are).*

## Project Structure

```
└── dolphinium-job-tracker/
    ├── README.md             # This file
    ├── docker-compose.yml    # Docker Compose configuration for backend services
    ├── Dockerfile            # Docker configuration for the FastAPI backend
    ├── requirements.txt      # Python dependencies for the backend
    ├── app/                  # Backend FastAPI application source code
    │   ├── __init__.py
    │   ├── config.py         # Application settings
    │   ├── main.py           # FastAPI app entry point
    │   ├── api/              # API endpoint definitions (routers)
    │   ├── models/           # Pydantic models and database setup
    │   ├── services/         # Business logic (e.g., LinkedIn crawler)
    │   └── utils/            # Utility functions (e.g., security)
    ├── job-tracker-frontend/ # Frontend Vue.js application source code
    │   ├── README.md         # Frontend specific README
    │   ├── package.json      # Node.js dependencies and scripts
    │   ├── vue.config.js     # Vue CLI configuration
    │   ├── public/           # Static assets and index.html template
    │   └── src/              # Frontend source code (components, views, store, etc.)
    └── tests/                # Backend tests
        └── test_auth.py
```

## Important Notes

*   **LinkedIn Crawler:** Web scraping is inherently fragile. LinkedIn frequently updates its website structure, which can break the crawler (`app/services/linkedin_crawler.py`). The selectors used might need adjustments over time. Using this feature should comply with LinkedIn's Terms of Service. Excessive scraping can lead to IP blocks.
*   **Security:** The default `SECRET_KEY` in `docker-compose.yml` is **not secure** for production. Always generate and use a strong, unique secret key in a production environment, preferably loaded from environment variables or a secrets management system.

