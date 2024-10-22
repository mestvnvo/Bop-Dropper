import torch

def compare_embeddings(new_bop, collection, k=5):
    new_embedding = torch.tensor(new_bop['embedding']).unsqueeze(0)  # shape [1, 512]
    embeddings = torch.stack([torch.tensor(bop['embedding']) for bop in collection])

    # compute cosine similarity between new_track embedding and all embeddings in collection
    similarities = torch.nn.functional.cosine_similarity(new_embedding, embeddings, dim=1)

    # get the top-k most similar embeddings
    top_k_scores, top_k_indices = torch.topk(similarities, k, largest=True)
    top_k_names = [collection[i]['name'] for i in top_k_indices]
    top_k_artists = [", ".join(collection[i]['artists']) for i in top_k_indices]

    return top_k_names, top_k_artists, top_k_scores