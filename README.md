# CI Pipeline for Flask Application

## Overview
This repository contains a Flask application with automated CI/CD using GitHub Actions and Docker.

## Project Structure
```
├── app.py                          # Flask application
├── test_app.py                     # Unit tests
├── Dockerfile                      # Docker image configuration
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies (includes pytest)
├── .github/workflows/ci.yaml       # GitHub Actions CI workflow
└── .gitignore                      # Git ignore rules
```

## FAQ

### 1. Why should kubectl apply not be used in CI?

While kubectl apply is effective for development, relying on it for Continuous Integration (CI) in production environments is discouraged due to several significant limitations related to automation, control, and traceability. 
Key reasons to avoid using kubectl apply in CI include:
**Lack of Audit Trail and Visibility:** Manual or scripted kubectl apply commands lack a clear, integrated audit trail. It becomes difficult to determine who changed what and when, which is essential for troubleshooting and compliance.
**Error-Prone and Lacks Robust Rollback:** While kubectl rollout undo works for Deployments, it might not work for other resource types like ConfigMaps or Secrets. A simple typo in a YAML file can disrupt an entire application, and the built-in rollback mechanisms are not comprehensive enough for all Kubernetes resources.
**Configuration Drift and State Management Issues:** kubectl apply uses a "last-applied-configuration" annotation for its three-way merge logic.
    - If changes are made to the cluster outside of the CI pipeline (e.g., via kubectl edit or another apply from a different source), the annotation can become inconsistent with the actual cluster state, leading to unexpected behavior or "configuration drift".
    - If a new container image is built but the image tag in the YAML file remains the same, kubectl apply will not see a change and thus won't deploy the new image. Using immutable tags is a better practice, but kubectl apply doesn't enforce this pattern.
**Scalability and Complexity:**  As the number of microservices and configuration files grows, managing deployments manually or with basic scripts becomes slow and error-prone.
**Inconsistent Behavior:**  Mixing kubectl create and kubectl apply on the same resource can cause unexpected merge behaviors because the initial create command doesn't add the necessary "last-applied-configuration" annotation that apply relies on.
**Limited Lifecycle Management:**  kubectl apply is a simple tool for applying a single manifest. It does not handle complex deployment strategies (like blue-green or canary deployments), dependency management, or resource cleanup in a sophisticated way. 

### 2. Why is latest a bad Docker tag?

**Using `latest` creates problems in production deployments:**

- **No version tracking**: You can't tell which exact version is running
- **Unpredictable updates**: The same tag points to different images over time
- **Breaks reproducibility**: Can't reliably rebuild the same environment
- **Deployment conflicts**: Multiple teams pulling different "latest" versions
- **Difficult rollbacks**: If something breaks, you don't know what to revert to
- **Cache issues**: Docker pulls the latest SHA even if you think you have it cached

**Best practice (used in this pipeline):**
```yaml
tags: henria/devops_1:${{ github.sha }}
```
- Uses Git commit SHA as the tag
- Immutable: Each commit gets a unique image
- Fully traceable and reproducible
- Easy to rollback by tag

### 3. What is the difference between CI and CD?

| **CI (Continuous Integration)** | **CD (Continuous Deployment)** |
|---|---|
| Automatically test code on every commit | Automatically deploy tested code to production |
| Runs unit tests, linting, builds | Triggers after successful CI |
| Catches bugs early | Delivers features to users |
| Runs on every push/PR | Should only run on main branch |
| Fails fast to prevent bad code | Ensures quality before reaching users |

**In this pipeline:**
- **CI enabled**: ✅ Tests run on every push/PR
- **CD not enabled**: Building Docker image on every commit (ready for deployment, but not auto-deploying)

**Pipeline flow:**
```
Code Push → CI (test) → Build Docker Image → Ready for CD (manual or automatic deployment)
```

### 4. How does this pipeline support GitOps?

**GitOps principle**: The Git repository is the single source of truth for the entire system.

**This pipeline supports GitOps by:**

1. **Version Control Everything**
   - Application code, tests, Dockerfile, CI config all in Git
   - Every change is tracked and auditable
   - Can rollback any change by reverting commits

2. **Immutable Docker Images**
   - Tagged by commit SHA: `henria/devops_1:${{ github.sha }}`
   - Each image is tied to a specific Git commit
   - Can trace any deployed image back to the exact code

3. **Automated CI Validation**
   - Tests run automatically on push
   - Bad code never builds into a Docker image
   - Only tested, validated code is pushed to registry

4. **Declarative Configuration**
   - Dockerfile declares how to build the image
   - requirements.txt declares dependencies
   - CI workflow declares build and test steps
   - No manual interventions needed

5. **Ready for Deployment Tools**
   - Docker image can be referenced in Kubernetes manifests
   - ArgoCD or Flux can pull these images and deploy
   - Deployment config can reference commit SHA tags
   - Changes flow: Git commit → Docker image → K8s deployment

**Example GitOps Flow:**
```
1. Developer commits code → Git
2. GitHub Actions (CI) runs tests
3. Tests pass → Docker image built with commit SHA tag
4. Image pushed to registry
5. Deployment manifest in Git references: henria/devops_1:${{ commit-sha }}
6. ArgoCD monitors manifest repo
7. ArgoCD deploys new image to Kubernetes
```

## Running Locally

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run Flask app
python app.py
```

## Docker

```bash
# Build image
docker build -t henria/devops_1:local .

# Run container
docker run -p 5000:5000 henria/devops_1:local
```

**In CI/CD (GitHub Actions):**
- Image is automatically built and tagged with commit SHA
- Pushed to Docker Hub as: `henria/devops_1:${{ github.sha }}`


## CI/CD Workflow

- Tests run on every push and pull request
- Docker image is built and pushed to Docker Hub
- Image is tagged with the Git commit SHA for full traceability
