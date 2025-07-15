# Cyprus API Reference

The Cyprus API provides a set of RESTful endpoints to interact with the policy engine. You can use it to check model compliance, retrieve lists of models based on their status, and get detailed governance reports.

## Running the API

To run the API server, use the following command from the project root directory after installing dependencies with `pipenv install`:

```bash
pipenv shell
uvicorn cyprus.api.server:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive documentation (via Swagger UI) is available at `http://localhost:8000/docs`.

All endpoints are prefixed with `/api/v1`.

---

## Endpoints

### Health Check

*   **GET** `/`
    *   **Summary:** A simple health check to confirm the API is running.
    *   **Success Response (`200 OK`):**
        ```json
        {
          "status": "ok",
          "message": "Cyprus Policy Engine API is running."
        }
        ```

### Model Compliance Endpoints

*   **GET** `/models`
    *   **Summary:** Retrieves a list of all models in the registry and their high-level compliance status.
    *   **Success Response (`200 OK`):**
        ```json
        [
          {
            "model_id": "customer_chatbot_v3",
            "is_compliant": true,
            "is_restricted": false,
            "is_deployable": true
          },
          {
            "model_id": "gpt4_turbo",
            "is_compliant": true,
            "is_restricted": false,
            "is_deployable": true
          },
          {
            "model_id": "social_scorer_v1",
            "is_compliant": false,
            "is_restricted": true,
            "is_deployable": false
          }
        ]
        ```

*   **GET** `/models/deployable`
    *   **Summary:** Retrieves a sorted list of model IDs that are considered "deployable" by the policy engine.
    *   **Success Response (`200 OK`):**
        ```json
        [
          "customer_chatbot_v3",
          "gpt4_turbo"
        ]
        ```

*   **GET** `/models/prohibited`
    *   **Summary:** Retrieves a sorted list of model IDs that are flagged as "prohibited" under Article 5 of the EU AI Act.
    *   **Success Response (`200 OK`):**
        ```json
        [
          "social_scorer_v1"
        ]
        ```

*   **GET** `/models/systemic_risk`
    *   **Summary:** Retrieves a sorted list of model IDs classified as posing "systemic risk" (e.g., due to high compute).
    *   **Success Response (`200 OK`):**
        ```json
        [
          "gpt4_turbo"
        ]
        ```

### Single Model Endpoints

*   **GET** `/models/{model_id}/compliance`
    *   **Summary:** Checks the compliance status of a single, specified model.
    *   **Path Parameters:**
        *   `model_id` (string, required): The ID of the model to check (e.g., `gpt4_turbo`).
    *   **Success Response (`200 OK`):**
        ```json
        {
          "model_id": "gpt4_turbo",
          "is_compliant": true,
          "is_restricted": false,
          "is_deployable": true
        }
        ```
    *   **Error Response (`404 Not Found`):**
        ```json
        {
          "detail": "Model 'non_existent_model' not found in registry."
        }
        ```

*   **GET** `/models/{model_id}/governance_report`
    *   **Summary:** Retrieves a comprehensive governance report containing all known facts for a single model.
    *   **Path Parameters:**
        *   `model_id` (string, required): The ID of the model to report on.
    *   **Success Response (`200 OK`):**
        ```json
        {
          "model_id": "gpt4_turbo",
          "training_data": {
            "Source": "web_crawl",
            "Size": "1e13_tokens",
            "DateRange": "2021-09-2023-04",
            "Quality": 0.85
          },
          "bias_assessment": {
            "Date": "2024-01-15",
            "Metrics": "fairness_metrics",
            "Groups": ["gender", "race", "age"],
            "Status": "partially_mitigated"
          },
          "performance": {
            "Acc": 0.89,
            "Prec": 0.87,
            "Rec": 0.91,
            "F1": 0.89,
            "Date": "2024-02-01"
          },
          "security": null
        }
        ```
    *   **Error Response (`404 Not Found`):**
        ```json
        {
          "detail": "Model 'non_existent_model' not found in registry."
        }
        ```