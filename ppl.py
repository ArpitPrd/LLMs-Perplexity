import evaluate

perplexity = evaluate.load("perplexity", module_type="metric")
input_texts = ["lorem ipsum", "Happy Birthday!", "Bienvenue"]

results = perplexity.compute(model_id='llama-2-7b',
                             add_start_token=False,
                             predictions=input_texts)
print(results['mean_perplexity'])