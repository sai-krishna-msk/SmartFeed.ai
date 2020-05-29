



from LDAModel import LDAModel
from test_lda_data import feature_matrix

tag = 'data-science'




model = LDAModel(mode = 'train', texts = feature_matrix["data-science"]["content"]["text"], tag=tag, edition='daily', )
model.train(n_topics=100)
print(f"Training Accuracy of {tag} is {model.evaluate()}")
model.save()