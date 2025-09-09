
Evolution of AI

Scaled due to self-supervision

Language models -> Large Language Models -> Foundational Models

Tokenization: 

Masked language model: predict missing tokens anywhere in the sequence.E.g. Bidirection Encoder representations from transformers (BERT)

Autoregressive language model: predict next token in the sequence. E.g. GPT

Generative: Generate open ended outputs

Post training: How to make the model respond appropriately to the user prompt.

LMM - Large multimodal model

Embedding model?? Backbone for LMM's

General purpose: Can do sentiment analysis and translation

Techniques to improve the performance:
1. Prompt engineering
2. Retrieval augmented generation
3. Finetune

Factors for AI engineering discipline:
1. General purpose AI capabilities
2. Increasing AI investment
3. Low barrier to entrance

How to articulate the benefit of GenAI?
1. Value capture such as cost reduction, process efficiency, growth and accelerating innovation

How enterprises are responding? More internal facing tools than external.

Intelligent Data Processing: How to inject Markov Chain?

Planning??
1. If you don't do this, competitors with AI can make you obsolete.
2. If you don't do this, you will miss opportunities to boost profits and productivity
3. You are unsure where AI will fit into the business, but you dont want to be left behind.

Role of AI

1. Critical or complementary
2. Reactive or proactive?
3. Dynamic or static

AI automation levels:
1. crawl: Mandatory human involvement
2. walk: Ai directly interacting wth internal employees
3. run: Including direct AI interactions with external users

AI competitive advantages:
1. Technology: Similar when using foundational models,
2. Data: 
3. Distribution: 

Enable feedback mechanism in the application

Metrics:
1. Quality metrics to measure the quality of the chatbot's responses
2. Latency: TTFT (Time to First Token), TPOT(time per output token), total latency.
3. Cost metrics: 
4. Others: interpretability, fairness

Massive Multitask Language Understanding (MMLU): Popular foundation model benchmark

AI Application stack:
1. Application development: AI interface, prompt engineering, context construction, evaluation
    a. Evaluation: Mitigating risks and uncovering opportunities. 


2. Model development: Inference optimization, dataset engineering, modeling & training, evaluation
    a. Model adaptation with prompt based techniques: No need for updating model weights.
    b. Finetuning: Requires updating model weights.
    c. Modeling and training: defining model architecture, training it and finetuning it.
        E.g. Quantization: process of reducing the precision of model weights, technically changes the model's weights but not considered training.
        Pre-training: Model weights randomly initialized. Consumes 98% of the compute and data resources
        Finetuning: Continuing to train a previously trained model. Typically requires fewer resources.
        Post-training: Interchangeable with fine-tuning though may be done with prompts or change of weights.


3. Infrastructure: Compute & data management, serving, monitoring


Dataset engineering:
1. Curating, generating and annotating the data needed for training and adapting AI models.
2. Annotating open ended vs. close ended queries.
3. Data manipulation: Deduplication, tokenization, context retrieval, quality control (including removal of sensitive and toxic data)

Inference optimization: Includes quantization, distillation and parallelism.










