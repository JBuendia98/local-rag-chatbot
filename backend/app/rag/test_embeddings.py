from embeddings import EmbeddingModel

if __name__ == "__main__":
    texts = [
        "SGFD is an AI defence company.",
        "John Doe founded the company.",
        "The weather is sunny today."
    ]

    model = EmbeddingModel()
    vectors = model.embed(texts)

    print("Vector shape:", vectors.shape)
