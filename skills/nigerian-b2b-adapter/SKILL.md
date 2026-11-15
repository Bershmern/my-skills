---
name: nigerian-b2b-adapter
description: >-
  Researches and reverse-engineers global B2B business models and intelligently adapts them to the Nigerian market, prioritizing viability, local economic realities, and stress-testing over basic localization.
---

# Nigerian B2B Adapter

## Overview
This skill orchestrates deep web research and analytical reasoning to reverse-engineer a target B2B business anywhere in the world and design an adapted, viable version for the Nigerian market. It explicitly avoids blindly copying foreign models, instead assessing fundamental viability in Nigeria and pivoting the model where necessary based on local realities.

## Dependencies
This skill relies on built-in agent capabilities:
- Web Search tools (`search_web`, `read_url_content`): Used to research the target company, analyze competitors, and find industry benchmarks.

## Quick Start
"Use the `nigerian-b2b-adapter` skill to analyze [Target Business Name] (Website: [URL], Industry: [Industry])."

## Workflow

When invoked, the agent MUST follow these exact steps sequentially. Do not ask the user for guidance unless missing information materially blocks the analysis. 

### 1. Research and Reverse-Engineer
Use your web search tools to research the target business using publicly available information. Identify and reconstruct its business model, including:
- Target customers and customer segments
- Core problem being solved
- Value proposition
- Products/services
- Revenue streams and pricing model
- Sales and distribution channels
- Customer acquisition strategy
- Operations and delivery model
- Key resources, partners, and cost structure
- Competitive positioning
- Geographic and market dependencies

### 2. Information Categorization (Strict Requirement)
When reporting on the original business model and your adapted estimates, explicitly label your data points using the following categories:
- **[Verified]**: directly supported by a source (e.g. public filings, pricing pages, market reports)
- **[Inferred]**: logically derived from available evidence
- **[Estimated]**: based on benchmarks, comparable companies, or assumptions
- **[Unknown]**: insufficient evidence to determine (do not ask the user for this unless it completely blocks further analysis)

**Never present an estimate or inference as a fact.**

### 3. Nigerian Market Viability Analysis
Analyze why the model works in its original market. Then, identify which assumptions may fail in Nigeria.
Account for Nigerian realities, such as:
- Purchasing power and willingness to pay
- Business density and target-market size
- Local competition and substitutes
- Infrastructure and logistics
- Internet and payment infrastructure
- Trust and customer behavior
- Regulatory and legal considerations
- Informal vs. formal business structures
- Talent and operational costs
- Import dependence and FX exposure
- Regional differences within Nigeria

Crucially, **evaluate viability first**. If the underlying model is fundamentally unviable in Nigeria, conclude what changes are necessary (e.g. redesigning the business model, changing the target customer, altering the revenue model, or reducing operational complexity) rather than merely localizing it.

### 4. Develop the Nigerian Adapted Model
Propose a comprehensive Nigerian version of the business model containing:
- Recommended target customer
- Nigerian value proposition
- Product/service structure
- Pricing strategy (in NGN)
- Revenue model
- Customer acquisition channels
- Sales process
- Operations model
- Required startup resources
- Estimated startup and operating costs
- Unit economics
- Break-even assumptions
- Key risks and mitigation strategies

### 5. Stress-Testing
Stress-test the adapted model against realistic Nigerian failure scenarios (e.g., currency devaluation, logistics failure, lack of trust/fraud, regulatory bans). Provide realistic solutions or pivots for each scenario.

### 6. Gap Analysis and Comparison
Compare the original business model with the proposed Nigerian model. Clearly explain what should be copied, modified, or rejected.

### 7. Launch Plan
End the output with a practical, actionable launch plan covering the first 30, 60, and 90 days of execution in Nigeria.

## Common Mistakes
- **Assuming Parity**: Do not assume foreign B2B pricing or customer acquisition models translate directly to Nigeria. 
- **Presenting Estimates as Facts**: Ensure all financial estimates and unverified operational details are explicitly tagged as `[Estimated]` or `[Inferred]`.
- **Blind Localization**: Do not simply change the currency to NGN. Consider if the target market is large enough in Nigeria, or if the product delivery needs to change from self-serve SaaS to a high-touch/offline service.
