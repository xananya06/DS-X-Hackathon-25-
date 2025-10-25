CONSCIOUSCART - Where DS meets effective consumerism

ConsciousCart is an agentic AI system used for cruelty-free beauty verification. As millions of animals suffer in comsmetics testing annually, our system aims to ensure consumers do not face significant barriers when it comes to ethical shopping while getting access to high-quality cosmetics and skincare products. 

Due to corporate greenwashing many brands claim they are cruelty free while the parent companies still test on animals, due to increased information fragmentation and increased 20 minutes + test time to test each product manually, only priveleged customers afford organic, cruelty-free, high quality cosmetics as opposed to the general audience. 

Our solution, ConsicousCart uses a single intelligent agent which autonomously decides how to verify the products by doing the following:
1) Checks local databases first focusing on efficiency
2) Searches web when needed ensuring accuracy and caching
3) Verifies parent company reationships
4) Provides ethical alternatives with prices
5) Learns over time, includes memory buffer, updates the dataset regularly with new products

For a sample brand in the dataset, agent makes 1-2 tool calls whereas for unknown brand agents may make 5+ tool calls to verify thoroughly. 

TECHNICAL STACK 
AGENT USED - Claude
DATABASE - SQLite for persistent storage
SEARCH - Web search capability (mock used for demo, production ready architecture)
UI - Streamliy (displays agent reasoning)
LANGUAGE Python 3.10 
DATA SCIENCE COMPONENT - Autonomous tool selection, Multi-source informations synthesis, knowledge graph reasoning, recommendation system, intelligent caching

FUTURE SCOPE - Integrating MCP Brave Search for live web queries and to combat limited data collection, MCP fetch for direct certification, Expands database to 100+ brands and adds user profiling across sessions.

HOW IS IT DIFFERENT FROM EXISTING APPLICATIONS: 
1) Conversational (No need of bar code reading)
2) Real-time verification, does not use static dataset
3) Provides alternatives, not just yes/no answers
4) Explains reasoning with sources


Made with love in DS_X Hackathon 2025



