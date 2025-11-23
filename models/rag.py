import requests


def get_context():
    # url = "http://localhost:8022/answer"
    # headers = {
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "query": "Какие требования к газоопасным работам?",
    #     "top_k": "5",
    #     "max_context_length": 2000
    # }

    # response = requests.post(url, headers=headers, json=data)
    # result = response.json()
    
    # context = result['context']
    
    # sources = []
    # for chunk in result['relevant_chunks']:
    #     chunk_sources = {
    #         # 'document_name': chunk['document_name'],
    #         'document_short_name': chunk['document_source'],
    #         'page_number': chunk['page_number']
    #     }
        
    #     sources.append(chunk_sources)
    
    context = ''
    return context
        