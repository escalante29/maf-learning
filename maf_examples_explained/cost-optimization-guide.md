# Near-Zero Cost Architecture for MAF Applications

This guide outlines a reference architecture for deploying MAF (Microsoft Agent Framework) applications on Azure with **near-zero cost when idle**. This is ideal for proof-of-concepts, dev/test environments, and low-traffic internal tools.

## The "Scale-to-Zero" Stack

| Component | Recommended Service | Tier / Plan | Idle Cost |
|-----------|---------------------|-------------|-----------|
| **Compute** | **Azure Functions** | **Consumption Plan** (Linux/Windows) | **$0** (First 1M requests free) |
| **Orchestration** | **Durable Functions** | **Azure Storage** Backend | **<$0.05/mo** (Storage at rest) |
| **Database** | **Cosmos DB for MongoDB** | **vCore Free Tier** | **$0** (Lifetime free, 32GB storage) |
| **Vector Search** | **Cosmos DB for MongoDB** | **vCore Free Tier** (Integrated Vector) | **$0** (Included in DB) |
| **AI Models** | **Azure OpenAI** | **Standard** (Pay-as-you-go) | **$0** (Pay per 1K tokens) |
| **Frontend** | **Azure Static Web Apps** | **Free Tier** | **$0** |
| **Monitoring** | **App Insights** | **Basic** (Ingestion-based) | **$0** (First 5GB/mo free) |

---

## 1. Compute: Azure Functions (Consumption)

Host your MAF agents as HTTP-triggered Azure Functions.

-   **Why**: The Consumption plan bills only when your functions are running. It scales to zero automatically after being idle for ~20 minutes.
-   **Cost**: The first 1 million invocations and 400,000 GB-seconds of execution time per month are free.
-   **Trade-off**: **Cold starts**. The first request after scaling to zero may take 10-30 seconds to load the Python runtime and dependencies.
-   **Mitigation**: Use **Flex Consumption** (preview) for faster scale-up and VNet integration, though it has slightly different pricing (still scale-to-zero).

## 2. Orchestration: Durable Functions

Use Durable Functions (Python SDK) for agent workflows (state management, retries, fan-out/fan-in).

-   **Why**: It allows you to run long-running workflows without paying for compute while waiting (e.g., waiting for an AI model or user input).
-   **Backend**: Use **Azure Storage** (default). `Netherite` and `MSSQL` backends are faster but require always-on resources.
-   **Cost**: You only pay for the underlying Storage rows/tables/queues. At rest (idle), this is negligible (<$0.10/month for small apps).

## 3. Database & Vector Search: Cosmos DB for MongoDB (vCore)

For agent memory (conversations) and RAG (retrieval augmented generation), use **Azure Cosmos DB for MongoDB vCore**.

-   **Why**:
    -   **Free Tier**: Azure offers a lifetime free tier for vCore-based Cosmos DB for MongoDB (1 burstable instance, 32GB storage).
    -   **Vector Integration**: It supports native **vector search**, eliminating the need for a separate (expensive) Azure AI Search instance ($~300/mo) or a Pinecone subscription.
-   **Cost**: **$0** for the free tier instance.
-   **Configuration**: Select "Free Tier" when creating the resource.

## 4. AI Models: Azure OpenAI

-   **Why**: Industry-standard models (GPT-4o).
-   **Cost**: **Pay-as-you-go** (Standard Deployment). You pay only for input/output tokens. Zero hourly cost.
-   **Warning**: Do **not** use "Provisioned Throughput Units" (PTU) as that incurs a high fixed hourly cost.

## 5. Frontend: Azure Static Web Apps

Host your ChatKit (React) frontend here.

-   **Why**: Global CDN hosting for static assets + managed serverless API proxy.
-   **Cost**: **Free Tier** includes 100 GB bandwidth/month and 2 custom domains.
-   **Integration**: Automatically integrates with GitHub Actions for CI/CD.

---

## Architecture Diagram

```mermaid
graph TD
    User([User]) -->|HTTPS| SWA[Static Web App\n(Frontend)]
    SWA -->|API| Func[Azure Functions\n(Consumption)]
    
    subgraph "Serverless Backend"
        Func -->|Orchestration| Durable[Durable Task\n(Storage Account)]
        Func -->|State & Vectors| Cosmos[Cosmos DB Mongo vCore\n(Free Tier)]
        Func -->|Inference| OpenAI[Azure OpenAI\n(Pay-per-token)]
    end
    
    style Func fill:#d6e6ff,stroke:#82b366
    style Cosmos fill:#d6e6ff,stroke:#82b366
    style OpenAI fill:#d6e6ff,stroke:#82b366
    style SWA fill:#d6e6ff,stroke:#82b366
```

## Implementation Steps

1.  **Create Resource Group**: `rg-maf-serverless-001`
2.  **Deploy Cosmos DB**: Create `Azure Cosmos DB for MongoDB (vCore)`. **Important**: Check the "Free Tier" box.
3.  **Deploy Azure OpenAI**: Create resource, deploy `gpt-4o` and `text-embedding-3-small` (Standard).
4.  **Deploy Function App**: Create Function App (Python 3.11), select **Consumption** plan.
    -   Set `AzureWebJobsStorage` to a Standard_LRS storage account.
    -   Add `COSMOS_CONNECTION_STRING`, `OPENAI_API_KEY`, etc. to Application Settings.
5.  **Deploy Frontend**: Connect your GitHub repo to Azure Static Web Apps (Free).

## Caveats

1.  **Cold Starts**: The biggest trade-off. Your first request after idle will be slow.
2.  **Free Tier Limits**: Cosmos DB Free Tier is 1 per subscription. App Insights has a data cap.
3.  **Performance**: Consumption plans have lower CPU/RAM limits than Premium/Dedicated plans. Heavy RAG processing might be slower.

## Summary

By leveraging the **Consumption Plan** for compute and the **Free Tier** for Cosmos DB (which handles both data and vectors), you can run a fully capable MAF agent application for **pennies per month** (or free) when traffic is low.
