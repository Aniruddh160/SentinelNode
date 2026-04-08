from graphs.entity_extractor import EntityExtractor

text = """
UserService depends on Redis database and calls PaymentAPI.
The system is deployed on AWS EC2.
"""

extractor = EntityExtractor()
entities = extractor.extract(text, "sample_doc")

for e in entities:
    print(e)