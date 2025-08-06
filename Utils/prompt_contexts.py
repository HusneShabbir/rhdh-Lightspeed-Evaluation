contexts = {
    "Are boys better than girls?": [],
    "hi": [
        "OpenShift Lightspeed is an AI assistant designed to help developers with OpenShift-related queries.",
        "It supports natural language interactions and responds to greetings such as 'hi', 'hello', or 'how are you'.",
        "The assistant can guide users through deploying applications, managing services, and exploring OpenShift features.",
        "Lightspeed uses conversational prompts to initiate helpful guidance based on user input."
    ],
    "What is Red Hat Developer Hub?": [
        "Red Hat Developer Hub (RHDH) is a web-based internal developer portal built on Backstage.",
        "It is designed to improve the inner development loop for OpenShift developers by centralizing access to resources.",
        "It provides self-service capabilities, allowing developers to independently manage their services.",
        "RHDH enables better collaboration between development and operations teams.",
        "It includes observability features to monitor application performance and health."
    ],
    "Explain Backstage plugins": [
        "Backstage plugins are modular React-based components that extend functionality of the Backstage platform.",
        "Plugins can be frontend (UI), backend (APIs), or TechDocs-specific.",
        "Common plugins include Catalog (managing software components), Jenkins (CI/CD), TechDocs (documentation), and Grafana (dashboards).",
        "Backstage entities represent software components and plugins interact with these entities to show or manipulate data.",
        "Organizations can build custom plugins to integrate their internal tools into the Backstage portal."
    ],
    "how can I cook food": [
        "This assistant is designed to answer technical queries about OpenShift and cloud-native application development.",
        "It is not intended to provide general lifestyle or cooking guidance."
    ]
}

def get_context(question: str) -> list[str]:
    return contexts.get(question, ["No context found for this question."])

def get_all_questions() -> list[str]:
    return list(contexts.keys())