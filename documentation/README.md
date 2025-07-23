# 📄 PromptToForm Project Documentation

> This folder contains the main documentation for the PromptToForm project, including architecture, flowcharts, and screenshots.

## 📚 Table of Contents

- [Architecture Overview](architecture.md)
- [Flowchart](flowchart.md)
- [Screenshots](screenshots.md)

---

## 🚀 Getting Started

### 1. AWS Setup

1. **Create an IAM user** in AWS.
2. **Assign permissions:**
   - Grant `AdministratorAccess` (or at least `AmazonBedrockFullAccess`).
3. **Create an access key** for the IAM user and securely store the Access Key ID and Secret Access Key.

### 2. Environment Setup

#### a) Create a `.env` file in the backend directory:

```env
AWS_ACCESS_KEY_ID=<Amazon Access Key Here>
AWS_SECRET_ACCESS_KEY=<Amazon Secret Access Key Here>
AWS_DEFAULT_REGION=us-east-1
```

#### b) Backend Setup

```sh
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### c) Reference Schemas & System Prompts

- Add the form reference schema (`All_fields.json`) to the `form_reference` folder (already present).
- Add the workflow reference schema to the `workflow_reference` folder.
- Add the appropriate `system_prompt.txt` to both `form_reference` and `workflow_reference` folders.
- The system prompt, reference JSON, and user request are passed to the LLM.

#### d) Run the Backend Server

```sh
cd backend
flask run
```

#### e) Run the Frontend Server

```sh
cd frontend
npm run dev
```

---

For more details, see the individual documentation files linked above.
