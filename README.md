# Local Lobe Chat

## Introduction
This is a small project that uses docker to host a local instance of LobeChat, enabling the additional power a wrapper like LobeChat provides (role configuration, file context, etc.) around the user's existing AI models (such as Gemini or Claude, linked with API keys).

In addition to the LobeChat container, 3 other containers are created to handle data storage and auth (postgres, minio, and logto). 

## Infrastructure Setup

### CLI
The following commands are used to deploy and remove the lobe chat service:
```
./cli up
./cli down
```

### Data Persistence
The settings, documents, and conversation history for Lobe Chat are stored in the two docker volumes specified in docker-compose. If these volumes are deleted then all persistent data will be wiped.

### Foundational Setup
Before getting into Lobe Chat and setting up the AI assistants themselves, two things must be done if the docker volumes are newly created. 

First, the minio instance must be accessed at http://localhost:9001 and a bucket named `lobechat` created. Then it must be set to public using the following command:
```
docker run --rm -it --network host --entrypoint=/bin/sh minio/mc -c "
  mc alias set myminio http://127.0.0.1:9000 minioadmin miniopass;
  mc anonymous set public myminio/lobechat
"
```

Next, the logto instance must be accessed and a user created, using the following steps:

1. Access the Admin Console: Open the browser and go to http://localhost:3002 (the Logto Admin UI).
2. Initial Setup: Follow the on-screen prompts to create the Administrator account for Logto itself.
3. Create the Application: * Navigate to Applications > Create Application.
    - Select Next.js (App Router) as the framework.
    - Name it "LobeChat".
4. Configure Redirects: In the Application settings, set the Redirect URI to http://localhost:3210/api/auth/callback/logto.
5. Get Credentials: Copy the App ID and App Secret and paste them into the .env
6. Add a User: Go to the User Management section in the Logto sidebar and click Add User. This is the account used to log into LobeChat.
7. run `./cli down` and `./cli up` so that lobe-chat reads the logto app id and secret

### Accessing LobeChat
Now that everything is set up, simply access LobeChat at http://localhost:3210 and sign in using the created user credentials. From here, LobeChat can also be installed as a PWA.

## LobeChat Settings

### Model Setup
The first step to configuring the LobeChat instance is setting what models it uses.

1. Disable all models except those you have API keys for in the `AI Service Provider` section of the Settings. By default, LocalLobeChat is set up to use a OpenAI API key, a Gemini API key and a Claude API key.

2. Add the API keys through the UI, as despite them being specified in the docker compose they often don't get set properly. You must have an OpenAI key for the Knowledge Base to work, or change the `docker-compose.yml` to use a different embedding model from an AI service you do have. 

3. Choose which models to enable for the AI services (e.g. GPT-5 nano, Gemini 2.5 Flash, Gemini 2.5 Pro, Claude Sonnet 4.5)

4. Go to the `System Assistant` section of the settings and set everything to use one of your cheap models (e.g. GPT-5 nano)

### Assistant Setup
The final step is the true power of LobeChat, configuring Assistants. I'll outline the process of setting up an `AI Coordinator` Assistant below, which is the Assistant I use to create all my other assitants.

#### Set up the Knowledge Base (KB) / Reference Material:
Create a new Knowledge Base in LobeChat. Upload all documentation, guidelines, and reference materials for creating other assistants. This foundational step ensures the AI Coordinator has the facts it needs from the start. I also include my resume so the assistant has knowledge about the user, and use a naming system to optimize lookups. Here are the files I use:

- B_Prompting_OpenAI.md: Brain, Focuses on prompt strategies from a specific vendor.
- B_Prompting_Anthropic.md: Brain, Focuses on prompt strategies from a specific vendor.
- B_Prompting_Gemini.md: Brain,	Focuses on prompt strategies from a specific vendor.
- B_Reasoning_CoT.md: Brain, Focuses on core reasoning strategies (Chain of Thought).
- L_Agent_Lobe.md: LobeChat, Core LobeChat agent architecture.
- L_KB_Lobe.md: LobeChat, Focuses on LobeChat's specific RAG setup.
- E_Metrics_WandB.md: Evaluation, Defines quality metrics for improvement.
- E_TokenUsage_OpenAI.md: Evaluation, Focuses on cost-saving and efficiency.
- P_Resume_User.md: Personal, Essential context about the user.

#### Create the Group/Assistant & Set Assistant Info:
Create a group for your assistants, give your assistant a clear Name (e.g., "AI Coordinator"), a concise Description, and an appropriate Avatar. This establishes its identity.

#### Set the Role Configuration (The Brain):
This is the most crucial step. Write a detailed, specific System Prompt defining its persona, goals, and constraints.

#### Link the Knowledge Base:
Explicitly link the KB you created in step 1. 

#### Set the Model Settings:
Select a powerful, context-aware model (e.g. Claude 4.5 Sonnet) and configure parameters like Temperature and Max Tokens. Additionally, in the settings along the char prompt itself, change `Disable Online Search` to `Smart Online Search` and enable the toggle below it to use the model's search engine.

#### Install/Enable Plugins:
Install and enable and necessary tools, the two plugins below are the most important and already installed, but must be enabled.

- Artifacts
- Code Interpreter

For self-reflection and AI assistant diagnostics, there's not a plugin solution, but one possiblility is to run a langfuse docker instance and link lobe-chat to it, then provide the observed data to the AI Coordinator. I've decided not to do this for now, so that is not included in this project.

#### Set the Opening Settings:
Define the Opening Message to serve as the first-turn system prompt execution, which should clearly establish the agent's identity, core mission, and its strategic approach to managing complexity. You may also add Opening Questions.

#### Set Chat Preferences:
Review settings and optimize, such as limiting history message count to reduce context rot.