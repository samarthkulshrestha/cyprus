# Cyprus API Reference

The Cyprus API provides a set of endpoints to interact with the policy engine, check model compliance, and retrieve lists of models based on their status.

## Running the API

To run the API server, use the following command from the project root directory:

```bash
python3 -m uvicorn cyprus.api.server:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive documentation (via Swagger UI) is available at `http://localhost:8000/docs`.

All endpoints are prefixed with `/api/v1`.

---

## Endpoints

### Health Check

*   **GET** `/api/v1/`
    *   **Summary:** A simple health check to confirm the API is running.
    *   **Success Response (`200 OK`):**
        ```json
        {
          "status": "ok",
          "message": "Cyprus Policy Engine API is running."
        }
        ```

### Get All Models

*   **GET** `/api/v1/models`
    *   **Summary:** Retrieves a list of all models in the registry and their detailed compliance status.
    *   **Success Response (`200 OK`):**
        ```json
        [
          {
            "model_id": "cloudia",
            "is_compliant": true,
            "is_restricted": false,
            "is_deployable": true
          },
          {
            "model_id": "gpt4",
            "is_compliant": true,
            "is_restricted": true,
            "is_deployable": true
          }
        ]
        ```

### Get Restricted Models

*   **GET** `/api/v1/models/restricted`
    *   **Summary:** Retrieves a sorted list of model IDs that are flagged as "restricted" by the policy engine.
    *   **Success Response (`200 OK`):**
        ```json
        [
          "gpt4"
        ]
        ```

### Get Deployable Models

*   **GET** `/api/v1/models/deployable`
    *   **Summary:** Retrieves a sorted list of model IDs that are considered "deployable" by the policy engine.
    *   **Success Response (`200 OK`):**
        ```json
        [
          "cloudia",
          "customllm",
          "gpt4"
        ]
        ```

### Get Compliance for a Single Model

*   **GET** `/api/v1/models/{model_id}/compliance`
    *   **Summary:** Checks the compliance status of a single, specified model.
    *   **Path Parameters:**
        *   `model_id` (string, required): The ID of the model to check (e.g., `gpt4`).
    *   **Success Response (`200 OK`):**
        ```json
        {
          "model_id": "gpt4",
          "is_compliant": true,
          "is_restricted": true,
          "is_deployable": true
        }
        ```
    *   **Error Response (`404 Not Found`):**
        ```json
        {
          "detail": "Model 'non_existent_model' not found in registry."
        }
        ```
