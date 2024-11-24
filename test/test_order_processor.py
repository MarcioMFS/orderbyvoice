from services.order_processor import process_order

def run_tests():
    inventory = [
        {
            "id": "001",
            "nome": "Big Mac",
            "categoria": "Hambúrguer",
            "descricao": "Sanduíche com dois hambúrgueres, alface, queijo, molho especial, cebola e picles.",
            "ingredientes": ["Hambúrguer", "Alface", "Queijo", "Molho especial", "Cebola", "Picles"]
        },
        {
            "id": "002",
            "nome": "Coca-Cola 350ml",
            "categoria": "Refrigerante",
            "descricao": "Refrigerante Coca-Cola em lata de 350ml.",
            "ingredientes": []
        },
        {
            "id": "003",
            "nome": "Batata Frita Média",
            "categoria": "Acompanhamento",
            "descricao": "Porção média de batatas fritas crocantes.",
            "ingredientes": ["Sal"]
        }
    ]

    tests = [
        {
            "description": "Cenário 1: Remoção com 'sem'",
            "text": "Quero um Big Mac sem cebola.",
            "expected": [
                {
                    "produto": "Big Mac",
                    "quantidade": 1,
                    "ingredientes_removidos": ["Cebola"]
                }
            ]
        },
        {
            "description": "Cenário 2: Remoção com 'não quero'",
            "text": "Gostaria de um Big Mac, mas não quero picles.",
            "expected": [
                {
                    "produto": "Big Mac",
                    "quantidade": 1,
                    "ingredientes_removidos": ["Picles"]
                }
            ]
        },
        {
            "description": "Cenário 3: Remoção com 'pode tirar'",
            "text": "Quero dois Big Mac e pode tirar a cebola.",
            "expected": [
                {
                    "produto": "Big Mac",
                    "quantidade": 2,
                    "ingredientes_removidos": ["Cebola"]
                }
            ]
        },
        {
            "description": "Cenário 4: Sem remoção de ingredientes",
            "text": "Quero três Big Mac.",
            "expected": [
                {
                    "produto": "Big Mac",
                    "quantidade": 3,
                    "ingredientes_removidos": []
                }
            ]
        },
        {
            "description": "Cenário 5: Múltiplos produtos com remoção",
            "text": "Quero um Big Mac sem cebola e uma Coca-Cola 350ml.",
            "expected": [
                {
                    "produto": "Big Mac",
                    "quantidade": 1,
                    "ingredientes_removidos": ["Cebola"]
                },
                {
                    "produto": "Coca-Cola 350ml",
                    "quantidade": 1,
                    "ingredientes_removidos": []
                }
            ]
        },
        {
            "description": "Cenário 6: Remoção de ingrediente em batata frita",
            "text": "Quero uma Batata Frita Média e tire o sal.",
            "expected": [
                {
                    "produto": "Batata Frita Média",
                    "quantidade": 1,
                    "ingredientes_removidos": ["Sal"]
                }
            ]
        }
    ]

    for test in tests:
        result = process_order(test["text"], inventory)
        if result == test["expected"]:
            print(f"✅ {test['description']} - Passed")
        else:
            print(f"❌ {test['description']} - Failed")
            print(f"   Expected: {test['expected']}")
            print(f"   Got: {result}")

if __name__ == "__main__":
    run_tests()
