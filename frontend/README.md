# Frontend Service (React Dashboard)

## Overview

This service provides the user interface for the OSINT platform. It's a single-page application (SPA) built using React (with Vite) and Material-UI. It interacts with the FastAPI backend to display data, visualize analytics, and manage user authentication.

## Key Features

*   User registration and login with JWT-based session management.
*   Protected routes for authenticated users.
*   Dashboard for viewing, filtering, and paginating scraped posts (`DashboardPage.jsx`).
*   Analytics page (`AnalyticsPage.jsx`) with charts for:
    *   Risk category distribution.
    *   Language distribution of posts.
    *   Top N named entities (e.g., PERSON, ORG).
    *   Time series analysis of post frequency.
*   Page for listing scraped profiles (`ScrapedProfilesPage.jsx`) with basic search and pagination.
*   Responsive design elements using Material-UI components.
*   Centralized API communication through services (`authService.js`, `postService.js`, `analyticsService.js`, `profileService.js`).
*   Global state management for authentication using React Context (`AuthContext.jsx`).

## Environment Variables

The primary environment variable for the frontend is set during the build process via Vite's environment variable system (using `.env.[mode]` files):

*   `VITE_API_BASE_URL`: The base URL for the backend API.
    *   In development (`frontend/.env.development`): Typically `http://localhost:8000` (if the backend runs directly on port 8000 and is accessible from the frontend dev server).
    *   In production (`frontend/.env.production`, used by Docker build): Typically a relative path like `/api/v1`. This path is then proxied by the Nginx server (configured in `frontend/nginx.default.conf` and running in the frontend's Docker container) to the backend service.

## Running Standalone (for Development)

1.  **Navigate to the `frontend` directory**:
    ```bash
    cd frontend
    ```
2.  **Ensure Backend is Running**: The backend service must be running and accessible at the URL specified in `frontend/.env.development` (the value of `VITE_API_BASE_URL`).

3.  **Install Dependencies**:
    If you haven't already, or if dependencies have changed:
    ```bash
    npm install --legacy-peer-deps
    ```
    *(The `--legacy-peer-deps` flag is used to bypass potential peer dependency conflicts, common in complex React projects. Remove if not needed or if it causes issues with your specific Node/npm version).*

4.  **Run the Development Server**:
    ```bash
    npm run dev
    ```
    This command starts the Vite development server. It will typically open the application in your default web browser (e.g., at `http://localhost:5173` or another port specified by Vite if 5173 is in use). The server supports Hot Module Replacement (HMR) for a fast development experience.

## Building for Production

*   To create an optimized static build of the application (assets will be placed in the `frontend/dist/` directory):
    ```bash
    npm run build
    ```
    This command uses `frontend/.env.production` to set environment variables like `VITE_API_BASE_URL` for the production build. The resulting `dist/` folder can then be served by any static file server (like Nginx, which is used in the Docker setup).

## Project Structure (`frontend/src/`)

*   `App.jsx`: Main application component with routing setup.
*   `main.jsx`: Entry point of the React application, renders the root component.
*   `components/`: Contains reusable UI components.
    *   `charts/`: Specific components for displaying Recharts graphs.
    *   `Navbar.jsx`: Site navigation bar.
    *   `ProtectedRoute.jsx`: Handles route protection for authenticated users.
    *   `PostTable.jsx`, `ProfileTable.jsx`, `RiskBadge.jsx`, `SentimentBadge.jsx`.
*   `pages/`: Top-level view components representing different pages of the application.
    *   `LoginPage.jsx`, `DashboardPage.jsx`, `AnalyticsPage.jsx`, `ScrapedProfilesPage.jsx`.
*   `services/`: Modules for interacting with the backend API.
    *   `api.js`: Configured Axios instance.
    *   `authService.js`, `postService.js`, `analyticsService.js`, `profileService.js`.
*   `contexts/`: React Context providers for global state management.
    *   `AuthContext.jsx`: Manages authentication state and user data.
*   `hooks/`: (Currently empty) For custom React hooks.
*   `assets/`: Static assets like images, SVGs.
*   `index.css`, `App.css`: Global and component-level styles.
