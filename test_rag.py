from rag import (
    build_knowledge_base,
    search_knowledge,
    generate_answer
)


print("Building knowledge base...")

count = build_knowledge_base()

print(f"Loaded {count} knowledge documents.")


question = "I cannot send of receive my work emails"


print("\nSearching knowledge base...")

results = search_knowledge(question)


print("\nGenerating AI answer...")


answer = generate_answer(
    question,
    results
)


print("\n" + "=" * 60)

print("My office printer is not working")

print("=" * 60)

print(answer)